const STEPS = [
  {
    title: "Tell us your trip",
    body: "Departure airport, dates, party size, and which parks you're visiting.",
  },
  {
    title: "We cost every fee",
    body: "Entry, the non-resident surcharge, fuel, lodging, and food, itemised in Decimal math, never estimated.",
  },
  {
    title: "Compare and decide",
    body: "See whether an annual pass beats paying as you go before you book anything.",
  },
] as const;

export default function HowItWorks() {
  return (
    <div>
      <h2 className="text-2xl font-semibold text-pine">How it works</h2>
      <div className="mt-8 flex flex-col divide-y divide-asphalt/20 border-t border-asphalt/20">
        {STEPS.map((step, i) => (
          <div key={step.title} className="grid gap-4 py-8 sm:grid-cols-[auto_1fr] sm:gap-10">
            <span className="figure text-6xl leading-none text-asphalt/25 sm:text-7xl">
              {String(i + 1).padStart(2, "0")}
            </span>
            <div className="self-center">
              <h3 className="font-medium text-ink">{step.title}</h3>
              <p className="mt-1.5 max-w-md text-sm leading-relaxed text-asphalt">{step.body}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
