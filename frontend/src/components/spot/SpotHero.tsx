export default function SpotHero({
  name,
  blurb,
  highlights,
  elevationFt,
  bestTimeToVisit,
}: {
  name: string;
  blurb: string;
  highlights?: string;
  elevationFt?: number | null;
  bestTimeToVisit?: string;
}) {
  const description = highlights || blurb;

  return (
    <div className="mb-8">
      <h1 className="text-3xl font-semibold text-pine">{name}</h1>
      {description && <p className="mt-2 max-w-2xl text-asphalt">{description}</p>}
      {(elevationFt || bestTimeToVisit) && (
        <dl className="mt-4 flex flex-wrap gap-x-8 gap-y-2 text-sm">
          {elevationFt && (
            <div className="flex items-baseline gap-1.5">
              <dt className="text-asphalt">Elevation</dt>
              <dd className="figure text-ink">{elevationFt.toLocaleString()} ft</dd>
            </div>
          )}
          {bestTimeToVisit && (
            <div className="flex items-baseline gap-1.5">
              <dt className="text-asphalt">Best time to visit</dt>
              <dd className="text-ink">{bestTimeToVisit}</dd>
            </div>
          )}
        </dl>
      )}
    </div>
  );
}
