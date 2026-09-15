import Link from "next/link";
import { notFound } from "next/navigation";
import { ApiError, fetchSpot } from "@/lib/api";
import { breadcrumbJsonLd, touristAttractionJsonLd } from "@/lib/seo";

const TABS = [
  { href: "", label: "Overview" },
  { href: "/cost", label: "Cost" },
  { href: "/best-time-to-visit", label: "Best time to visit" },
  { href: "/reservations", label: "Reservations" },
  { href: "/campervan", label: "Campervan" },
];

export default async function SpotLayout({
  children,
  params,
}: {
  children: React.ReactNode;
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
    <div className="px-6 py-16">
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify([
            touristAttractionJsonLd(spot),
            breadcrumbJsonLd([
              { name: "Spots", url: "/spots" },
              { name: spot.name, url: `/spots/${spot.slug}` },
            ]),
          ]),
        }}
      />
      <nav className="mb-8 flex gap-4 border-b border-asphalt/20 text-sm">
        {TABS.map((tab) => (
          <Link
            key={tab.href}
            href={`/spots/${slug}${tab.href}`}
            className="border-b-2 border-transparent py-2 text-asphalt hover:border-pine"
          >
            {tab.label}
          </Link>
        ))}
      </nav>
      {children}
    </div>
  );
}
