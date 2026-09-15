import type { Metadata } from "next";
import PageHero from "@/components/layout/PageHero";
import VendorsGrid from "@/components/vendors/VendorsGrid";
import { fetchPartners } from "@/lib/api";

export const dynamic = "force-dynamic";

export const metadata: Metadata = {
  title: "Vendors - Roadfare",
  description: "Real campervan, bicycle, and camping-gear rental vendors near the road.",
};

export default async function VendorsPage() {
  const partners = await fetchPartners();

  return (
    <section className="px-6 py-16">
      <PageHero
        title="Vendors"
        description="Real businesses we've found for gear Roadfare doesn't sell itself — campervans, bikes, tents."
        imageSrc="/images/parks/acad.jpg"
        imageAlt="A park ranger checking in a vehicle at Acadia National Park"
      />
      <p className="-mt-6 mb-8 max-w-xl text-sm text-asphalt">
        These are informational listings: Roadfare has no commission relationship with
        any vendor below, we just link to their own site.
      </p>

      {partners.length === 0 ? (
        <p className="mt-10 text-asphalt">No vendors listed yet. Check back soon.</p>
      ) : (
        <VendorsGrid partners={partners} />
      )}
    </section>
  );
}
