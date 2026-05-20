import { RoutingTester } from "@/components/controls/RoutingTester";

export default function RoutingPage() {
  return (
    <>
      <header className="page-header">
        <div>
          <h1 className="page-title">Routing Rules</h1>
          <p className="muted">Priority-ordered conditions evaluated before strategy scoring.</p>
        </div>
      </header>
      <RoutingTester />
    </>
  );
}
