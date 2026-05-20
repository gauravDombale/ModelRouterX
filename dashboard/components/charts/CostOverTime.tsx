"use client";

import { CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

type TrendPoint = {
  time: string;
  cost: number;
  rate: number;
  requests: number;
};

const defaultData = [
  { time: "00:00", cost: 0.0 },
  { time: "04:00", cost: 0.0 },
  { time: "08:00", cost: 0.0 },
  { time: "12:00", cost: 0.0 },
  { time: "16:00", cost: 0.0 },
  { time: "20:00", cost: 0.0 }
];

export function CostOverTime({ data = [] }: { data?: TrendPoint[] }) {
  const chartData = data.length > 0 ? data : defaultData;

  return (
    <ResponsiveContainer width="100%" height={260}>
      <LineChart data={chartData}>
        <CartesianGrid stroke="#e5e9f0" />
        <XAxis dataKey="time" />
        <YAxis tickFormatter={(v) => `$${Number(v).toFixed(3)}`} />
        <Tooltip formatter={(v) => `$${Number(v).toFixed(4)}`} />
        <Line type="monotone" dataKey="cost" stroke="#2563eb" strokeWidth={2} dot={false} />
      </LineChart>
    </ResponsiveContainer>
  );
}


