"use client";

/**
 * MapLibre + Protomaps (PROJECT_STRUCTURE.md). No hosted PMTiles basemap is configured
 * yet (NEXT_PUBLIC_MAPLIBRE_STYLE_URL is blank) — that's a real infra dependency (a
 * hosted tile source), not something to fake with a placeholder tile URL. Renders the
 * container + coordinates so the page layout is real; the actual map wires in once a
 * style URL exists.
 */
export default function SpotMap({
  latitude,
  longitude,
}: {
  latitude: number;
  longitude: number;
}) {
  const styleUrl = process.env.NEXT_PUBLIC_MAPLIBRE_STYLE_URL;

  if (!styleUrl) {
    return (
      <div className="flex h-64 items-center justify-center rounded border border-asphalt/20 bg-snow text-sm text-asphalt">
        Map not configured yet ({latitude.toFixed(4)}, {longitude.toFixed(4)})
      </div>
    );
  }

  // Real MapLibre wiring lands once NEXT_PUBLIC_MAPLIBRE_STYLE_URL is set.
  return null;
}
