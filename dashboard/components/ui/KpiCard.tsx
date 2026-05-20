type KpiCardProps = {
  label: string;
  value: string;
  detail: string;
};

export function KpiCard({ label, value, detail }: KpiCardProps) {
  return (
    <section className="card">
      <div className="muted">{label}</div>
      <div className="metric">{value}</div>
      <div className="muted">{detail}</div>
    </section>
  );
}

