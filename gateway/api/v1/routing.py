from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from gateway.dependencies import get_current_key, get_redis
from gateway.db.session import get_session
from gateway.models.routing_rule import RoutingRule
from gateway.models.virtual_key import VirtualKey
from gateway.routing.router import ModelRouter
from gateway.schemas import ChatCompletionRequest, RoutingRuleCreate

router = APIRouter(prefix="/api/v1/routing", tags=["routing"])


@router.post("/rules")
async def create_rule(payload: RoutingRuleCreate, key: VirtualKey = Depends(get_current_key), session: AsyncSession = Depends(get_session)):
    rule = RoutingRule(virtual_key_id=key.id, **payload.model_dump())
    session.add(rule)
    await session.commit()
    await session.refresh(rule)
    return {"id": str(rule.id), "name": rule.name}


@router.get("/rules")
async def list_rules(key: VirtualKey = Depends(get_current_key), session: AsyncSession = Depends(get_session)):
    rules = (await session.execute(select(RoutingRule).where(RoutingRule.virtual_key_id == key.id).order_by(RoutingRule.priority.desc()))).scalars().all()
    return {"data": [{"id": str(r.id), "name": r.name, "priority": r.priority, "conditions": r.conditions, "target_model": r.target_model, "is_active": r.is_active} for r in rules]}


@router.put("/rules/{rule_id}")
async def update_rule(rule_id: str, payload: RoutingRuleCreate, key: VirtualKey = Depends(get_current_key), session: AsyncSession = Depends(get_session)):
    rule = await session.get(RoutingRule, rule_id)
    if not rule or rule.virtual_key_id != key.id:
        raise HTTPException(404, "Rule not found")
    for field, value in payload.model_dump().items():
        setattr(rule, field, value)
    await session.commit()
    return {"status": "updated"}


@router.delete("/rules/{rule_id}")
async def delete_rule(rule_id: str, key: VirtualKey = Depends(get_current_key), session: AsyncSession = Depends(get_session)):
    rule = await session.get(RoutingRule, rule_id)
    if not rule or rule.virtual_key_id != key.id:
        raise HTTPException(404, "Rule not found")
    await session.delete(rule)
    await session.commit()
    return {"status": "deleted"}


@router.post("/test")
async def test_route(request: ChatCompletionRequest, key: VirtualKey = Depends(get_current_key), session: AsyncSession = Depends(get_session), redis=Depends(get_redis)):
    decision = await ModelRouter(redis).route(request, key, session)
    return {
        "requested_model": decision.requested_model,
        "routed_model": decision.model,
        "provider": decision.provider,
        "strategy": decision.strategy,
        "task_type": decision.task_type,
        "reason": decision.reason,
        "fallback_chain": decision.fallback_chain,
    }

