"use client";

import { useGateway } from "@/lib/hooks/useGateway";
import { CacheHitRate } from "@/components/charts/CacheHitRate";
import { CostOverTime } from "@/components/charts/CostOverTime";
import { LatencyHeatmap } from "@/components/charts/LatencyHeatmap";
import { ModelDistribution } from "@/components/charts/ModelDistribution";
import { RefreshCw } from "lucide-react";

type TrendPoint = {
  time: string;
  cost: number;
  rate: number;
  requests: number;
};

type TrendStats = {
  trend: TrendPoint[];
};

type CostStats = {
  total_cost_usd: string;
  by_model: {
    model: string;
    requests: number;
    cost_usd: string;
  }[];
};

export default function AnalyticsPage() {
  const { data: trendData, mutate: mutateTrend } = useGateway<TrendStats>("/api/v1/analytics/trend", { trend: [] });
  const { data: costData, mutate: mutateCost } = useGateway<CostStats>("/api/v1/analytics/cost", { total_cost_usd: "0.00", by_model: [] });

  const handleRefresh = async () => {
    await Promise.all([mutateTrend(), mutateCost()]);
  };

  return (
    <>
      <header className="page-header">
        <div>
          <h1 className="page-title">Analytics</h1>
          <p className="muted">Cost, model distribution, latency percentiles, and cache savings.</p>
        </div>
      </header>
      <div className="toolbar" style={{ marginBottom: 16 }}>
        <button className="button" onClick={handleRefresh}>
          <RefreshCw size={16} />
          Refresh
        </button>
      </div>
      <section className="grid cols-2">
        <div className="card">
          <h2>Cost Over Time</h2>
          <CostOverTime data={trendData?.trend ?? []} />
        </div>
        <div className="card">
          <h2>Cache Performance</h2>
          <CacheHitRate data={trendData?.trend ?? []} />
        </div>
        <div className="card">
          <h2>Latency Percentiles</h2>
          <LatencyHeatmap />
        </div>
        <div className="card">
          <h2>Model Distribution</h2>
          <div style={{ marginTop: 16 }}>
            <ModelDistribution data={costData?.by_model ?? []} />
          </div>
        </div>
      </section>
    </>
  );
}


