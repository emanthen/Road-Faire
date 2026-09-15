"use client";

import { useEffect, useState } from "react";
import ItineraryCard from "@/components/planner/ItineraryCard";
import { fetchPlanWaypoints } from "@/lib/api";
import type { SpotDetail } from "@/types/api";
import type { TierWaypoints, TripOption } from "@/types/planner";

/** Fetches gas-station/restaurant suggestions once (they come from a live, sometimes
 * slow OpenStreetMap lookup) and hands each tier its own legs — rather than each
 * ItineraryCard fetching the same data three times. Missing or slow-to-load waypoints
 * degrade silently: the itinerary still renders immediately without them. */
export default function ItineraryList({
  planId,
  options,
  spotDetails,
}: {
  planId: string;
  options: TripOption[];
  spotDetails: Record<string, SpotDetail | null>;
}) {
  const [waypointsByTier, setWaypointsByTier] = useState<Record<string, TierWaypoints>>({});

  useEffect(() => {
    let cancelled = false;
    fetchPlanWaypoints(planId)
      .then((tiers) => {
        if (cancelled) return;
        setWaypointsByTier(Object.fromEntries(tiers.map((t) => [t.tier, t])));
      })
      .catch(() => {
        // Overpass being slow/unreachable shouldn't disturb the itinerary already shown.
      });
    return () => {
      cancelled = true;
    };
  }, [planId]);

  return (
    <div className="reveal-stagger mt-8 flex flex-col gap-10">
      {options.map((option) => (
        <ItineraryCard
          key={option.tier}
          option={option}
          spotDetails={spotDetails}
          legWaypoints={waypointsByTier[option.tier]?.legs}
        />
      ))}
    </div>
  );
}
