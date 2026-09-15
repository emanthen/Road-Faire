import HeroCollage from "@/components/home/HeroCollage";
import HeroSearch from "@/components/home/HeroSearch";

/** Text panel + a tilted photo collage, rather than one full-bleed background photo —
 * the collage shows nine of the real park photos already in the catalog instead of
 * just one, and reads as a considered layout rather than a stock hero banner. */
export default function Hero() {
  return (
    <section className="w-screen bg-pine" style={{ marginInline: "calc(50% - 50vw)" }}>
      <div className="mx-auto grid max-w-[1600px] gap-10 px-6 py-16 sm:grid-cols-2 sm:items-center sm:gap-16 sm:py-24">
        <div className="text-snow">
          <h1 className="text-4xl font-bold leading-[1.05] tracking-tight sm:text-6xl">
            Know the real cost before you book.
          </h1>
          <p className="mt-5 max-w-lg text-base leading-relaxed text-snow/85 sm:text-lg">
            Non-US residents pay a $100 per-person surcharge at 11 national parks. We
            tell you whether that&apos;s cheaper than an annual pass, before you book
            anything.
          </p>
          <div className="mt-8 max-w-md">
            <HeroSearch />
          </div>
          <p className="mt-5 flex items-baseline gap-2">
            <span className="figure text-2xl text-sodium">$100</span>
            <span className="text-xs text-snow/80">per adult &middot; 11 parks</span>
          </p>
        </div>

        <HeroCollage />
      </div>
    </section>
  );
}
