import { formatUSD } from "@/lib/money";

/** The sodium accent — costs the user didn't expect (BUILD_PROMPT §5). One per screen.
 * The accent lives in the chip's border/fill, not the text: sodium (#E8A33D) on this
 * light background is ~1.9:1 contrast, well under WCAG AA's 4.5:1 minimum for text. */
export default function SurchargeCallout({ amountCents }: { amountCents: number }) {
  if (amountCents === 0) return null;

  return (
    <p className="reveal rounded border border-sodium/40 bg-sodium/10 px-4 py-3 text-ink">
      You&apos;ll pay{" "}
      <span className="figure font-semibold text-ink">{formatUSD(amountCents)}</span> in
      non-resident surcharges.
    </p>
  );
}
