import type { Metadata } from "next";
import { notFound } from "next/navigation";
import ReservationRules from "@/components/spot/ReservationRules";
import { ApiError, fetchSpot } from "@/lib/api";
import { safeSpotMetadata } from "@/lib/seo";

export async function generateMetadata({
  params,
}: {
  params: Promise<{ slug: string }>;
}): Promise<Metadata> {
  const { slug } = await params;
  return safeSpotMetadata(slug, "Reservations");
}

export default async function ReservationsPage({
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
        Reservations at {spot.name}
      </h1>
      <ReservationRules rules={spot.reservation_rules} />
    </div>
  );
}
