import type { Metadata } from "next";
import Link from "next/link";
import PageHero from "@/components/layout/PageHero";
import TripForm from "@/components/planner/TripForm";

export const metadata: Metadata = {
  title: "Plan a trip - Roadfare",
  description: "Tell us where you're flying into and we'll cost out three trip options.",
};

export default function PlanPage() {
  return (
    <section className="px-6 py-16">
      <PageHero
        title="Plan a trip"
        description="Tell us where you're flying into, when, and your budget. We'll cost out three fully itemised options, day by day."
        imageSrc="/images/parks/yose.jpg"
        imageAlt="A backpacker approaching an alpine lake in Yosemite National Park"
      />
      <div className="relative max-w-xl border border-asphalt/20 p-6 sm:p-10">
        <TripForm />
        <p className="mt-6 text-sm text-asphalt">
          Not sure what to expect?{" "}
          <Link href="/trips" className="text-pine underline">
            See example trips
          </Link>
          .
        </p>
      </div>
    </section>
  );
}
