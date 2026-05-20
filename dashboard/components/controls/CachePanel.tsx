"use client";

import { RefreshCw } from "lucide-react";
import { CacheHitRate } from "@/components/charts/CacheHitRate";
import { KpiCard } from "@/components/ui/KpiCard";
import { useGateway } from "@/lib/hooks/useGateway";

type CacheStats = {
  hit_rate: number;
  hits: number;
  total: number;
};

export function CachePanel() {
  const { data, mutate } = useGateway<CacheStats>("/api/v1/analytics/cache", { hit_rate: 0, hits: 0, total: 0 });
  const hitRate = Math.round((data?.hit_rate ?? 0) * 100);

  return (
    <>
      <div className="toolbar">
        <button className="button" onClick={() => void mutate()}>
          <RefreshCw size={16} />
          Refresh
        </button>
      </div>
      <section className="grid cols-4">
        <KpiCard label="Hit rate" value={`${hitRate}%`} detail={`${data?.hits ?? 0} hits`} />
        <KpiCard label="Requests" value={`${data?.total ?? 0}`} detail="Logged requests" />
        <KpiCard label="Savings" value="Live" detail="Cache hits return zero cost" />
        <KpiCard label="Scope" value="Tenant" detail="Isolated by owner and model" />
      </section>
      <section className="card" style={{ marginTop: 16 }}>
        <h2>Hit Rate Trend</h2>
        <CacheHitRate />
      </section>
    </>
  );
}
