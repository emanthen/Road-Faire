"use client";

import { useEffect } from "react";
import { Marker, Popup } from "maplibre-gl";
import { useMap } from "@/components/map/MapContext";

/** One pin + label popup on a live map — the single-point case RouteLayer's per-stop
 * markers also reduce to, so both share this instead of duplicating marker setup.
 * Reads the map instance from MapContext (set by an ancestor SpotMap), so it renders
 * nothing until that map has loaded. */
export default function SpotMarker({
  latitude,
  longitude,
  label,
}: {
  latitude: number;
  longitude: number;
  label?: string;
}) {
  const map = useMap();

  useEffect(() => {
    if (!map) return;

    const marker = new Marker({ color: "#24503F" }).setLngLat([longitude, latitude]);
    if (label) {
      marker.setPopup(new Popup({ offset: 12 }).setText(label));
    }
    marker.addTo(map);
    return () => {
      marker.remove();
    };
  }, [map, latitude, longitude, label]);

  return null;
}
