from fastapi import APIRouter, Depends, Query
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from gateway.db.session import get_session
from gateway.models.request_log import RequestLog

router = APIRouter(prefix="/api/v1/analytics", tags=["analytics"])


@router.get("/requests")
async def requests(limit: int = Query(50, le=500), session: AsyncSession = Depends(get_session)):
    rows = (await session.execute(select(RequestLog).order_by(desc(RequestLog.created_at)).limit(limit))).scalars().all()
    return {"data": [
        {
            "id": str(r.id),
            "request_id": r.request_id,
            "created_at": r.created_at.isoformat(),
            "model": r.routed_model,
            "provider": r.routed_provider,
            "task_type": r.task_type,
            "latency_ms": r.total_latency_ms,
            "cost_usd": str(r.total_cost_usd),
            "cache_status": r.cache_status,
            "status_code": r.status_code,
        }
        for r in rows
    ]}


@router.get("/cost")
async def cost(session: AsyncSession = Depends(get_session)):
    total = (await session.execute(select(func.coalesce(func.sum(RequestLog.total_cost_usd), 0)))).scalar()
    by_model = (
        await session.execute(
            select(RequestLog.routed_model, func.count(), func.coalesce(func.sum(RequestLog.total_cost_usd), 0))
            .group_by(RequestLog.routed_model)
            .order_by(desc(func.count()))
        )
    ).all()
    return {"total_cost_usd": str(total), "by_model": [{"model": m, "requests": c, "cost_usd": str(cost)} for m, c, cost in by_model]}


@router.get("/latency")
async def latency(session: AsyncSession = Depends(get_session)):
    res = (await session.execute(
        select(
            func.coalesce(func.avg(RequestLog.total_latency_ms), 0).label("avg"),
            func.coalesce(func.percentile_cont(0.5).within_group(RequestLog.total_latency_ms), 0).label("p50"),
            func.coalesce(func.percentile_cont(0.95).within_group(RequestLog.total_latency_ms), 0).label("p95")
        )
    )).one_or_none()
    
    avg_val = res.avg if res else 0
    p50_val = res.p50 if res else 0
    p95_val = res.p95 if res else 0
    return {"avg_latency_ms": int(avg_val), "p50_ms": int(p50_val), "p95_ms": int(p95_val)}


@router.get("/cache")
async def cache(session: AsyncSession = Depends(get_session)):
    total = (await session.execute(select(func.count()).select_from(RequestLog))).scalar() or 0
    hits = (
        await session.execute(select(func.count()).select_from(RequestLog).where(RequestLog.cache_status.in_(["hit_exact", "hit_semantic"])))
    ).scalar() or 0
    return {"hit_rate": hits / total if total else 0, "hits": hits, "total": total}


@router.get("/trend")
async def trend(session: AsyncSession = Depends(get_session)):
    from datetime import datetime, timedelta
    from sqlalchemy import text
    
    cutoff = datetime.utcnow() - timedelta(hours=24)
    result = await session.execute(
        select(
            func.date_trunc('hour', RequestLog.created_at).label('hour'),
            func.coalesce(func.sum(RequestLog.total_cost_usd), 0).label('cost'),
            func.count(RequestLog.id).label('total'),
            func.count(RequestLog.id).filter(RequestLog.cache_status.in_(["hit_exact", "hit_semantic"])).label('hits')
        )
        .where(RequestLog.created_at >= cutoff)
        .group_by(text('1'))
        .order_by(text('1'))
    )
    rows = result.all()
    
    trend_data = []
    for hour, cost, total, hits in rows:
        time_str = hour.strftime("%H:%M") if hour else ""
        rate = hits / total if total > 0 else 0
        trend_data.append({
            "time": time_str,
            "cost": float(cost),
            "rate": float(rate),
            "requests": total
        })
    
    if not trend_data:
        # Provide default dynamic/static seed so charts are populated initially
        trend_data = [
            {"time": "00:00", "cost": 0.0, "rate": 0.0, "requests": 0}
        ]
        
    return {"trend": trend_data}

