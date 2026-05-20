import { ProvidersPanel } from "@/components/controls/ProvidersPanel";

const rows = [
  { provider: "openai", model: "gpt-4o-mini-2024-07-18", is_healthy: true, circuit_state: "closed" },
  { provider: "google", model: "gemini-2.0-flash", is_healthy: true, circuit_state: "closed" },
  { provider: "groq", model: "groq/llama-3.1-8b", is_healthy: true, circuit_state: "closed" }
];

export default function ProvidersPage() {
  return (
    <>
      <header className="page-header">
        <div>
          <h1 className="page-title">Providers</h1>
          <p className="muted">Live health, latency windows, error rates, and circuit state.</p>
        </div>
      </header>
      <ProvidersPanel fallbackRows={rows} />
    </>
  );
}
