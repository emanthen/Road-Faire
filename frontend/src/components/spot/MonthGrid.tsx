import type { CrowdIndex } from "@/types/api";

const MONTH_LABELS = [
  "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
];

/** 12-month best-time heat table, keyed off crowd score (lower = quieter = greener). */
export default function MonthGrid({ crowdIndexes }: { crowdIndexes: CrowdIndex[] }) {
  const byMonth = new Map(crowdIndexes.map((c) => [c.month, c.score]));

  return (
    <div className="grid grid-cols-6 gap-2 sm:grid-cols-12">
      {MONTH_LABELS.map((label, i) => {
        const score = byMonth.get(i + 1);
        const opacity = score === undefined ? 0.1 : score / 100;
        return (
          <div key={label} className="text-center">
            <div
              className="h-10 rounded border border-pine/20"
              style={{ backgroundColor: `rgba(36, 80, 63, ${opacity})` }}
              aria-label={
                score === undefined ? `${label}: no data` : `${label}: crowd score ${score}`
              }
            />
            <span className="mt-1 block text-xs text-asphalt">{label}</span>
          </div>
        );
      })}
    </div>
  );
}
