import { createContext, useContext } from "react";
import type { Map as MapLibreMap } from "maplibre-gl";

/**
 * Exposes SpotMap's live maplibregl.Map instance to descendants (SpotMarker,
 * RouteLayer) via context rather than a render-prop. A render-prop's function value
 * isn't serializable across the server/client boundary, so it breaks the moment
 * SpotMap is used directly from a Server Component (e.g. the spot detail page) —
 * plain JSX children have no such restriction.
 */
export const MapContext = createContext<MapLibreMap | null>(null);

export function useMap(): MapLibreMap | null {
  return useContext(MapContext);
}
