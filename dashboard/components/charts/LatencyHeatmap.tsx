"use client";

import { useGateway } from "@/lib/hooks/useGateway";

type ProviderRow = {
  provider: string;
  model: string;
  is_healthy: boolean;
  circuit_state: string;
  p50_latency_ms?: number;
  p95_latency_ms?: number;
};

const defaultProviders = [
  { provider: "Anthropic", model: "claude-haiku-4-5", is_healthy: true, circuit_state: "closed", p50_latency_ms: 1300, p95_latency_ms: 2800 },
  { provider: "OpenAI", model: "gpt-4o-mini", is_healthy: true, circuit_state: "closed", p50_latency_ms: 800, p95_latency_ms: 1700 },
  { provider: "Google", model: "gemini-2.0-flash", is_healthy: true, circuit_state: "closed", p50_latency_ms: 500, p95_latency_ms: 1200 },
  { provider: "Groq", model: "groq/llama-3.1-8b", is_healthy: true, circuit_state: "closed", p50_latency_ms: 100, p95_latency_ms: 300 },
  { provider: "Ollama", model: "ollama/llama3.1", is_healthy: true, circuit_state: "closed", p50_latency_ms: 300, p95_latency_ms: 900 }
];

export function LatencyHeatmap() {
  const { data } = useGateway<{ providers: ProviderRow[] }>("/api/v1/providers/health", { providers: [] });
  
  const rows = data?.providers && data.providers.length > 0 ? data.providers : defaultProviders;

  return (
    <table className="table">
      <thead>
        <tr>
          <th>Provider</th>
          <th>Model</th>
          <th>p50</th>
          <th>p95</th>
          <th>Circuit</th>
        </tr>
      </thead>
      <tbody>
        {rows.map((row) => {
          const p50Sec = row.p50_latency_ms ? `${(row.p50_latency_ms / 1000).toFixed(2)}s` : "0.00s";
          const p95Sec = row.p95_latency_ms ? `${(row.p95_latency_ms / 1000).toFixed(2)}s` : "0.00s";
          
          return (
            <tr key={`${row.provider}-${row.model}`}>
              <td style={{ textTransform: "capitalize" }}>{row.provider}</td>
              <td style={{ fontSize: "0.85em", color: "#666" }}>{row.model}</td>
              <td>{p50Sec}</td>
              <td>{p95Sec}</td>
              <td>
                <span className="badge">
                  {row.circuit_state}
                </span>
              </td>
            </tr>
          );
        })}
      </tbody>
    </table>
  );
}


