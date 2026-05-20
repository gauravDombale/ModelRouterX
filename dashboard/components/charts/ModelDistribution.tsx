"use client";

import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts";

const colors = ["#2563eb", "#0f9f6e", "#b7791f", "#d92d20"];

export function ModelDistribution({ data }: { data: { model: string; requests: number }[] }) {
  return (
    <ResponsiveContainer width="100%" height={260}>
      <PieChart>
        <Pie data={data} dataKey="requests" nameKey="model" outerRadius={92} innerRadius={48}>
          {data.map((item, index) => (
            <Cell key={item.model} fill={colors[index % colors.length]} />
          ))}
        </Pie>
        <Tooltip />
      </PieChart>
    </ResponsiveContainer>
  );
}

