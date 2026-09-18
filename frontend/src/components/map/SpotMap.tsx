"use client";

import { useEffect, useRef, useState } from "react";
import { Map as MapLibreMap, NavigationControl } from "maplibre-gl";
import "maplibre-gl/dist/maplibre-gl.css";
import { MapContext } from "@/components/map/MapContext";

/**
 * MapLibre + Protomaps (PROJECT_STRUCTURE.md). Renders nothing until
 * NEXT_PUBLIC_MAPLIBRE_STYLE_URL is set — that's a real infra dependency (a hosted
 * PMTiles tile source), not something to fake with a placeholder tile URL — falling
 * back to a labeled placeholder so the page layout is still real.
 *
 * `children` are ordinary JSX (SpotMarker, RouteLayer, ...) that read the live map
 * instance via MapContext rather than a render-prop — a render-prop's function value
 * isn't serializable across the server/client boundary, which breaks the moment this
 * is used directly from a Server Component (e.g. the spot detail page).
 */
export default function SpotMap({
  latitude,
  longitude,
  zoom = 9,
  children,
}: {
  latitude: number;
  longitude: number;
  zoom?: number;
  children?: React.ReactNode;
}) {
  const styleUrl = process.env.NEXT_PUBLIC_MAPLIBRE_STYLE_URL;
  const containerRef = useRef<HTMLDivElement>(null);
  const [map, setMap] = useState<MapLibreMap | null>(null);

  useEffect(() => {
    if (!styleUrl || !containerRef.current) return;

    const instance = new MapLibreMap({
      container: containerRef.current,
      style: styleUrl,
      center: [longitude, latitude],
      zoom,
    });
    instance.addControl(new NavigationControl(), "top-right");
    instance.on("load", () => setMap(instance));

    return () => {
      instance.remove();
      setMap(null);
    };
    // Re-centering an existing map on prop changes is a separate concern from
    // creating it — this effect only ever runs once per style URL.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [styleUrl]);

  if (!styleUrl) {
    return (
      <div className="flex h-64 items-center justify-center rounded border border-asphalt/20 bg-snow text-sm text-asphalt">
        Map not configured yet ({latitude.toFixed(4)}, {longitude.toFixed(4)})
      </div>
    );
  }

  return (
    <>
      <div
        ref={containerRef}
        className="h-64 w-full overflow-hidden rounded border border-asphalt/20"
      />
      <MapContext.Provider value={map}>{children}</MapContext.Provider>
    </>
  );
}
