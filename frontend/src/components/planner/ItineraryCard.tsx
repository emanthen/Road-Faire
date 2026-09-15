import CostLine from "@/components/cost/CostLine";
import CostTable from "@/components/cost/CostTable";
import DayTimeline from "@/components/planner/DayTimeline";
import { formatUSD } from "@/lib/money";
import type { SpotDetail } from "@/types/api";
import type { LegWaypoints, TripOption } from "@/types/planner";

const TIER_LABELS: Record<TripOption["tier"], string> = {
  LEAN: "Lean",
  BALANCED: "Balanced",
  COMFORT: "Comfort",
};

function toCents(decimalString: string): number {
  return Math.round(parseFloat(decimalString) * 100);
}

export default function ItineraryCard({
  option,
  spotDetails,
  legWaypoints,
}: {
  option: TripOption;
  spotDetails: Record<string, SpotDetail | null>;
  legWaypoints?: LegWaypoints[];
}) {
  return (
    <div className="border-b border-asphalt/20 pb-8">
      <div className="flex items-baseline justify-between">
        <h3 className="text-lg font-semibold text-pine">{TIER_LABELS[option.tier]}</h3>
        <span className="figure text-xl text-ink">{formatUSD(toCents(option.cost.total))}</span>
      </div>
      <p className="mt-1 text-sm text-asphalt">
        {option.loop.days}-day trip, {option.loop.stops.length}{" "}
        {option.loop.stops.length === 1 ? "stop" : "stops"}, {option.loop.total_miles} miles
      </p>

      <div className="mt-4">
        <DayTimeline loop={option.loop} spotDetails={spotDetails} legWaypoints={legWaypoints} />
      </div>

      <div className="mt-4">
        <CostTable>
          <CostLine label="Transport" amountCents={toCents(option.cost.transport)} />
          <CostLine label="Lodging" amountCents={toCents(option.cost.lodging)} />
          <CostLine label="Entry fees" amountCents={toCents(option.cost.entry)} />
          <CostLine label="Fuel" amountCents={toCents(option.cost.fuel)} />
          <CostLine label="Food" amountCents={toCents(option.cost.food)} />
          <CostLine label="Buffer (15%)" amountCents={toCents(option.cost.buffer)} />
        </CostTable>
      </div>
    </div>
  );
}
