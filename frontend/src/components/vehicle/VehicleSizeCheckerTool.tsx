"use client";

import { useState } from "react";
import SizeChecker from "@/components/vehicle/SizeChecker";
import type { SpotListItem } from "@/types/api";

export default function VehicleSizeCheckerTool({ spots }: { spots: SpotListItem[] }) {
  const [selectedSlug, setSelectedSlug] = useState("");

  return (
    <div className="flex flex-col gap-6">
      <label className="flex flex-col gap-1.5 text-sm font-medium text-ink">
        Which spot are you visiting?
        <select
          value={selectedSlug}
          onChange={(e) => setSelectedSlug(e.target.value)}
          className="min-h-11 max-w-sm rounded border border-asphalt/30 px-3 py-2 text-ink"
        >
          <option value="">Choose a spot</option>
          {spots.map((spot) => (
            <option key={spot.slug} value={spot.slug}>
              {spot.name}
            </option>
          ))}
        </select>
      </label>

      {selectedSlug && <SizeChecker key={selectedSlug} spotSlug={selectedSlug} />}
    </div>
  );
}
