import type { Metadata } from "next";
import { notFound } from "next/navigation";
import ClimateChart from "@/components/spot/ClimateChart";
import MonthGrid from "@/components/spot/MonthGrid";
import { ApiError, fetchSpot } from "@/lib/api";
import { safeSpotMetadata } from "@/lib/seo";

export async function generateMetadata({
  params,
}: {
  params: Promise<{ slug: string }>;
}): Promise<Metadata> {
  const { slug } = await params;
  return safeSpotMetadata(slug, "Best time to visit");
}

export default async function BestTimeToVisitPage({
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
        Best time to visit {spot.name}
      </h1>
      <div className="mb-8">
        <h2 className="mb-2 text-sm text-asphalt">Crowds by month (darker = busier)</h2>
        <MonthGrid crowdIndexes={spot.crowd_indexes} />
      </div>
      <div>
        <h2 className="mb-2 text-sm text-asphalt">Average temperature by month</h2>
        <ClimateChart normals={spot.climate_normals} />
      </div>
    </div>
  );
}
