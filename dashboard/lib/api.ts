export const gatewayUrl = process.env.NEXT_PUBLIC_GATEWAY_URL ?? "http://localhost:8000";

export async function gatewayFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const baseUrl = typeof window === "undefined" ? gatewayUrl : "";
  const res = await fetch(`${baseUrl}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {})
    },
    cache: "no-store"
  });
  if (!res.ok) {
    throw new Error(await res.text());
  }
  return res.json() as Promise<T>;
}

export type StoredKey = {
  key: string;
  keyPrefix: string;
};

export function readStoredKey(): StoredKey | null {
  if (typeof window === "undefined") return null;
  const raw = window.localStorage.getItem("mrx_api_key");
  const prefix = window.localStorage.getItem("mrx_key_prefix");
  return raw ? { key: raw, keyPrefix: prefix ?? raw.slice(0, 12) } : null;
}

export function writeStoredKey(key: string, keyPrefix: string) {
  window.localStorage.setItem("mrx_api_key", key);
  window.localStorage.setItem("mrx_key_prefix", keyPrefix);
}

export const demoCost = {
  total_cost_usd: "128.42",
  by_model: [
    { model: "gpt-4o-mini-2024-07-18", requests: 18240, cost_usd: "28.12" },
    { model: "claude-sonnet-4-20250514", requests: 4120, cost_usd: "72.33" },
    { model: "gemini-2.0-flash", requests: 9850, cost_usd: "9.42" }
  ]
};
