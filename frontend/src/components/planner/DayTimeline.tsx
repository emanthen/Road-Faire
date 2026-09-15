import { Fuel, UtensilsCrossed } from "lucide-react";
import Image from "next/image";
import { formatUSD } from "@/lib/money";
import type { SpotDetail } from "@/types/api";
import type { LegWaypoints, Loop } from "@/types/planner";

function toCents(decimalString: string): number {
  return Math.round(parseFloat(decimalString) * 100);
}

function LegWaypointsRow({ leg }: { leg: LegWaypoints }) {
  if (!leg.fuel && !leg.restaurant) return null;
  return (
    <div className="mt-2 grid grid-cols-2 gap-3 rounded-lg bg-asphalt/5 p-2 text-xs text-asphalt">
      <div className="flex items-start gap-1.5">
        <Fuel size={14} className="mt-0.5 shrink-0 text-pine" />
        {leg.fuel ? (
          <span>
            {leg.fuel.name} <span className="figure">&middot; {leg.fuel.distance_mi} mi</span>
          </span>
        ) : (
          <span className="text-asphalt/60">No fuel stop found nearby</span>
        )}
      </div>
      <div className="flex items-start gap-1.5">
        <UtensilsCrossed size={14} className="mt-0.5 shrink-0 text-pine" />
        {leg.restaurant ? (
          <span>
            {leg.restaurant.name}{" "}
            <span className="figure">&middot; {leg.restaurant.distance_mi} mi</span>
          </span>
        ) : (
          <span className="text-asphalt/60">No place to eat found nearby</span>
        )}
      </div>
    </div>
  );
}

export default function DayTimeline({
  loop,
  spotDetails,
  legWaypoints,
}: {
  loop: Loop;
  spotDetails: Record<string, SpotDetail | null>;
  legWaypoints?: LegWaypoints[];
}) {
  return (
    <ol className="flex flex-col gap-4">
      {loop.stops.map((stop, i) => {
        const feeCents = toCents(stop.standard_fee);
        const detail = spotDetails[stop.slug];
        const primaryPhoto = detail?.photos.find((p) => p.is_primary) ?? detail?.photos[0];
        const leg = legWaypoints?.[i];

        return (
          <li key={stop.slug} className="flex gap-4 border-b border-asphalt/20 pb-4">
            {primaryPhoto && (
              <div className="relative hidden h-20 w-20 shrink-0 overflow-hidden rounded-lg bg-asphalt/10 sm:block">
                <Image
                  src={primaryPhoto.url}
                  alt={primaryPhoto.alt_text || stop.name}
                  fill
                  sizes="80px"
                  className="object-cover"
                />
              </div>
            )}
            <div className="min-w-0 flex-1">
              <div className="flex flex-wrap items-baseline justify-between gap-x-4">
                <span className="font-medium text-ink">
                  Day {i + 1}: {stop.name}
                </span>
                <span className="figure shrink-0 text-asphalt">
                  {stop.nights} {stop.nights === 1 ? "night" : "nights"}
                </span>
              </div>

              <div className="mt-1 flex flex-wrap gap-x-4 gap-y-0.5 text-sm text-asphalt">
                {feeCents > 0 && (
                  <span>
                    Entry fee: <span className="figure">{formatUSD(feeCents)}</span>
                    {stop.fee_type === "person" ? " per person" : " per vehicle"}
                  </span>
                )}
                {detail?.elevation_ft && (
                  <span>
                    Elevation: <span className="figure">{detail.elevation_ft.toLocaleString()} ft</span>
                  </span>
                )}
                {stop.activities.length > 0 && (
                  <span>{stop.activities.map((activity) => activity.name).join(", ")}</span>
                )}
              </div>

              {detail?.best_time_to_visit && (
                <p className="mt-1 text-sm text-asphalt">
                  Best time to visit: {detail.best_time_to_visit}
                </p>
              )}
              {leg && <LegWaypointsRow leg={leg} />}
            </div>
          </li>
        );
      })}
    </ol>
  );
}
