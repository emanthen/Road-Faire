import type { Metadata } from "next";
import Image from "next/image";
import Link from "next/link";
import PageHero from "@/components/layout/PageHero";
import Reveal from "@/components/layout/Reveal";
import { fetchSpots } from "@/lib/api";
import type { SpotType } from "@/types/api";

export const metadata: Metadata = {
  title: "Browse spots - Roadfare",
  description:
    "Real entry fees, best time to visit, vehicle limits, and reservation rules for every spot in the catalog.",
};

const TYPE_LABELS: Record<SpotType, string> = {
  national_park: "National park",
  state_park: "State park",
  monument: "National monument",
  forest: "National forest",
  other: "Other",
};

const ACTIVITY_LABELS: Record<string, string> = {
  trail: "Hiking trails",
  tour: "Tours",
};

/** Local convention, not API data — every spot currently in the catalog is one of the
 * 11 real parks whose photos already live here (see public/images/parks/SOURCES.txt). */
function photoUrl(slug: string): string {
  return `/images/parks/${slug}.jpg`;
}

export default async function SpotsPage({
  searchParams,
}: {
  searchParams: Promise<{ type?: string; state?: string; activity?: string }>;
}) {
  const { type, state, activity } = await searchParams;
  const { results } = await fetchSpots({ type, state, activity });

  return (
    <section className="px-6 py-16">
      <PageHero
        title="Browse spots"
        description="Entry fees, the best time to visit, vehicle limits, and reservation rules, not just a park name and a photo."
        imageSrc="/images/parks/zion.jpg"
        imageAlt="Visitors at a trailhead in Zion National Park"
      />

      <form
        action="/spots"
        className="flex flex-col gap-3 rounded-full border border-asphalt/20 bg-snow p-2 sm:flex-row sm:items-center"
      >
        <label className="flex flex-1 flex-col gap-0.5 px-4 py-1.5">
          <span className="text-xs font-medium text-asphalt">Type</span>
          <select
            name="type"
            defaultValue={type ?? ""}
            className="min-h-6 bg-transparent text-sm text-ink outline-none"
          >
            <option value="">All types</option>
            {Object.entries(TYPE_LABELS).map(([value, label]) => (
              <option key={value} value={value}>
                {label}
              </option>
            ))}
          </select>
        </label>

        <span className="hidden h-8 w-px bg-asphalt/20 sm:block" aria-hidden />

        <label className="flex flex-1 flex-col gap-0.5 px-4 py-1.5">
          <span className="text-xs font-medium text-asphalt">Activities</span>
          <select
            name="activity"
            defaultValue={activity ?? ""}
            className="min-h-6 bg-transparent text-sm text-ink outline-none"
          >
            <option value="">Any activity</option>
            {Object.entries(ACTIVITY_LABELS).map(([value, label]) => (
              <option key={value} value={value}>
                {label}
              </option>
            ))}
          </select>
        </label>

        <span className="hidden h-8 w-px bg-asphalt/20 sm:block" aria-hidden />

        <label className="flex flex-1 flex-col gap-0.5 px-4 py-1.5">
          <span className="text-xs font-medium text-asphalt">State</span>
          <input
            type="text"
            name="state"
            maxLength={2}
            defaultValue={state ?? ""}
            placeholder="Any state"
            className="figure min-h-6 w-full bg-transparent text-left text-sm uppercase text-ink outline-none placeholder:normal-case placeholder:text-asphalt/70"
          />
        </label>

        <button
          type="submit"
          className="m-0.5 flex min-h-11 shrink-0 items-center justify-center rounded-full bg-sodium px-7 font-medium text-ink hover:bg-snow hover:ring-1 hover:ring-inset hover:ring-sodium active:scale-[0.98]"
        >
          Filter
        </button>
      </form>

      {results.length === 0 ? (
        <p className="mt-10 text-asphalt">
          No spots match yet. The catalog is still being built out.
        </p>
      ) : (
        <Reveal>
          <div className="mt-8 grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-5">
            {results.map((spot) => (
              <Link
                key={spot.slug}
                href={`/spots/${spot.slug}`}
                className="group flex flex-col gap-2"
              >
                <div className="relative aspect-[4/3] overflow-hidden rounded-xl bg-asphalt/10">
                  <Image
                    src={photoUrl(spot.slug)}
                    alt={`NPS photo of ${spot.name}`}
                    fill
                    sizes="(min-width: 1024px) 20vw, (min-width: 640px) 33vw, 50vw"
                    className="object-cover transition-transform duration-500 group-hover:scale-105"
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-ink/75 via-ink/0 to-ink/0" />
                  <span className="absolute bottom-3 left-3 right-3 font-medium text-snow">
                    {spot.name}
                  </span>
                </div>
                <span className="figure text-xs text-asphalt">
                  {TYPE_LABELS[spot.type]} &middot; {spot.state} &middot; {spot.min_days}+ days
                </span>
              </Link>
            ))}
          </div>
        </Reveal>
      )}
    </section>
  );
}
