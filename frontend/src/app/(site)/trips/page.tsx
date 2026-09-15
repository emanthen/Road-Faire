import type { Metadata } from "next";
import Image from "next/image";
import Link from "next/link";
import PageHero from "@/components/layout/PageHero";
import { fetchFeaturedTrips } from "@/lib/api";
import { SURCHARGE_PARKS } from "@/lib/parks";
import { formatUSD } from "@/lib/money";

export const dynamic = "force-dynamic";

export const metadata: Metadata = {
  title: "Example trips - Roadfare",
  description: "Real, fully costed road-trip itineraries built by the planner.",
};

function toCents(decimalString: string): number {
  return Math.round(parseFloat(decimalString) * 100);
}

/** The API returns the real spot name per stop, not a slug — matched back against the
 * same park list the rest of the site uses so the card can show that spot's real photo,
 * not a generic placeholder. Falls back to the Grand Canyon hero photo on no match,
 * which only happens if a trip's first stop isn't one of the 11 seeded parks yet. */
function photoForDestination(name: string | undefined): string {
  const match = SURCHARGE_PARKS.find((park) => park.name === name);
  return `/images/parks/${match?.slug ?? "grca"}.jpg`;
}

export default async function TripsPage() {
  const trips = await fetchFeaturedTrips();

  return (
    <section className="px-6 py-16">
      <PageHero
        title="Example trips"
        description="Real itineraries built by the planner against the current catalog, not mockups."
        imageSrc="/images/parks/brca.jpg"
        imageAlt="Hikers on a trail among the hoodoos of Bryce Canyon National Park"
      />

      {trips.length === 0 ? (
        <p className="mt-10 text-asphalt">No example trips published yet.</p>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {trips.map((trip) => (
            <Link
              key={trip.id}
              href={`/plan/${trip.id}`}
              className="group flex flex-col overflow-hidden rounded-xl border border-asphalt/20"
            >
              <div className="relative aspect-[4/3] overflow-hidden bg-asphalt/10">
                <Image
                  src={photoForDestination(trip.destinations[0])}
                  alt=""
                  fill
                  sizes="(min-width: 1024px) 33vw, (min-width: 640px) 50vw, 100vw"
                  className="object-cover transition-transform duration-500 group-hover:scale-105"
                />
              </div>
              <div className="flex flex-1 flex-col gap-1 p-5">
                <span className="text-xs uppercase tracking-wide text-asphalt">
                  {trip.days}-day trip from {trip.origin_airport}
                </span>
                <h2 className="font-medium text-ink group-hover:text-pine">
                  {trip.destinations.join(", ") || "Trip"}
                </h2>
                {trip.from_total && (
                  <p className="mt-auto pt-3 text-sm text-asphalt">
                    from{" "}
                    <span className="figure text-base text-ink">
                      {formatUSD(toCents(trip.from_total))}
                    </span>
                  </p>
                )}
              </div>
            </Link>
          ))}
        </div>
      )}
    </section>
  );
}
