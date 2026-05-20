"use client";

import { Area, AreaChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

type TrendPoint = {
  time: string;
  cost: number;
  rate: number;
  requests: number;
};

const defaultData = [
  { time: "Mon", rate: 0.18 },
  { time: "Tue", rate: 0.22 },
  { time: "Wed", rate: 0.31 },
  { time: "Thu", rate: 0.35 },
  { time: "Fri", rate: 0.38 }
];

export function CacheHitRate({ data = [] }: { data?: TrendPoint[] }) {
  const chartData = data.length > 0 ? data : defaultData;

  return (
    <ResponsiveContainer width="100%" height={240}>
      <AreaChart data={chartData}>
        <CartesianGrid stroke="#e5e9f0" />
        <XAxis dataKey="time" />
        <YAxis tickFormatter={(v) => `${Math.round(Number(v) * 100)}%`} />
        <Tooltip formatter={(v) => `${Math.round(Number(v) * 100)}%`} />
        <Area dataKey="rate" stroke="#0f9f6e" fill="#dff7ed" />
      </AreaChart>
    </ResponsiveContainer>
  );
}


