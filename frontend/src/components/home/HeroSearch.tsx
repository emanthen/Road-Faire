"use client";

import { useState } from "react";
import { SURCHARGE_PARKS } from "@/lib/parks";

/** A real search-first entry point into the calculator below — not a decorative
 * search box. There's no per-park pre-fill wired up yet (the calculator's own park
 * picker handles that), so this scrolls to it rather than pretending to deep-link. */
export default function HeroSearch() {
  const [slug, setSlug] = useState("");

  function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    document.getElementById("calculator")?.scrollIntoView({ behavior: "smooth" });
  }

  return (
    <form
      onSubmit={handleSubmit}
      className="flex flex-col overflow-hidden rounded-full border border-asphalt/20 bg-snow shadow-sm sm:flex-row sm:items-center"
    >
      <label className="flex flex-1 flex-col gap-0.5 px-6 py-3">
        <span className="text-xs font-medium text-asphalt">Which park?</span>
        <select
          value={slug}
          onChange={(e) => setSlug(e.target.value)}
          className="min-h-6 bg-transparent text-sm text-ink outline-none"
        >
          <option value="">Search 11 parks</option>
          {SURCHARGE_PARKS.map((park) => (
            <option key={park.slug} value={park.slug}>
              {park.name}
            </option>
          ))}
        </select>
      </label>
      <button
        type="submit"
        className="m-1.5 flex min-h-11 items-center justify-center rounded-full bg-sodium px-7 font-medium text-ink hover:bg-snow hover:ring-1 hover:ring-inset hover:ring-sodium active:scale-[0.98]"
      >
        Check the cost
      </button>
    </form>
  );
}
