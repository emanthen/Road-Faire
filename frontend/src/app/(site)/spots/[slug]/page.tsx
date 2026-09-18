import type { Metadata } from "next";
import { notFound } from "next/navigation";
import ActivityList from "@/components/spot/ActivityList";
import AtAGlance from "@/components/spot/AtAGlance";
import Gallery from "@/components/spot/Gallery";
import SpotHero from "@/components/spot/SpotHero";
import SpotMap from "@/components/map/SpotMap";
import SpotMarker from "@/components/map/SpotMarker";
import { ApiError, fetchSpot } from "@/lib/api";
import { safeSpotMetadata } from "@/lib/seo";

export async function generateMetadata({
  params,
}: {
  params: Promise<{ slug: string }>;
}): Promise<Metadata> {
  const { slug } = await params;
  return safeSpotMetadata(slug, "Overview");
}

export default async function SpotOverviewPage({
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
      <SpotHero
        name={spot.name}
        blurb={spot.blurb}
        highlights={spot.highlights}
        elevationFt={spot.elevation_ft}
        bestTimeToVisit={spot.best_time_to_visit}
      />
      {spot.photos.length > 0 && (
        <div className="mb-8">
          <Gallery photos={spot.photos} spotName={spot.name} />
        </div>
      )}
      <div className="grid gap-8 md:grid-cols-2">
        <div>
          <h2 className="mb-2 text-lg font-medium text-pine">At a glance</h2>
          <AtAGlance cost={spot.cost} contactPhone={spot.contact_phone} />
        </div>
        <SpotMap latitude={spot.latitude} longitude={spot.longitude}>
          <SpotMarker latitude={spot.latitude} longitude={spot.longitude} label={spot.name} />
        </SpotMap>
      </div>
      <div className="mt-8">
        <h2 className="mb-2 text-lg font-medium text-pine">Things to do</h2>
        <ActivityList activities={spot.activities} />
      </div>
    </div>
  );
}
