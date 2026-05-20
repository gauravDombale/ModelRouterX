from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from gateway.db.session import get_session
from gateway.models.virtual_key import VirtualKey
from gateway.schemas import KeyCreate
from gateway.utils.security import generate_api_key, hash_api_key, key_prefix

router = APIRouter(prefix="/api/v1/keys", tags=["keys"])


@router.post("")
async def create_key(payload: KeyCreate, session: AsyncSession = Depends(get_session)):
    api_key = generate_api_key()
    key = VirtualKey(
        key_hash=hash_api_key(api_key),
        key_prefix=key_prefix(api_key),
        name=payload.name,
        owner_id=payload.owner_id,
        budget_limit_usd=payload.budget_limit_usd,
        rpm_limit=payload.rpm_limit,
        tpm_limit=payload.tpm_limit,
        routing_strategy=payload.routing_strategy,
        allowed_models=payload.allowed_models,
        key_metadata=payload.metadata,
    )
    session.add(key)
    await session.commit()
    await session.refresh(key)
    return {"id": str(key.id), "key": api_key, "key_prefix": key.key_prefix, "name": key.name}


@router.get("")
async def list_keys(session: AsyncSession = Depends(get_session)):
    keys = (await session.execute(select(VirtualKey).order_by(VirtualKey.created_at.desc()))).scalars().all()
    return {
        "data": [
            {
                "id": str(k.id),
                "key_prefix": k.key_prefix,
                "name": k.name,
                "owner_id": k.owner_id,
                "budget_used_usd": str(k.budget_used_usd),
                "budget_limit_usd": str(k.budget_limit_usd) if k.budget_limit_usd is not None else None,
                "rpm_limit": k.rpm_limit,
                "tpm_limit": k.tpm_limit,
                "routing_strategy": k.routing_strategy,
                "is_active": k.is_active,
            }
            for k in keys
        ]
    }


@router.delete("/{key_id}")
async def revoke_key(key_id: str, session: AsyncSession = Depends(get_session)):
    key = await session.get(VirtualKey, key_id)
    if not key:
        raise HTTPException(404, "Key not found")
    key.is_active = False
    await session.commit()
    return {"status": "revoked"}

