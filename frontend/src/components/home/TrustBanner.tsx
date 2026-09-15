export default function TrustBanner() {
  return (
    <div className="grid gap-6 border-y border-asphalt/20 py-10 sm:grid-cols-[auto_1fr] sm:items-center sm:gap-10">
      <div className="flex items-baseline gap-3 sm:flex-col sm:items-start sm:gap-0">
        <span className="figure text-5xl leading-none text-pine sm:text-6xl">11</span>
        <span className="text-xs uppercase tracking-wide text-asphalt sm:mt-1">
          parks in the catalog
        </span>
      </div>
      <p className="max-w-2xl text-lg leading-relaxed text-ink sm:border-l sm:border-asphalt/20 sm:pl-10">
        Every fee and rule in the catalog is either pulled from an official source or
        flagged for manual review. We don&apos;t guess at numbers that cost you money.
      </p>
    </div>
  );
}
