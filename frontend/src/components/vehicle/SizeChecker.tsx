"use client";

import { useState } from "react";
import FitBadge from "@/components/vehicle/FitBadge";
import { useSizeCheck } from "@/hooks/useSizeCheck";

function today(): string {
  return new Date().toISOString().slice(0, 10);
}

export default function SizeChecker({ spotSlug }: { spotSlug: string }) {
  const mutation = useSizeCheck();
  const [lengthFt, setLengthFt] = useState("");
  const [heightFt, setHeightFt] = useState("");
  const [travelDate, setTravelDate] = useState(today);

  const isValid = lengthFt !== "" && heightFt !== "" && travelDate !== "";

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!isValid) return;
    mutation.mutate({
      length_ft: lengthFt,
      height_ft: heightFt,
      spot_slug: spotSlug,
      travel_date: travelDate,
    });
  }

  return (
    <form onSubmit={handleSubmit} className="flex max-w-sm flex-col gap-4">
      <div className="flex gap-4">
        <label className="flex flex-col gap-1.5 text-sm font-medium text-ink">
          Length (ft)
          <input
            type="number"
            min={0}
            step={0.1}
            inputMode="decimal"
            value={lengthFt}
            onChange={(e) => setLengthFt(e.target.value)}
            className="figure min-h-11 w-24 rounded border border-asphalt/30 px-3 py-2 text-ink hover:border-pine/60"
          />
        </label>
        <label className="flex flex-col gap-1.5 text-sm font-medium text-ink">
          Height (ft)
          <input
            type="number"
            min={0}
            step={0.1}
            inputMode="decimal"
            value={heightFt}
            onChange={(e) => setHeightFt(e.target.value)}
            className="figure min-h-11 w-24 rounded border border-asphalt/30 px-3 py-2 text-ink hover:border-pine/60"
          />
        </label>
      </div>

      <label className="flex flex-col gap-1.5 text-sm font-medium text-ink">
        Travel date
        <input
          type="date"
          value={travelDate}
          onChange={(e) => setTravelDate(e.target.value)}
          className="min-h-11 w-44 rounded border border-asphalt/30 px-3 py-2 text-ink hover:border-pine/60"
        />
      </label>

      <button
        type="submit"
        disabled={!isValid || mutation.isPending}
        className="min-h-11 self-start rounded bg-pine px-6 py-2.5 font-medium text-snow hover:bg-ink active:scale-[0.98] disabled:opacity-40"
      >
        {mutation.isPending ? "Checking…" : "Check my vehicle"}
      </button>

      {mutation.isError && <p className="text-signal">{mutation.error.message}</p>}

      {mutation.isSuccess && (
        <div className="flex flex-col gap-2 border-t border-asphalt/20 pt-4">
          <FitBadge status={mutation.data.status} />
          {mutation.data.reasons.length > 0 && (
            <ul className="flex flex-col gap-1 text-sm text-asphalt">
              {mutation.data.reasons.map((reason) => (
                <li key={reason}>{reason}</li>
              ))}
            </ul>
          )}
        </div>
      )}
    </form>
  );
}
