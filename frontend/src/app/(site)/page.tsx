import FeeCalculator from "@/components/fee-calculator/FeeCalculator";
import SurchargeFacts from "@/components/fee-calculator/SurchargeFacts";
import ClosingCtas from "@/components/home/ClosingCtas";
import Hero from "@/components/home/Hero";
import HowItWorks from "@/components/home/HowItWorks";
import ParksGrid from "@/components/home/ParksGrid";
import TrustBanner from "@/components/home/TrustBanner";
import Reveal from "@/components/layout/Reveal";

/** HOME — a real photo hero carries the headline, then the fee calculator (the actual
 * product) follows directly below it, framed as the instrument it is. */
export default function HomePage() {
  return (
    <div className="flex flex-col gap-20 pb-12 sm:gap-24 sm:pb-16">
      <Hero />

      <section id="calculator" className="px-6">
        <div className="relative border border-asphalt/20 p-6 sm:p-10">
          <span className="figure absolute right-6 top-6 text-xs text-asphalt/60 sm:right-10 sm:top-10">
            001
          </span>
          <h2 className="text-sm font-medium text-ink">Try it with your own trip</h2>
          <div className="mt-8 grid gap-10 lg:grid-cols-5 lg:gap-16">
            <div className="lg:col-span-3">
              <FeeCalculator />
            </div>
            <div className="lg:col-span-2">
              <SurchargeFacts />
            </div>
          </div>
        </div>
      </section>

      <section className="px-6">
        <Reveal>
          <HowItWorks />
        </Reveal>
      </section>

      <section className="px-6">
        <Reveal>
          <ParksGrid />
        </Reveal>
      </section>

      <section className="px-6">
        <Reveal>
          <TrustBanner />
        </Reveal>
      </section>

      <section className="px-6">
        <Reveal>
          <ClosingCtas />
        </Reveal>
      </section>
    </div>
  );
}
