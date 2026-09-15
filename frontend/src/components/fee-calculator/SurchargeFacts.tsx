const FACTS = [
  { value: "$100", label: "Non-resident surcharge, per adult over 16" },
  { value: "11", label: "National parks that charge it" },
  { value: "$250", label: "Annual pass, non-resident" },
  { value: "$80", label: "Annual pass, US resident" },
] as const;

export default function SurchargeFacts() {
  return (
    <div className="lg:pt-9">
      <h2 className="text-sm font-medium text-ink">The fee most planners skip</h2>
      <dl className="mt-4 flex flex-col divide-y divide-asphalt/20 border-t border-asphalt/20">
        {FACTS.map((fact) => (
          <div key={fact.label} className="flex items-baseline justify-between gap-6 py-3">
            <dt className="text-sm text-asphalt">{fact.label}</dt>
            <dd className="figure shrink-0 text-lg text-ink">{fact.value}</dd>
          </div>
        ))}
      </dl>
    </div>
  );
}
