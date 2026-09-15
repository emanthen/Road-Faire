"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import RadioToggleGroup from "@/components/ui/RadioToggleGroup";
import { useTripPlan } from "@/hooks/useTripPlan";
import type { TripRequest } from "@/types/planner";

export default function TripForm() {
  const router = useRouter();
  const mutation = useTripPlan();

  const [form, setForm] = useState({
    origin_airport: "",
    start_date: "",
    end_date: "",
    adults: 2,
    children: 0,
    budget_usd: "2000",
    is_us_resident: true,
    vehicle_pref: "car" as TripRequest["vehicle_pref"],
    max_drive_hours_per_day: "4",
  });

  function update<K extends keyof typeof form>(key: K, value: (typeof form)[K]) {
    setForm((prev) => ({ ...prev, [key]: value }));
  }

  const isValid =
    form.origin_airport.length === 3 &&
    form.start_date !== "" &&
    form.end_date !== "" &&
    form.end_date > form.start_date;

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!isValid) return;
    mutation.mutate(
      { ...form, vibe_tags: [] },
      { onSuccess: (data) => router.push(`/plan/${data.id}`) }
    );
  }

  return (
    <form onSubmit={handleSubmit} className="flex max-w-xl flex-col gap-6">
      <label className="flex flex-col gap-1.5 text-sm font-medium text-ink">
        Departure airport (3-letter code)
        <input
          type="text"
          maxLength={3}
          value={form.origin_airport}
          onChange={(e) => update("origin_airport", e.target.value.toUpperCase())}
          className="min-h-11 w-24 rounded border border-asphalt/30 px-3 py-2 uppercase text-ink hover:border-pine/60"
          placeholder="JFK"
        />
      </label>

      <div className="flex gap-4">
        <label className="flex flex-col gap-1.5 text-sm font-medium text-ink">
          Start date
          <input
            type="date"
            value={form.start_date}
            onChange={(e) => update("start_date", e.target.value)}
            className="min-h-11 rounded border border-asphalt/30 px-3 py-2 text-ink hover:border-pine/60"
          />
        </label>
        <label className="flex flex-col gap-1.5 text-sm font-medium text-ink">
          End date
          <input
            type="date"
            value={form.end_date}
            onChange={(e) => update("end_date", e.target.value)}
            className="min-h-11 rounded border border-asphalt/30 px-3 py-2 text-ink hover:border-pine/60"
          />
        </label>
      </div>

      <div className="flex gap-4">
        <label className="flex flex-col gap-1.5 text-sm font-medium text-ink">
          Adults (16+)
          <input
            type="number"
            min={1}
            value={form.adults}
            onChange={(e) => update("adults", Math.max(1, Number(e.target.value)))}
            className="min-h-11 w-24 rounded border border-asphalt/30 px-3 py-2 text-ink figure hover:border-pine/60"
          />
        </label>
        <label className="flex flex-col gap-1.5 text-sm font-medium text-ink">
          Children (under 16)
          <input
            type="number"
            min={0}
            value={form.children}
            onChange={(e) => update("children", Math.max(0, Number(e.target.value)))}
            className="min-h-11 w-24 rounded border border-asphalt/30 px-3 py-2 text-ink figure hover:border-pine/60"
          />
        </label>
      </div>

      <label className="flex flex-col gap-1.5 text-sm font-medium text-ink">
        Budget (USD)
        <input
          type="number"
          min={0}
          value={form.budget_usd}
          onChange={(e) => update("budget_usd", e.target.value)}
          className="min-h-11 w-32 rounded border border-asphalt/30 px-3 py-2 text-ink figure hover:border-pine/60"
        />
      </label>

      <RadioToggleGroup
        legend="Are you a US resident?"
        value={form.is_us_resident}
        onChange={(value) => update("is_us_resident", value)}
        options={[
          { label: "US resident", value: true },
          { label: "Non-resident", value: false },
        ]}
      />

      <RadioToggleGroup
        legend="Vehicle"
        value={form.vehicle_pref}
        onChange={(value) => update("vehicle_pref", value)}
        optionClassName="capitalize"
        options={[
          { label: "car", value: "car" },
          { label: "van", value: "van" },
        ]}
      />

      <button
        type="submit"
        disabled={!isValid || mutation.isPending}
        className="min-h-11 self-start rounded bg-pine px-7 py-2.5 font-medium text-snow hover:bg-ink disabled:opacity-40"
      >
        {mutation.isPending ? "Planning…" : "Plan my trip"}
      </button>

      {mutation.isError && (
        <p className="text-signal">{mutation.error.message}</p>
      )}
    </form>
  );
}
