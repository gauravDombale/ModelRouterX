from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


async def rollup_hourly_costs(session: AsyncSession) -> None:
    # Delete existing entries in the range first to avoid duplication
    await session.execute(
        text(
            """
            DELETE FROM cost_rollups
            WHERE period_start >= date_trunc('hour', now() - interval '2 hours')
            """
        )
    )
    # Insert new aggregated values
    await session.execute(
        text(
            """
            INSERT INTO cost_rollups (virtual_key_id, period_start, provider, model, request_count, total_tokens, total_cost_usd, cache_hits)
            SELECT
                virtual_key_id,
                date_trunc('hour', created_at),
                routed_provider,
                routed_model,
                count(*),
                coalesce(sum(total_tokens), 0),
                coalesce(sum(total_cost_usd), 0),
                count(*) FILTER (WHERE cache_status IN ('hit_exact', 'hit_semantic'))
            FROM request_logs
            WHERE created_at >= date_trunc('hour', now() - interval '2 hours')
            GROUP BY 1, 2, 3, 4
            """
        )
    )
    await session.commit()

