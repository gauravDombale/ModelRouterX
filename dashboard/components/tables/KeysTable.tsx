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

export function KeysTable({ rows }: { rows: KeyRow[] }) {
  return (
    <table className="table">
      <thead>
        <tr>
          <th>Name</th>
          <th>Prefix</th>
          <th>Owner</th>
          <th>Budget</th>
          <th>RPM</th>
          <th>TPM</th>
          <th>Strategy</th>
          <th>Status</th>
        </tr>
      </thead>
      <tbody>
        {rows.map((row) => (
          <tr key={row.id}>
            <td>{row.name}</td>
            <td>{row.key_prefix}</td>
            <td>{row.owner_id}</td>
            <td>${row.budget_used_usd} / {row.budget_limit_usd ? `$${row.budget_limit_usd}` : "unlimited"}</td>
            <td>{row.rpm_limit ?? "none"}</td>
            <td>{row.tpm_limit ?? "none"}</td>
            <td>{row.routing_strategy}</td>
            <td><span className="badge">{row.is_active ? "active" : "revoked"}</span></td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

