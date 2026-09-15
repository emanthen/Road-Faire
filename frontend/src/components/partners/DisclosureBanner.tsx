/**
 * FTC affiliate disclosure — must render above the fold on any page containing
 * affiliate links (BUILD_PROMPT §7). Real, legally-required copy, not placeholder text.
 */
export default function DisclosureBanner() {
  return (
    <p className="border-b border-asphalt/20 bg-snow px-6 py-3 text-sm text-asphalt">
      Roadfare earns a commission when you book through some links on this page, at no
      extra cost to you. We only link to partners we&apos;d recommend anyway. See our{" "}
      <a href="/disclosure" className="text-pine underline">
        full disclosure
      </a>
      .
    </p>
  );
}
