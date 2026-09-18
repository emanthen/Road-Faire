"use client";

import { useEffect } from "react";
import { GeoJSONSource, LngLatBounds } from "maplibre-gl";
import { useMap } from "@/components/map/MapContext";
import SpotMarker from "@/components/map/SpotMarker";
import type { Loop } from "@/types/planner";

const ROUTE_SOURCE_ID = "trip-route";
const ROUTE_LAYER_ID = "trip-route-line";

/**
 * Draws a trip's stops on a live map: a marker per stop, and a line connecting them
 * in order. The line is a straight-line path between consecutive stops, not a routed
 * road polyline — apps.planner.engine.candidates doesn't have real drive geometry yet
 * (it uses straight-line distance; see its ponytail note on DriveTime), and connecting
 * the dots honestly beats faking a road-following route the data doesn't support.
 *
 * Reads the map instance from MapContext (set by an ancestor SpotMap).
 */
export default function RouteLayer({ loop }: { loop: Loop }) {
  const map = useMap();

  useEffect(() => {
    if (!map || loop.stops.length < 2) return;

    const coordinates: [number, number][] = loop.stops.map((stop) => [
      stop.longitude,
      stop.latitude,
    ]);
    const geojson: GeoJSON.Feature<GeoJSON.LineString> = {
      type: "Feature",
      properties: {},
      geometry: { type: "LineString", coordinates },
    };

    const existingSource = map.getSource(ROUTE_SOURCE_ID) as GeoJSONSource | undefined;
    if (existingSource) {
      existingSource.setData(geojson);
    } else {
      map.addSource(ROUTE_SOURCE_ID, { type: "geojson", data: geojson });
      map.addLayer({
        id: ROUTE_LAYER_ID,
        type: "line",
        source: ROUTE_SOURCE_ID,
        layout: { "line-join": "round", "line-cap": "round" },
        paint: { "line-color": "#24503F", "line-width": 3, "line-dasharray": [2, 2] },
      });
    }

    const bounds = coordinates.reduce(
      (b, coord) => b.extend(coord),
      new LngLatBounds(coordinates[0], coordinates[0])
    );
    map.fitBounds(bounds, { padding: 40, maxZoom: 10 });

    return () => {
      if (map.getLayer(ROUTE_LAYER_ID)) map.removeLayer(ROUTE_LAYER_ID);
      if (map.getSource(ROUTE_SOURCE_ID)) map.removeSource(ROUTE_SOURCE_ID);
    };
  }, [map, loop]);

  return (
    <>
      {loop.stops.map((stop) => (
        <SpotMarker key={stop.slug} latitude={stop.latitude} longitude={stop.longitude} label={stop.name} />
      ))}
    </>
  );
}
