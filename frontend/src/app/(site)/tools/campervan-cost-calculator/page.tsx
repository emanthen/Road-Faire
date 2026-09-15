import type { Metadata } from "next";
import PageHero from "@/components/layout/PageHero";
import CampervanCostCalculator from "@/components/vehicle/CampervanCostCalculator";

export const metadata: Metadata = {
  title: "Campervan cost calculator - Roadfare",
  description:
    "The real cost of a campervan rental, mileage overage and all, not just the nightly rate.",
};

export default function CampervanCostCalculatorPage() {
  return (
    <section className="px-6 py-16">
      <PageHero
        title="Campervan cost calculator"
        description="Rental listings quote a nightly rate. They rarely mention mileage overage, prep fees, or one-way charges until checkout. Enter your rental's real terms and see the total."
        imageSrc="/images/parks/acad.jpg"
        imageAlt="A park ranger checking in a vehicle at Acadia National Park"
      />

      <div className="relative border border-asphalt/20 p-6 sm:p-10">
        <CampervanCostCalculator />
      </div>
    </section>
  );
}
