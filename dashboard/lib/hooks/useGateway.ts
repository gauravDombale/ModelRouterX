"use client";

import useSWR from "swr";
import { gatewayFetch } from "@/lib/api";

export function useGateway<T>(path: string, fallbackData: T) {
  return useSWR<T>(path, gatewayFetch, { fallbackData, refreshInterval: 5000 });
}

