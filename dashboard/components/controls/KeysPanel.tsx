"use client";

import { Plus, RefreshCw } from "lucide-react";
import { useState } from "react";
import { gatewayFetch, readStoredKey, writeStoredKey } from "@/lib/api";
import { useGateway } from "@/lib/hooks/useGateway";
import { KeysTable } from "@/components/tables/KeysTable";

type KeyRow = {
  id: string;
  key_prefix: string;
  name: string;
  owner_id: string;
  budget_used_usd: string;
  budget_limit_usd: string | null;
  rpm_limit: number | null;
  tpm_limit: number | null;
  routing_strategy: string;
  is_active: boolean;
};

export function KeysPanel({ fallbackRows }: { fallbackRows: KeyRow[] }) {
  const { data, mutate } = useGateway<{ data: KeyRow[] }>("/api/v1/keys", { data: fallbackRows });
  const [name, setName] = useState("dashboard-key");
  const [createdKey, setCreatedKey] = useState(readStoredKey()?.key ?? "");
  const [status, setStatus] = useState("");

  async function createKey() {
    setStatus("Creating...");
    const result = await gatewayFetch<{ key: string; key_prefix: string }>("/api/v1/keys", {
      method: "POST",
      body: JSON.stringify({ name, routing_strategy: "balanced" })
    });
    writeStoredKey(result.key, result.key_prefix);
    setCreatedKey(result.key);
    setStatus("Created and stored for routing tests.");
    await mutate();
  }

  return (
    <>
      <div className="toolbar">
        <input className="input" value={name} onChange={(event) => setName(event.target.value)} aria-label="Key name" />
        <button className="button primary" onClick={() => void createKey()}>
          <Plus size={16} />
          Create
        </button>
        <button className="button" onClick={() => void mutate()}>
          <RefreshCw size={16} />
          Refresh
        </button>
        {status ? <span className="badge">{status}</span> : null}
      </div>
      {createdKey ? (
        <section className="card" style={{ marginBottom: 14 }}>
          <div className="muted">Latest key</div>
          <code style={{ wordBreak: "break-all" }}>{createdKey}</code>
        </section>
      ) : null}
      <section className="card">
        <KeysTable rows={data?.data ?? []} />
      </section>
    </>
  );
}
