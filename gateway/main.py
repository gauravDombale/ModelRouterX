from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from redis.asyncio import Redis
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from gateway.api.v1.analytics import router as analytics_router
from gateway.api.v1.chat import router as chat_router
from gateway.api.v1.health import router as health_router
from gateway.api.v1.keys import router as keys_router
from gateway.api.v1.models import router as models_router
from gateway.api.v1.routing import router as routing_router
from gateway.config import get_settings
from gateway.db.session import AsyncSessionLocal
from gateway.jobs.health_checker import write_health_snapshot
from gateway.jobs.cost_rollup import rollup_hourly_costs
from gateway.jobs.cache_eviction import evict_expired_cache


async def run_health_checker():
    async with AsyncSessionLocal() as session:
        await write_health_snapshot(session)


async def run_cost_rollup():
    async with AsyncSessionLocal() as session:
        await rollup_hourly_costs(session)


async def run_cache_eviction():
    async with AsyncSessionLocal() as session:
        await evict_expired_cache(session)


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    app.state.redis = Redis.from_url(settings.redis_url, decode_responses=False)

    scheduler = AsyncIOScheduler()
    scheduler.add_job(run_health_checker, "interval", seconds=60, id="health_checker")
    scheduler.add_job(run_cost_rollup, "cron", minute=0, id="cost_rollup")
    scheduler.add_job(run_cache_eviction, "interval", hours=24, id="cache_eviction")
    scheduler.start()

    try:
        await run_health_checker()
    except Exception as e:
        print(f"Failed to run initial startup health check: {e}")

    yield

    scheduler.shutdown()
    await app.state.redis.aclose()


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=settings.app_name, version="0.1.0", lifespan=lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(health_router)
    app.include_router(chat_router)
    app.include_router(models_router)
    app.include_router(keys_router)
    app.include_router(analytics_router)
    app.include_router(routing_router)

    @app.get("/")
    async def root():
        return {
            "name": settings.app_name,
            "status": "ok",
            "dashboard_url": "http://localhost:3000",
            "health_url": "/health",
            "models_url": "/v1/models",
            "docs_url": "/docs",
        }

    return app


app = create_app()
