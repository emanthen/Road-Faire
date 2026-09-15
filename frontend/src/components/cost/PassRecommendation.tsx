import type { EntryFeeBreakdown } from "@/lib/schemas";

export default function PassRecommendation({
  recommendation,
}: {
  recommendation: EntryFeeBreakdown["recommendation"];
}) {
  return <p className="mt-4 text-ink">{recommendation.explanation}</p>;
}
