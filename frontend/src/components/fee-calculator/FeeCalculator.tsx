"use client";

import { useState } from "react";
import ResidencyToggle from "@/components/fee-calculator/ResidencyToggle";
import ParkPicker from "@/components/fee-calculator/ParkPicker";
import { SURCHARGE_PARKS } from "@/lib/parks";
import PartySizeInput from "@/components/fee-calculator/PartySizeInput";
import ResultPanel from "@/components/fee-calculator/ResultPanel";
import { useFeeCalculator } from "@/hooks/useFeeCalculator";
import { trackFeeCalculated } from "@/lib/analytics";

// Standard vehicle entrance fee assumed per park when the visitor hasn't told us
// otherwise. Real per-park figures come from apps.catalog.SpotCost once a spot is
// selected from the live catalog (Phase 4); this tool works standalone before that.
const ASSUMED_VEHICLE_FEE = "35.00";

export default function FeeCalculator() {
  const [selectedSlugs, setSelectedSlugs] = useState<string[]>([]);
  const [isUsResident, setIsUsResident] = useState(false);
  const [adults, setAdults] = useState(2);
  const [children, setChildren] = useState(0);

  const mutation = useFeeCalculator();

  function handleCalculate() {
    if (selectedSlugs.length === 0) return;
    const parks = selectedSlugs.map((slug) => {
      const park = SURCHARGE_PARKS.find((p) => p.slug === slug)!;
      return {
        slug: park.slug,
        name: park.name,
        standard_fee: ASSUMED_VEHICLE_FEE,
        fee_type: "vehicle" as const,
      };
    });
    mutation.mutate(
      { parks, adults, children, is_us_resident: isUsResident },
      { onSuccess: () => trackFeeCalculated() }
    );
  }

  return (
    <div className="max-w-2xl">
      <div className="flex flex-col gap-6">
        <ParkPicker selected={selectedSlugs} onChange={setSelectedSlugs} />
        <ResidencyToggle isUsResident={isUsResident} onChange={setIsUsResident} />
        <PartySizeInput
          adults={adults}
          childrenCount={children}
          onAdultsChange={setAdults}
          onChildrenChange={setChildren}
        />
        <button
          type="button"
          onClick={handleCalculate}
          disabled={selectedSlugs.length === 0 || mutation.isPending}
          className="min-h-11 self-start rounded bg-pine px-7 py-2.5 font-medium text-snow hover:bg-ink active:scale-[0.98] disabled:opacity-40 disabled:hover:bg-pine disabled:active:scale-100"
        >
          {mutation.isPending ? "Calculating…" : "Calculate"}
        </button>
        {mutation.isError && (
          <p className="text-signal">Couldn&apos;t calculate that. Try again.</p>
        )}
      </div>
      {mutation.data && <ResultPanel breakdown={mutation.data} />}
    </div>
  );
}
