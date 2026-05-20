import { CachePanel } from "@/components/controls/CachePanel";

export default function CachePage() {
  return (
    <>
      <header className="page-header">
        <div>
          <h1 className="page-title">Semantic Cache</h1>
          <p className="muted">Tenant-isolated exact and semantic cache performance.</p>
        </div>
      </header>
      <CachePanel />
    </>
  );
}
