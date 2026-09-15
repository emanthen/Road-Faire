import Image from "next/image";
import Link from "next/link";
import { SURCHARGE_PARKS } from "@/lib/parks";

/** Real NPS photos, downloaded from each park's own nps.gov homepage (public domain —
 * works of the US federal government, 17 U.S.C. § 105). Self-hosted in public/images/parks
 * rather than hotlinked so the site doesn't depend on nps.gov's own CDN paths staying put. */
function photoUrl(slug: string): string {
  return `/images/parks/${slug}.jpg`;
}

export default function ParksGrid() {
  return (
    <div>
      <div className="flex flex-wrap items-baseline justify-between gap-x-8 gap-y-2">
        <h2 className="text-2xl font-semibold text-pine">The 11 parks that charge it</h2>
        <span className="figure text-sm text-asphalt">11 parks &middot; $100 each</span>
      </div>
      <p className="mt-2 max-w-xl text-asphalt">
        Every one of these charges non-US residents $100 per adult on top of the
        standard entry fee.
      </p>

      <div className="mt-8 grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-5">
        {SURCHARGE_PARKS.map((park) => (
          <Link
            key={park.slug}
            href={`/spots/${park.slug}`}
            className="group relative aspect-[3/4] overflow-hidden rounded-xl bg-asphalt/10"
          >
            <Image
              src={photoUrl(park.slug)}
              alt={`NPS photo of ${park.name}`}
              fill
              sizes="(min-width: 1024px) 20vw, (min-width: 640px) 33vw, 50vw"
              className="object-cover transition-transform duration-500 group-hover:scale-105"
            />
            {/* A real legibility aid, not decoration: the photo's brightness varies,
                white text needs this to stay readable everywhere. */}
            <div className="absolute inset-0 bg-gradient-to-t from-ink/80 via-ink/0 to-ink/0" />
            <span className="absolute bottom-3 left-3 right-3 font-medium text-snow">
              {park.name}
            </span>
          </Link>
        ))}
      </div>
    </div>
  );
}
