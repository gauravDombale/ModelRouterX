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

export function RequestLogTable({ rows }: { rows: RequestRow[] }) {
  return (
    <table className="table">
      <thead>
        <tr>
          <th>Time</th>
          <th>Model</th>
          <th>Provider</th>
          <th>Task</th>
          <th>Latency</th>
          <th>Cost</th>
          <th>Cache</th>
          <th>Status</th>
        </tr>
      </thead>
      <tbody>
        {rows.map((row) => (
          <tr key={row.request_id}>
            <td>{new Date(row.created_at).toLocaleString()}</td>
            <td>{row.model}</td>
            <td>{row.provider}</td>
            <td><span className="badge">{row.task_type}</span></td>
            <td>{row.latency_ms}ms</td>
            <td>${row.cost_usd}</td>
            <td>{row.cache_status}</td>
            <td>{row.status_code}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

