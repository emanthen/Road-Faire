import type { Metadata } from "next";
import Link from "next/link";
import PageHero from "@/components/layout/PageHero";
import Reveal from "@/components/layout/Reveal";

export const metadata: Metadata = {
  title: "About - Roadfare",
  description: "Why Roadfare exists and how it makes money.",
};

export default function AboutPage() {
  return (
    <section className="px-6 py-16">
      <PageHero
        title="About Roadfare"
        description="Most trip planners quote a park entry fee and stop there. We don't."
        imageSrc="/images/parks/seki.jpg"
        imageAlt="Inside a visitor center at Sequoia & Kings Canyon National Parks"
      />

      <Reveal>
        <div className="flex max-w-2xl flex-col gap-4 text-ink">
          <p>
            Eleven US national parks charge non-US residents a $100 per-adult surcharge
            on top of the standard entry fee. It rarely shows up until you&apos;re
            already at the gate. Roadfare surfaces that cost upfront, works out whether
            an annual pass beats paying as you go, and builds full road-trip itineraries
            with every fee itemised: entry, fuel, lodging, and food.
          </p>
          <p>
            Every fee and rule in the catalog is either pulled live from an official
            source (the National Park Service, Recreation.gov, OpenStreetMap) or
            flagged for manual review. We don&apos;t guess at numbers that cost you
            money.
          </p>
          <p>
            Roadfare earns a commission on some bookings made through partner links. It
            never changes which recommendation you see. See our{" "}
            <Link href="/disclosure" className="text-pine underline">
              full disclosure
            </Link>
            .
          </p>
        </div>
      </Reveal>
    </section>
  );
}
