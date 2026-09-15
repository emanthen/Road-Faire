import type { Metadata } from "next";
import PageHero from "@/components/layout/PageHero";
import FeeCalculator from "@/components/fee-calculator/FeeCalculator";

export const metadata: Metadata = {
  title: "National park fee calculator - Roadfare",
  description:
    "Work out the non-resident national park surcharge for your trip, and whether an annual pass beats paying as you go.",
};

export default function NationalParkFeeCalculatorPage() {
  return (
    <section className="px-6 py-16">
      <PageHero
        title="National park fee calculator"
        description="Pick your parks, party size, and residency status to see the real total, including the $100 non-resident surcharge most planners miss."
        imageSrc="/images/parks/grca.jpg"
        imageAlt="Rafters on the Colorado River beneath the canyon walls, Grand Canyon National Park"
      />
      <div className="relative border border-asphalt/20 p-6 sm:p-10">
        <FeeCalculator />
      </div>
    </section>
  );
}
