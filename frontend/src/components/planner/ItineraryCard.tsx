import CostLine from "@/components/cost/CostLine";
import CostTable from "@/components/cost/CostTable";
import PassRecommendation from "@/components/cost/PassRecommendation";
import RouteLayer from "@/components/map/RouteLayer";
import SpotMap from "@/components/map/SpotMap";
import DayTimeline from "@/components/planner/DayTimeline";
import VanCostBreakdown from "@/components/vehicle/VanCostBreakdown";
import { formatUSD } from "@/lib/money";
import type { SpotDetail } from "@/types/api";
import type { CostRange, LegWaypoints, TripOption } from "@/types/planner";

const TIER_LABELS: Record<TripOption["tier"], string> = {
  LEAN: "Lean",
  BALANCED: "Balanced",
  COMFORT: "Comfort",
};

function toCents(decimalString: string): number {
  return Math.round(parseFloat(decimalString) * 100);
}

function rangeCents(range: CostRange | null): { low: number; high: number } | undefined {
  if (!range) return undefined;
  return { low: toCents(range.low), high: toCents(range.high) };
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
  const { cost } = option;
  const isEstimate = (category: string) => cost.estimated_categories.includes(category);
  const transportRange = rangeCents(cost.transport_range);
  const lodgingRange = rangeCents(cost.lodging_range);

  return (
    <div className="border-b border-asphalt/20 pb-8">
      <div className="flex items-baseline justify-between">
        <h3 className="text-lg font-semibold text-pine">{TIER_LABELS[option.tier]}</h3>
        <span className="figure text-xl text-ink">{formatUSD(toCents(cost.total))}</span>
      </div>
      <p className="mt-1 text-sm text-asphalt">
        {option.loop.days}-day trip, {option.loop.stops.length}{" "}
        {option.loop.stops.length === 1 ? "stop" : "stops"}, {option.loop.total_miles} miles
      </p>

      {option.narrative && <p className="mt-3 text-ink">{option.narrative}</p>}

      {option.loop.stops.length > 0 && (
        <div className="mt-4">
          <SpotMap
            latitude={option.loop.stops[0].latitude}
            longitude={option.loop.stops[0].longitude}
            zoom={6}
          >
            <RouteLayer loop={option.loop} />
          </SpotMap>
        </div>
      )}

      <div className="mt-4">
        <DayTimeline loop={option.loop} spotDetails={spotDetails} legWaypoints={legWaypoints} />
      </div>

      <div className="mt-4">
        <CostTable>
          {cost.van_breakdown === null && (
            <CostLine
              label="Transport"
              amountCents={toCents(cost.transport)}
              isEstimate={isEstimate("transport")}
              rangeLowCents={transportRange?.low}
              rangeHighCents={transportRange?.high}
            />
          )}
          <CostLine
            label="Lodging"
            amountCents={toCents(cost.lodging)}
            isEstimate={isEstimate("lodging")}
            rangeLowCents={lodgingRange?.low}
            rangeHighCents={lodgingRange?.high}
          />
          <CostLine label="Entry fees" amountCents={toCents(cost.entry)} />
          <CostLine
            label="Fuel"
            amountCents={toCents(cost.fuel)}
            isEstimate={isEstimate("fuel")}
          />
          <CostLine label="Food" amountCents={toCents(cost.food)} />
          <CostLine label="Buffer (15%)" amountCents={toCents(cost.buffer)} />
        </CostTable>
        {cost.van_breakdown !== null && <VanCostBreakdown breakdown={cost.van_breakdown} />}
      </div>

      <PassRecommendation recommendation={cost.entry_recommendation} />
    </div>
  );
}
