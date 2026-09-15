import type { Metadata } from "next";
import { notFound } from "next/navigation";
import FitBadge from "@/components/vehicle/FitBadge";
import SizeChecker from "@/components/vehicle/SizeChecker";
import VerifiedAt from "@/components/spot/VerifiedAt";
import { ApiError, fetchSpot } from "@/lib/api";
import { safeSpotMetadata } from "@/lib/seo";
import type { SpotDetail } from "@/types/api";

export async function generateMetadata({
  params,
}: {
  params: Promise<{ slug: string }>;
}): Promise<Metadata> {
  const { slug } = await params;
  return safeSpotMetadata(slug, "Campervan access");
}

export default async function CampervanPage({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await params;
  let spot;
  try {
    spot = await fetchSpot(slug);
  } catch (error) {
    if (error instanceof ApiError && error.statusCode === 404) notFound();
    throw error;
  }

  return (
    <div>
      <h1 className="mb-6 text-2xl font-semibold text-pine">
        Campervan access at {spot.name}
      </h1>
      <SizeChecker spotSlug={spot.slug} />
      {spot.vehicle_limits.length === 0 ? (
        <p className="mt-4 text-asphalt">No vehicle size limits on file for this spot yet.</p>
      ) : (
        <ul className="mt-6 flex flex-col gap-4">
          {spot.vehicle_limits.map((limit, i) => (
            <li key={i} className="border-b border-asphalt/20 pb-4">
              <div className="flex items-center gap-2">
                <FitBadge status="warning" />
                <span className="figure text-ink">
                  {limit.max_length_ft ? `${limit.max_length_ft} ft long` : "No length limit"}
                  {limit.max_height_ft ? `, ${limit.max_height_ft} ft tall` : ""}
                </span>
              </div>
              {limit.applies_to_roads.length > 0 && (
                <p className="mt-1 text-sm text-asphalt">
                  Applies to: {limit.applies_to_roads.join(", ")}
                </p>
              )}
              {limit.effective_from && (
                <p className="mt-1 text-sm text-asphalt">Effective from {limit.effective_from}</p>
              )}
              <div className="mt-1">
                <VerifiedAt date={limit.verified_at} />
              </div>
            </li>
          ))}
        </ul>
      )}
      <AmenitiesSummary amenities={spot.amenities} />
    </div>
  );
}

function AmenitiesSummary({ amenities }: { amenities: SpotDetail["amenities"] }) {
  const dumpStations = amenities.filter((a) => a.kind === "dump_station").length;
  const water = amenities.filter((a) => a.kind === "water").length;

  if (dumpStations === 0 && water === 0) {
    return null;
  }

  return (
    <div className="mt-8 border-t border-asphalt/20 pt-6">
      <h2 className="text-sm font-medium text-ink">Nearby amenities</h2>
      <ul className="mt-2 flex flex-col gap-1 text-sm text-asphalt">
        {dumpStations > 0 && <li>{dumpStations} dump station(s) within 12 miles</li>}
        {water > 0 && <li>{water} potable water point(s) within 3 miles</li>}
      </ul>
      <p className="mt-2 text-xs text-asphalt">
        From{" "}
        <a
          href="https://www.openstreetmap.org/copyright"
          className="underline hover:text-pine"
        >
          OpenStreetMap
        </a>{" "}
        contributors. Not independently verified, and exact locations may have changed.
      </p>
    </div>
  );
}
