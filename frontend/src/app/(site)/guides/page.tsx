import type { Metadata } from "next";
import Link from "next/link";
import PageHero from "@/components/layout/PageHero";
import { fetchPages } from "@/lib/api";

export const dynamic = "force-dynamic";

export const metadata: Metadata = {
  title: "Travel stories - Roadfare",
  description: "Real trip write-ups and destination guides for US road trips.",
};

export default async function GuidesPage() {
  const { results } = await fetchPages();

  return (
    <section className="px-6 py-16">
      <PageHero
        title="Travel stories"
        description="Destination guides and trip write-ups, grounded in the same real fees and rules the planner uses."
        imageSrc="/images/parks/ever.jpg"
        imageAlt="Wetlands and grasses in Everglades National Park"
      />

      {results.length === 0 ? (
        <p className="mt-10 text-asphalt">No stories published yet. Check back soon.</p>
      ) : (
        <ul className="mt-8 flex flex-col divide-y divide-asphalt/20 border-t border-asphalt/20">
          {results.map((page) => (
            <li key={page.slug}>
              <Link
                href={`/guides/${page.slug}`}
                className="block py-4 font-medium text-ink hover:text-pine"
              >
                {page.title}
              </Link>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
