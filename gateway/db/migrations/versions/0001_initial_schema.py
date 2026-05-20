"""Initial ModelRouterX schema."""

from alembic import op

revision = "0001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE EXTENSION IF NOT EXISTS vector;
        CREATE EXTENSION IF NOT EXISTS pgcrypto;

        CREATE TABLE IF NOT EXISTS virtual_keys (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            key_hash TEXT UNIQUE NOT NULL,
            key_prefix TEXT NOT NULL,
            name TEXT NOT NULL,
            owner_id TEXT NOT NULL,
            budget_limit_usd NUMERIC(10,4),
            budget_used_usd NUMERIC(10,4) DEFAULT 0,
            rpm_limit INT,
            tpm_limit INT,
            routing_strategy TEXT DEFAULT 'balanced',
            allowed_models TEXT[],
            metadata JSONB DEFAULT '{}',
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMPTZ DEFAULT NOW(),
            expires_at TIMESTAMPTZ
        );

        CREATE TABLE IF NOT EXISTS request_logs (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            virtual_key_id UUID REFERENCES virtual_keys(id),
            request_id TEXT UNIQUE NOT NULL,
            requested_model TEXT NOT NULL,
            routed_model TEXT NOT NULL,
            routed_provider TEXT NOT NULL,
            routing_strategy TEXT NOT NULL,
            task_type TEXT,
            routing_reason TEXT,
            cache_status TEXT NOT NULL DEFAULT 'miss',
            cache_similarity NUMERIC(4,3),
            prompt_tokens INT NOT NULL DEFAULT 0,
            completion_tokens INT NOT NULL DEFAULT 0,
            total_tokens INT NOT NULL DEFAULT 0,
            prompt_cost_usd NUMERIC(10,6) DEFAULT 0,
            completion_cost_usd NUMERIC(10,6) DEFAULT 0,
            total_cost_usd NUMERIC(10,6) DEFAULT 0,
            ttfb_ms INT,
            total_latency_ms INT NOT NULL,
            provider_latency_ms INT,
            status_code INT NOT NULL,
            error_type TEXT,
            fallback_used BOOLEAN DEFAULT FALSE,
            fallback_chain TEXT[],
            request_body JSONB,
            response_body JSONB,
            created_at TIMESTAMPTZ DEFAULT NOW()
        );

        CREATE TABLE IF NOT EXISTS provider_health (
            id BIGSERIAL PRIMARY KEY,
            provider TEXT NOT NULL,
            model TEXT NOT NULL,
            is_healthy BOOLEAN NOT NULL,
            p50_latency_ms INT,
            p95_latency_ms INT,
            error_rate_pct NUMERIC(5,2),
            circuit_state TEXT DEFAULT 'closed',
            sampled_at TIMESTAMPTZ DEFAULT NOW()
        );

        CREATE TABLE IF NOT EXISTS cost_rollups (
            id BIGSERIAL PRIMARY KEY,
            virtual_key_id UUID REFERENCES virtual_keys(id),
            period_start TIMESTAMPTZ NOT NULL,
            period_type TEXT NOT NULL DEFAULT 'hour',
            provider TEXT,
            model TEXT,
            request_count INT DEFAULT 0,
            total_tokens BIGINT DEFAULT 0,
            total_cost_usd NUMERIC(10,4) DEFAULT 0,
            cache_hits INT DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS semantic_cache (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            tenant_id TEXT NOT NULL,
            prompt_hash TEXT NOT NULL,
            prompt_embedding vector(1536),
            model TEXT NOT NULL,
            response_body JSONB NOT NULL,
            prompt_tokens INT,
            completion_tokens INT,
            hit_count INT DEFAULT 0,
            created_at TIMESTAMPTZ DEFAULT NOW(),
            last_hit_at TIMESTAMPTZ,
            expires_at TIMESTAMPTZ
        );

        CREATE TABLE IF NOT EXISTS routing_rules (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            virtual_key_id UUID REFERENCES virtual_keys(id),
            name TEXT NOT NULL,
            priority INT NOT NULL DEFAULT 0,
            conditions JSONB NOT NULL,
            target_model TEXT NOT NULL,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMPTZ DEFAULT NOW()
        );

        CREATE INDEX IF NOT EXISTS idx_request_logs_key_id ON request_logs(virtual_key_id);
        CREATE INDEX IF NOT EXISTS idx_request_logs_created_at ON request_logs(created_at DESC);
        CREATE INDEX IF NOT EXISTS idx_request_logs_provider ON request_logs(routed_provider);
        CREATE INDEX IF NOT EXISTS idx_request_logs_task_type ON request_logs(task_type);
        CREATE INDEX IF NOT EXISTS idx_provider_health_latest ON provider_health(provider, model, sampled_at DESC);
        CREATE INDEX IF NOT EXISTS idx_semantic_cache_tenant_model ON semantic_cache(tenant_id, model);
        CREATE INDEX IF NOT EXISTS idx_semantic_cache_embedding ON semantic_cache
            USING ivfflat (prompt_embedding vector_cosine_ops)
            WITH (lists = 100);
        """
    )


def downgrade() -> None:
    op.execute(
        """
        DROP TABLE IF EXISTS routing_rules;
        DROP TABLE IF EXISTS semantic_cache;
        DROP TABLE IF EXISTS cost_rollups;
        DROP TABLE IF EXISTS provider_health;
        DROP TABLE IF EXISTS request_logs;
        DROP TABLE IF EXISTS virtual_keys;
        """
    )

