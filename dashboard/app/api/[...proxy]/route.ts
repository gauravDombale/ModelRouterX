import { NextRequest } from "next/server";

const gatewayUrl = (process.env.GATEWAY_URL ?? process.env.NEXT_PUBLIC_GATEWAY_URL ?? "http://localhost:8000").replace(
  /\/$/,
  ""
);

async function proxy(req: NextRequest, context: { params: Promise<{ proxy: string[] }> }) {
  const { proxy } = await context.params;
  const target = `${gatewayUrl}/api/${proxy.join("/")}${req.nextUrl.search}`;
  const body = req.method === "GET" || req.method === "HEAD" ? undefined : await req.text();
  return fetch(target, {
    method: req.method,
    headers: req.headers,
    body,
    cache: "no-store"
  });
}

export const GET = proxy;
export const POST = proxy;
export const PUT = proxy;
export const DELETE = proxy;
