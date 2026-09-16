import { formatUSD } from "@/lib/money";

export default function CostLine({
  label,
  amountCents,
  accent = false,
  isEstimate = false,
  rangeLowCents,
  rangeHighCents,
}: {
  label: string;
  amountCents: number;
  accent?: boolean;
  /** True when this figure is a bootstrap assumption, not cited data — shows a range
   * and an "estimate" badge instead of a fake-precise single dollar amount
   * (BUILD_PROMPT C2: "$95-140/night (estimate)" is honest, "$120.00" is not). */
  isEstimate?: boolean;
  rangeLowCents?: number;
  rangeHighCents?: number;
}) {
  const showRange = isEstimate && rangeLowCents !== undefined && rangeHighCents !== undefined;

  return (
    <div className="flex items-baseline justify-between border-b border-asphalt/20 py-2">
      <span className={accent ? "font-semibold text-ink" : "text-ink"}>
        {label}
        {isEstimate && <span className="ml-2 text-xs text-asphalt">(estimate)</span>}
      </span>
      <span className={`figure text-ink ${accent ? "font-semibold" : ""}`}>
        {showRange
          ? `${formatUSD(rangeLowCents!)}–${formatUSD(rangeHighCents!)}`
          : formatUSD(amountCents)}
      </span>
    </div>
  );
}
