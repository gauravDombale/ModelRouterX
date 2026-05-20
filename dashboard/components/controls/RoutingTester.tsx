"use client";

import { Play, Plus } from "lucide-react";
import { useState } from "react";
import { gatewayFetch, readStoredKey, writeStoredKey } from "@/lib/api";

type RoutingResult = {
  routed_model: string;
  provider: string;
  strategy: string;
  task_type: string;
  reason: string;
  fallback_chain: string[];
};

async function ensureKey(): Promise<string> {
  const stored = readStoredKey();
  if (stored?.key) return stored.key;
  const result = await gatewayFetch<{ key: string; key_prefix: string }>("/api/v1/keys", {
    method: "POST",
    body: JSON.stringify({ name: "dashboard-routing", routing_strategy: "balanced" })
  });
  writeStoredKey(result.key, result.key_prefix);
  return result.key;
}

export function RoutingTester() {
  const [prompt, setPrompt] = useState("Write a Python function to redact PHI from a patient note.");
  const [ruleName, setRuleName] = useState("PHI compliance");
  const [promptContains, setPromptContains] = useState("HIPAA, PHI, patient");
  const [targetModel, setTargetModel] = useState("gpt-4o-mini-2024-07-18");
  const [result, setResult] = useState<RoutingResult | null>(null);
  const [status, setStatus] = useState("");

  async function run() {
    setStatus("Testing...");
    const key = await ensureKey();
    const data = await gatewayFetch<RoutingResult>("/api/v1/routing/test", {
      method: "POST",
      headers: { Authorization: `Bearer ${key}` },
      body: JSON.stringify({ model: "auto", messages: [{ role: "user", content: prompt }], max_tokens: 256 })
    });
    setResult(data);
    setStatus("Done");
  }

  async function addRule() {
    setStatus("Creating rule...");
    const key = await ensureKey();
    await gatewayFetch<{ id: string; name: string }>("/api/v1/routing/rules", {
      method: "POST",
      headers: { Authorization: `Bearer ${key}` },
      body: JSON.stringify({
        name: ruleName,
        priority: 10,
        conditions: { prompt_contains: promptContains.split(",").map((term) => term.trim()).filter(Boolean) },
        target_model: targetModel,
        is_active: true
      })
    });
    setStatus("Rule created");
  }

  return (
    <section className="grid cols-2">
      <div className="card">
        <h2>Rule Editor</h2>
        <div className="grid">
          <input className="input" placeholder="Rule name" value={ruleName} onChange={(event) => setRuleName(event.target.value)} />
          <input className="input" placeholder="Prompt contains" value={promptContains} onChange={(event) => setPromptContains(event.target.value)} />
          <select className="select" aria-label="Target model" value={targetModel} onChange={(event) => setTargetModel(event.target.value)}>
            <option>gpt-4o-mini-2024-07-18</option>
            <option>gpt-4o-2024-11-20</option>
            <option>gemini-2.0-flash</option>
            <option>groq/llama-3.1-8b</option>
          </select>
          <button className="button" onClick={() => void addRule()}>
            <Plus size={16} />
            Add Rule
          </button>
        </div>
      </div>
      <div className="card">
        <h2>Test Routing</h2>
        <textarea className="textarea" value={prompt} onChange={(event) => setPrompt(event.target.value)} />
        <div className="toolbar" style={{ marginTop: 12 }}>
          <button className="button primary" onClick={() => void run()}>
            <Play size={16} />
            Run
          </button>
          {status ? <span className="badge">{status}</span> : null}
        </div>
        {result ? (
          <div className="grid">
            <span className="badge">{result.routed_model}</span>
            <p className="muted">{result.provider} · {result.strategy} · {result.task_type}</p>
            <p>{result.reason}</p>
          </div>
        ) : null}
      </div>
    </section>
  );
}
