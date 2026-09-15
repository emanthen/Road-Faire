import type { Metadata } from "next";
import PageHero from "@/components/layout/PageHero";
import VehicleSizeCheckerTool from "@/components/vehicle/VehicleSizeCheckerTool";
import { fetchSpots } from "@/lib/api";

export const dynamic = "force-dynamic";

export const metadata: Metadata = {
  title: "Vehicle size checker - Roadfare",
  description: "Check whether your camper or RV fits the road and campground limits at a spot.",
};

export default async function VehicleSizeCheckerPage() {
  const { results } = await fetchSpots({});

  return (
    <section className="px-6 py-16">
      <PageHero
        title="Vehicle size checker"
        description="Enter your vehicle's length and height to see whether it fits a spot's road and campground limits."
        imageSrc="/images/parks/yell.jpg"
        imageAlt="Staff on a park road in Yellowstone National Park"
      />

      <div className="relative border border-asphalt/20 p-6 sm:p-10">
        {results.length === 0 ? (
          <p className="text-asphalt">
            No spots in the catalog yet, so there&apos;s nothing to check against.
          </p>
        ) : (
          <VehicleSizeCheckerTool spots={results} />
        )}
      </div>
    </section>
  );
}
