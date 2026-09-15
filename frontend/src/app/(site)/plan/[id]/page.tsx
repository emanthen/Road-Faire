import { notFound } from "next/navigation";
import ExportPdfButton from "@/components/planner/ExportPdfButton";
import ItineraryList from "@/components/planner/ItineraryList";
import { ApiError, fetchPlan, fetchSpot } from "@/lib/api";
import type { SpotDetail } from "@/types/api";

const VEHICLE_LABELS = { car: "Car", van: "Campervan / van" } as const;

/**
 * Three costed options (LEAN/BALANCED/COMFORT).
 */
export default async function PlanResultsPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;

  let plan;
  try {
    plan = await fetchPlan(id);
  } catch (error) {
    if (error instanceof ApiError && error.statusCode === 404) notFound();
    throw error;
  }

  // Every option's stops, deduped — LEAN/BALANCED/COMFORT usually share most of the
  // same spots, so this is normally 3-5 fetches, not 3x that.
  const uniqueSlugs = Array.from(
    new Set(plan.options.flatMap((option) => option.loop.stops.map((stop) => stop.slug)))
  );
  const spotEntries = await Promise.all(
    uniqueSlugs.map(async (slug): Promise<[string, SpotDetail | null]> => {
      try {
        return [slug, await fetchSpot(slug)];
      } catch {
        return [slug, null];
      }
    })
  );
  const spotDetails = Object.fromEntries(spotEntries);

  const { request: tripRequest } = plan;
  const partySize = `${tripRequest.adults} adult${tripRequest.adults === 1 ? "" : "s"}${
    tripRequest.children > 0
      ? `, ${tripRequest.children} child${tripRequest.children === 1 ? "" : "ren"}`
      : ""
  }`;

  return (
    <section className="px-6 py-16">
      <div className="flex flex-wrap items-baseline justify-between gap-4">
        <h1 className="text-2xl font-semibold text-pine">Your trip options</h1>
        <ExportPdfButton planId={id} />
      </div>
      <p className="mt-2 text-sm text-asphalt">
        From {tripRequest.origin_airport} &middot; {tripRequest.start_date} to{" "}
        {tripRequest.end_date} &middot; {partySize} &middot;{" "}
        {VEHICLE_LABELS[tripRequest.vehicle_pref]}
      </p>

      <ItineraryList planId={id} options={plan.options} spotDetails={spotDetails} />
    </section>
  );
}
