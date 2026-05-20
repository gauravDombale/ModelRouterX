import { RequestsPanel } from "@/components/controls/RequestsPanel";

const rows = [
  { request_id: "req_01", created_at: new Date().toISOString(), model: "gpt-4o-mini-2024-07-18", provider: "openai", task_type: "chat", latency_ms: 612, cost_usd: "0.0004", cache_status: "miss", status_code: 200 },
  { request_id: "req_02", created_at: new Date().toISOString(), model: "claude-sonnet-4-20250514", provider: "anthropic", task_type: "code", latency_ms: 1320, cost_usd: "0.0112", cache_status: "hit_semantic", status_code: 200 }
];

export default function RequestsPage() {
  return (
    <>
      <header className="page-header">
        <div>
          <h1 className="page-title">Request Log</h1>
          <p className="muted">Filter requests by provider, model, cache status, task type, and status code.</p>
        </div>
      </header>
      <RequestsPanel fallbackRows={rows} />
    </>
  );
}
