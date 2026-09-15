"use client";

import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { ClimateNormal } from "@/types/api";

const MONTH_LABELS = [
  "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
];

export default function ClimateChart({ normals }: { normals: ClimateNormal[] }) {
  const data = normals
    .slice()
    .sort((a, b) => a.month - b.month)
    .map((n) => ({
      month: MONTH_LABELS[n.month - 1],
      high: parseFloat(n.high_f),
      low: parseFloat(n.low_f),
    }));

  if (data.length === 0) {
    return <p className="text-asphalt">No climate data yet.</p>;
  }

  return (
    <div className="h-64 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#6B716933" />
          <XAxis dataKey="month" stroke="#6B7169" fontSize={12} />
          <YAxis stroke="#6B7169" fontSize={12} unit="°F" />
          <Tooltip />
          <Line type="monotone" dataKey="high" stroke="#E8A33D" strokeWidth={2} dot={false} />
          <Line type="monotone" dataKey="low" stroke="#24503F" strokeWidth={2} dot={false} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
