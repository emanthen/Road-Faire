import type { Metadata } from "next";
import { notFound } from "next/navigation";
import CostLine from "@/components/cost/CostLine";
import CostTable from "@/components/cost/CostTable";
import VerifiedAt from "@/components/spot/VerifiedAt";
import { ApiError, fetchSpot } from "@/lib/api";
import { safeSpotMetadata } from "@/lib/seo";

export async function generateMetadata({
  params,
}: {
  params: Promise<{ slug: string }>;
}): Promise<Metadata> {
  const { slug } = await params;
  return safeSpotMetadata(slug, "Cost");
}

function toCents(decimalString: string | null): number | null {
  if (!decimalString) return null;
  return Math.round(parseFloat(decimalString) * 100);
}

export default async function SpotCostPage({
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
  const cost = spot.cost;

  return (
    <div>
      <h1 className="mb-2 text-2xl font-semibold text-pine">{spot.name}: cost breakdown</h1>
      <div className="mb-6">
        <VerifiedAt date={cost?.verified_at ?? null} />
      </div>
      {!cost ? (
        <p className="text-asphalt">Cost data hasn&apos;t been added for this spot yet.</p>
      ) : (
        <CostTable>
          {toCents(cost.entry_vehicle) !== null && (
            <CostLine label="Entrance (per vehicle)" amountCents={toCents(cost.entry_vehicle)!} />
          )}
          {toCents(cost.entry_person) !== null && (
            <CostLine label="Entrance (per person)" amountCents={toCents(cost.entry_person)!} />
          )}
          {toCents(cost.parking) !== null && (
            <CostLine label="Parking" amountCents={toCents(cost.parking)!} />
          )}
          {toCents(cost.campsite_low) !== null && (
            <CostLine label="Campsite (from)" amountCents={toCents(cost.campsite_low)!} />
          )}
          {toCents(cost.campsite_high) !== null && (
            <CostLine label="Campsite (up to)" amountCents={toCents(cost.campsite_high)!} />
          )}
          {toCents(cost.shuttle) !== null && (
            <CostLine label="Shuttle" amountCents={toCents(cost.shuttle)!} />
          )}
        </CostTable>
      )}
      <p className="mt-6 text-sm text-asphalt">
        Non-resident? Use the{" "}
        <a href="/tools/national-park-fee-calculator" className="text-pine underline">
          fee calculator
        </a>{" "}
        to check if the surcharge applies here.
      </p>
    </div>
  );
}
