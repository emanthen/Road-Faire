import CostLine from "@/components/cost/CostLine";
import PassRecommendation from "@/components/cost/PassRecommendation";
import SurchargeCallout from "@/components/cost/SurchargeCallout";
import { useCountUp } from "@/hooks/useCountUp";
import type { EntryFeeBreakdown } from "@/lib/schemas";

function toCents(decimalString: string): number {
  return Math.round(parseFloat(decimalString) * 100);
}

export default function ResultPanel({ breakdown }: { breakdown: EntryFeeBreakdown }) {
  const payAsYouGoCents = useCountUp(toCents(breakdown.pay_as_you_go_total));
  const annualPassCents = useCountUp(toCents(breakdown.annual_pass_total));
  const surchargeCents = breakdown.lines.reduce(
    (sum, line) => sum + toCents(line.surcharge),
    0
  );

  return (
    <div className="reveal mt-6">
      <SurchargeCallout amountCents={surchargeCents} />
      <div className="mt-4">
        <CostLine label="Paying as you go" amountCents={Math.round(payAsYouGoCents)} />
        <CostLine label="Annual pass" amountCents={Math.round(annualPassCents)} />
      </div>
      <PassRecommendation recommendation={breakdown.recommendation} />
    </div>
  );
}
