"use client";

import { SURCHARGE_PARKS } from "@/lib/parks";

export default function ParkPicker({
  selected,
  onChange,
}: {
  selected: string[];
  onChange: (slugs: string[]) => void;
}) {
  function toggle(slug: string) {
    onChange(
      selected.includes(slug) ? selected.filter((s) => s !== slug) : [...selected, slug]
    );
  }

  return (
    <fieldset>
      <legend className="mb-3 text-sm font-medium text-ink">Which parks are you visiting?</legend>
      <div className="flex flex-wrap gap-2">
        {SURCHARGE_PARKS.map((park) => {
          const isSelected = selected.includes(park.slug);
          return (
            <button
              key={park.slug}
              type="button"
              aria-pressed={isSelected}
              onClick={() => toggle(park.slug)}
              className={`min-h-11 rounded border px-3.5 py-2 text-sm font-medium active:scale-[0.98] ${
                isSelected
                  ? "border-pine bg-pine text-snow"
                  : "border-asphalt/30 text-ink hover:border-pine hover:bg-pine/5"
              }`}
            >
              {park.name}
            </button>
          );
        })}
      </div>
    </fieldset>
  );
}
