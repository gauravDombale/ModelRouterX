"use client";

import { useGateway } from "@/lib/hooks/useGateway";
import { KpiCard } from "@/components/ui/KpiCard";
import { CostOverTime } from "@/components/charts/CostOverTime";
import { ModelDistribution } from "@/components/charts/ModelDistribution";
import { RefreshCw } from "lucide-react";

type CostStats = {
  total_cost_usd: string;
  by_model: {
    model: string;
    requests: number;
    cost_usd: string;
  }[];
};

type CacheStats = {
  hit_rate: number;
  hits: number;
  total: number;
};

type ProviderRow = {
  provider: string;
  model: string;
  is_healthy: boolean;
  circuit_state: string;
};

type ProviderStats = {
  providers: ProviderRow[];
};

type TrendPoint = {
  time: string;
  cost: number;
  rate: number;
  requests: number;
};

type TrendStats = {
  trend: TrendPoint[];
};

export function OverviewPanel() {
  const { data: costData, mutate: mutateCost } = useGateway<CostStats>("/api/v1/analytics/cost", {
    total_cost_usd: "0.00",
    by_model: []
  });

  const { data: cacheData, mutate: mutateCache } = useGateway<CacheStats>("/api/v1/analytics/cache", {
    hit_rate: 0,
    hits: 0,
    total: 0
  });

  const { data: healthData, mutate: mutateHealth } = useGateway<ProviderStats>("/api/v1/providers/health", {
    providers: []
  });

  const { data: trendData, mutate: mutateTrend } = useGateway<TrendStats>("/api/v1/analytics/trend", {
    trend: []
  });

  const handleRefresh = async () => {
    await Promise.all([mutateCost(), mutateCache(), mutateHealth(), mutateTrend()]);
  };

  const totalCost = parseFloat(costData?.total_cost_usd ?? "0").toFixed(2);
  const cacheHitRate = Math.round((cacheData?.hit_rate ?? 0) * 100);
  
  const providers = healthData?.providers ?? [];
  const totalProviders = providers.length;
  const healthyProviders = providers.filter((p) => p.is_healthy).length;

  return (
    <>
      <div className="toolbar" style={{ marginBottom: 16 }}>
        <button className="button" onClick={handleRefresh}>
          <RefreshCw size={16} />
          Refresh
        </button>
      </div>

      <section className="grid cols-4">
        <KpiCard
          label="Cost today"
          value={`$${totalCost}`}
          detail="Total cost of routed requests"
        />
        <KpiCard
          label="Request volume"
          value={`${cacheData?.total ?? 0}`}
          detail="Total requests logged"
        />
        <KpiCard
          label="Cache hit rate"
          value={`${cacheHitRate}%`}
          detail={`${cacheData?.hits ?? 0} hits cached`}
        />
        <KpiCard
          label="Provider health"
          value={`${healthyProviders} / ${totalProviders}`}
          detail={
            totalProviders > 0 && healthyProviders === totalProviders
              ? "All circuits closed (healthy)"
              : `${totalProviders - healthyProviders} provider models degraded`
          }
        />
      </section>

      <section className="grid cols-2" style={{ marginTop: 16 }}>
        <div className="card">
          <h2>Cost Over Time</h2>
          <CostOverTime data={trendData?.trend ?? []} />
        </div>
        <div className="card">
          <h2>Top Models</h2>
          <ModelDistribution data={costData?.by_model ?? []} />
        </div>
      </section>
    </>
  );
}
