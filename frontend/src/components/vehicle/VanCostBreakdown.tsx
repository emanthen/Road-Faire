import CostLine from "@/components/cost/CostLine";
import CostTable from "@/components/cost/CostTable";
import type { VanCostBreakdown as VanCostBreakdownData } from "@/types/planner";

function toCents(decimalString: string): number {
  return Math.round(parseFloat(decimalString) * 100);
}

/** Itemised campervan true-cost table — every line true_cost() computed, never a
 * collapsed single "transport" number (BUILD_PROMPT §4.1 / C1). Lines that are always
 * zero for a given trip (no one-way drop, no generator hours, no hookups, no add-ons)
 * still render at $0 rather than being hidden — the itinerary should show what wasn't
 * charged, not just what was. */
export default function VanCostBreakdown({ breakdown }: { breakdown: VanCostBreakdownData }) {
  return (
    <div className="mt-3">
      <p className="text-sm text-asphalt">Van cost, itemised</p>
      <CostTable>
        <CostLine label="Base rate" amountCents={toCents(breakdown.base)} />
        <CostLine label="Mileage overage" amountCents={toCents(breakdown.mileage_overage)} />
        <CostLine label="Prep fee" amountCents={toCents(breakdown.prep_fee)} />
        <CostLine label="Insurance" amountCents={toCents(breakdown.insurance)} />
        <CostLine label="One-way fee" amountCents={toCents(breakdown.one_way_fee)} />
        <CostLine label="Generator" amountCents={toCents(breakdown.generator)} />
        <CostLine label="Hookup premium" amountCents={toCents(breakdown.hookup_premium)} />
        <CostLine label="Add-ons" amountCents={toCents(breakdown.addons)} />
        <CostLine label="Van total" amountCents={toCents(breakdown.total)} accent />
      </CostTable>
    </div>
  );
}
