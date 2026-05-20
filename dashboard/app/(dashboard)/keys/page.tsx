import { KeysPanel } from "@/components/controls/KeysPanel";

const rows = [
  { id: "1", key_prefix: "mrx_sk_abcd", name: "dev-key", owner_id: "default", budget_used_usd: "12.45", budget_limit_usd: "100.00", rpm_limit: 120, tpm_limit: 60000, routing_strategy: "balanced", is_active: true }
];

export default function KeysPage() {
  return (
    <>
      <header className="page-header">
        <div>
          <h1 className="page-title">Virtual Keys</h1>
          <p className="muted">Per-key budgets, limits, routing strategy overrides, and revocation.</p>
        </div>
      </header>
      <KeysPanel fallbackRows={rows} />
    </>
  );
}
