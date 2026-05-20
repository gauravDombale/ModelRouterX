import { OverviewPanel } from "@/components/controls/OverviewPanel";

export default function OverviewPage() {
  return (
    <>
      <header className="page-header">
        <div>
          <h1 className="page-title">Gateway Overview</h1>
          <p className="muted">Live routing, cost, latency, and cache posture.</p>
        </div>
      </header>
      <OverviewPanel />
    </>
  );
}


