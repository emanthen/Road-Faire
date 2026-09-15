import { formatUSD } from "@/lib/money";

export default function CostLine({
  label,
  amountCents,
  accent = false,
}: {
  label: string;
  amountCents: number;
  accent?: boolean;
}) {
  return (
    <div className="flex items-baseline justify-between border-b border-asphalt/20 py-2">
      <span className={accent ? "font-semibold text-ink" : "text-ink"}>{label}</span>
      <span className={`figure text-ink ${accent ? "font-semibold" : ""}`}>
        {formatUSD(amountCents)}
      </span>
    </div>
  );
}
