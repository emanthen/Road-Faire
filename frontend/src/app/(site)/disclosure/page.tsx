import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Affiliate disclosure - Roadfare",
  description: "How Roadfare makes money and how that affects what we show you.",
};

/** FTC disclosure (BUILD_PROMPT §7) — required before any /go/ links ship in Phase 6. */
export default function DisclosurePage() {
  return (
    <section className="max-w-2xl px-6 py-16">
      <h1 className="text-2xl font-semibold text-pine">Affiliate disclosure</h1>
      <div className="mt-6 flex flex-col gap-4 text-ink">
        <p>
          Roadfare doesn&apos;t own any campervans, cars, hotels, campsites, or tours. We
          link out to partners who do, and when you book through one of those links, we
          earn a commission. You pay the same price either way. The commission comes
          out of what the partner would otherwise spend on advertising, not out of your
          pocket.
        </p>
        <p>
          Every outbound link on Roadfare routes through a redirect at{" "}
          <code className="figure text-sm">/go/</code> so we can track which
          recommendations are actually useful. That redirect is the only thing that
          changes. The destination is always the real partner site, at the real price.
        </p>
        <p>
          We choose partners based on whether we&apos;d actually recommend them, not
          based on which one pays the highest commission. If a fee or rule changes, we
          update the number, not the recommendation.
        </p>
        <p className="text-sm text-asphalt">
          This disclosure follows FTC guidelines on affiliate marketing (16 CFR Part 255).
        </p>
      </div>
    </section>
  );
}
