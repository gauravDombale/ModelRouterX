"use client";

import { RefreshCw } from "lucide-react";
import { useGateway } from "@/lib/hooks/useGateway";
import { RequestLogTable } from "@/components/tables/RequestLogTable";

type RequestRow = {
  request_id: string;
  created_at: string;
  model: string;
  provider: string;
  task_type: string;
  latency_ms: number;
  cost_usd: string;
  cache_status: string;
  status_code: number;
};

export function RequestsPanel({ fallbackRows }: { fallbackRows: RequestRow[] }) {
  const { data, error, isLoading, mutate } = useGateway<{ data: RequestRow[] }>("/api/v1/analytics/requests?limit=50", { data: fallbackRows });

  return (
    <>
      <div className="toolbar">
        <button className="button" onClick={() => void mutate()} disabled={isLoading}>
          <RefreshCw size={16} />
          Refresh
        </button>
        {error ? <span className="badge">gateway unavailable</span> : null}
      </div>
      <section className="card">
        <RequestLogTable rows={data?.data ?? []} />
      </section>
    </>
  );
}
