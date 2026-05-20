"use client";

import { RefreshCw } from "lucide-react";
import { useGateway } from "@/lib/hooks/useGateway";

type ProviderRow = {
  provider: string;
  model: string;
  is_healthy: boolean;
  circuit_state: string;
};

export function ProvidersPanel({ fallbackRows }: { fallbackRows: ProviderRow[] }) {
  const { data, mutate } = useGateway<{ providers: ProviderRow[] }>("/api/v1/providers/health", { providers: fallbackRows });
  const rows = data?.providers ?? [];

  return (
    <>
      <div className="toolbar">
        <button className="button" onClick={() => void mutate()}>
          <RefreshCw size={16} />
          Refresh
        </button>
      </div>
      <section className="card">
        <table className="table">
          <thead>
            <tr><th>Provider</th><th>Model</th><th>Health</th><th>Circuit</th></tr>
          </thead>
          <tbody>
            {rows.map((row) => (
              <tr key={`${row.provider}-${row.model}`}>
                <td>{row.provider}</td>
                <td>{row.model}</td>
                <td><span className={`status-dot ${row.is_healthy ? "" : "down"}`} /> {row.is_healthy ? "healthy" : "down"}</td>
                <td><span className="badge">{row.circuit_state}</span></td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>
    </>
  );
}
