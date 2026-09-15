"use client";

import { useState } from "react";
import CostLine from "@/components/cost/CostLine";
import CostTable from "@/components/cost/CostTable";
import { useTrueCost } from "@/hooks/useTrueCost";
import { formatUSD } from "@/lib/money";

function NumberField({
  label,
  value,
  onChange,
  width = "w-28",
}: {
  label: string;
  value: string;
  onChange: (value: string) => void;
  width?: string;
}) {
  return (
    <label className="flex flex-col gap-1.5 text-sm font-medium text-ink">
      {label}
      <input
        type="number"
        min={0}
        step={0.01}
        inputMode="decimal"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className={`figure min-h-11 ${width} rounded border border-asphalt/30 px-3 py-2 text-ink hover:border-pine/60`}
      />
    </label>
  );
}

function toCents(decimalString: string): number {
  return Math.round(parseFloat(decimalString || "0") * 100);
}

export default function CampervanCostCalculator() {
  const mutation = useTrueCost();

  const [nights, setNights] = useState("4");
  const [plannedMiles, setPlannedMiles] = useState("");
  const [baseNightlyRate, setBaseNightlyRate] = useState("");
  const [includedMilesPerNight, setIncludedMilesPerNight] = useState("100");
  const [overageRatePerMile, setOverageRatePerMile] = useState("0");
  const [prepFee, setPrepFee] = useState("0");
  const [insurancePerNight, setInsurancePerNight] = useState("0");
  const [oneWayFee, setOneWayFee] = useState("0");
  const [generatorHours, setGeneratorHours] = useState("0");
  const [generatorRatePerHour, setGeneratorRatePerHour] = useState("0");
  const [hookupNights, setHookupNights] = useState("0");
  const [hookupPremiumPerNight, setHookupPremiumPerNight] = useState("0");

  const isValid = nights !== "" && plannedMiles !== "" && baseNightlyRate !== "";

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!isValid) return;
    mutation.mutate({
      nights: Number(nights),
      planned_miles: plannedMiles,
      base_nightly_rate: baseNightlyRate,
      included_miles_per_night: Number(includedMilesPerNight || 0),
      overage_rate_per_mile: overageRatePerMile || "0",
      prep_fee: prepFee || "0",
      insurance_per_night: insurancePerNight || "0",
      one_way: Number(oneWayFee || 0) > 0,
      one_way_fee: oneWayFee || "0",
      generator_hours: generatorHours || "0",
      generator_rate_per_hour: generatorRatePerHour || "0",
      hookup_nights: Number(hookupNights || 0),
      hookup_premium_per_night: hookupPremiumPerNight || "0",
    });
  }

  return (
    <form onSubmit={handleSubmit} className="flex max-w-xl flex-col gap-6">
      <div className="flex flex-wrap gap-4">
        <NumberField label="Nights" value={nights} onChange={setNights} width="w-20" />
        <NumberField label="Planned miles" value={plannedMiles} onChange={setPlannedMiles} />
        <NumberField
          label="Nightly rate (USD)"
          value={baseNightlyRate}
          onChange={setBaseNightlyRate}
        />
      </div>

      <div className="flex flex-wrap gap-4">
        <NumberField
          label="Miles included per night"
          value={includedMilesPerNight}
          onChange={setIncludedMilesPerNight}
        />
        <NumberField
          label="Overage rate ($/mi)"
          value={overageRatePerMile}
          onChange={setOverageRatePerMile}
        />
      </div>

      <details className="rounded border border-asphalt/20 p-4">
        <summary className="cursor-pointer text-sm font-medium text-ink">
          More costs (prep fee, insurance, one-way, generator, hookups)
        </summary>
        <div className="mt-4 flex flex-wrap gap-4">
          <NumberField label="Prep fee (USD)" value={prepFee} onChange={setPrepFee} />
          <NumberField
            label="Insurance ($/night)"
            value={insurancePerNight}
            onChange={setInsurancePerNight}
          />
          <NumberField label="One-way fee (USD)" value={oneWayFee} onChange={setOneWayFee} />
          <NumberField
            label="Generator hours"
            value={generatorHours}
            onChange={setGeneratorHours}
            width="w-20"
          />
          <NumberField
            label="Generator rate ($/hr)"
            value={generatorRatePerHour}
            onChange={setGeneratorRatePerHour}
          />
          <NumberField
            label="Hookup nights"
            value={hookupNights}
            onChange={setHookupNights}
            width="w-20"
          />
          <NumberField
            label="Hookup premium ($/night)"
            value={hookupPremiumPerNight}
            onChange={setHookupPremiumPerNight}
          />
        </div>
      </details>

      <button
        type="submit"
        disabled={!isValid || mutation.isPending}
        className="min-h-11 self-start rounded bg-pine px-7 py-2.5 font-medium text-snow hover:bg-ink active:scale-[0.98] disabled:opacity-40"
      >
        {mutation.isPending ? "Calculating…" : "Calculate true cost"}
      </button>

      {mutation.isError && <p className="text-signal">Couldn&apos;t calculate that. Try again.</p>}

      {mutation.isSuccess && (
        <div className="reveal mt-2">
          <CostTable>
            <CostLine label="Base rate" amountCents={toCents(mutation.data.base)} />
            <CostLine label="Mileage overage" amountCents={toCents(mutation.data.mileage_overage)} />
            <CostLine label="Prep fee" amountCents={toCents(mutation.data.prep_fee)} />
            <CostLine label="Insurance" amountCents={toCents(mutation.data.insurance)} />
            <CostLine label="One-way fee" amountCents={toCents(mutation.data.one_way_fee)} />
            <CostLine label="Generator" amountCents={toCents(mutation.data.generator)} />
            <CostLine label="Hookup premium" amountCents={toCents(mutation.data.hookup_premium)} />
          </CostTable>
          <div className="mt-2 flex items-baseline justify-between pt-2">
            <span className="font-medium text-ink">True cost</span>
            <span className="figure text-xl text-ink">
              {formatUSD(toCents(mutation.data.total))}
            </span>
          </div>
        </div>
      )}
    </form>
  );
}
