/** Mirrors apps.catalog.serializers.SpotDetailSerializer. Hand-written for now —
 * generated from the OpenAPI schema (/schema/) once codegen is wired up. */

export interface SpotCost {
  entry_vehicle: string | null;
  entry_person: string | null;
  parking: string | null;
  campsite_low: string | null;
  campsite_high: string | null;
  shuttle: string | null;
  source_url: string;
  verified_at: string | null;
}

export interface ReservationRule {
  kind: "timed_entry" | "vehicle" | "permit" | "shuttle" | "lottery";
  season_start: string | null;
  season_end: string | null;
  window_start: string | null;
  window_end: string | null;
  booking_url: string;
  processing_fee: string | null;
  notes: string;
  source_url: string;
  verified_at: string | null;
}

export interface VehicleLimit {
  max_length_ft: string | null;
  max_height_ft: string | null;
  max_weight_lb: number | null;
  effective_from: string | null;
  applies_to_roads: string[];
  source_url: string;
  verified_at: string | null;
}

export interface ClimateNormal {
  month: number;
  high_f: string;
  low_f: string;
  precip_in: string;
  snow_in: string;
}

export interface CrowdIndex {
  month: number;
  score: number;
}

export interface Activity {
  name: string;
  kind: "trail" | "tour";
  distance_mi: string | null;
  elevation_gain_ft: number | null;
  permit_required: boolean;
}

export type SpotType = "national_park" | "state_park" | "monument" | "forest" | "other";

export interface SpotListItem {
  slug: string;
  name: string;
  type: SpotType;
  state: string;
  min_days: number;
  vibe_tags: string[];
}

export interface SpotListResponse {
  next: string | null;
  previous: string | null;
  results: SpotListItem[];
}

export interface AuthUser {
  id: number;
  username: string;
  email: string;
  is_staff: boolean;
}

export interface AuthResponse {
  token: string;
  user: AuthUser;
}

export interface SiteSettings {
  site_name: string;
  tagline: string;
  logo_url: string;
  twitter_url: string;
  instagram_url: string;
  contact_email: string;
}

export interface ContentPage {
  slug: string;
  title: string;
  body: string;
}

export interface ContentPageListResponse {
  next: string | null;
  previous: string | null;
  results: ContentPage[];
}

export type OfferCategory =
  | "campervan"
  | "car"
  | "hotel"
  | "campsite"
  | "activity"
  | "insurance"
  | "bicycle"
  | "camping_gear";

export interface PartnerOffer {
  id: string;
  category: OfferCategory;
  description: string;
  price_note: string;
}

export interface Partner {
  name: string;
  slug: string;
  service_area: string;
  contact_phone: string;
  terms_note: string;
  rating: string | null;
  rating_count: number | null;
  rating_source: string;
  rating_url: string;
  offers: PartnerOffer[];
  verified_at: string | null;
}

export interface SpotAmenity {
  kind: "dump_station" | "water";
  longitude: number;
  latitude: number;
  source_url: string;
  verified_at: string | null;
}

export interface SpotPhoto {
  url: string;
  alt_text: string;
  caption: string;
  credit: string;
  is_primary: boolean;
}

export interface SpotDetail {
  slug: string;
  name: string;
  type: string;
  state: number;
  min_days: number;
  vibe_tags: string[];
  nearest_airports: string[];
  blurb: string;
  elevation_ft: number | null;
  best_time_to_visit: string;
  highlights: string;
  meta_title: string;
  meta_description: string;
  contact_phone: string;
  longitude: number;
  latitude: number;
  cost: SpotCost | null;
  reservation_rules: ReservationRule[];
  vehicle_limits: VehicleLimit[];
  climate_normals: ClimateNormal[];
  crowd_indexes: CrowdIndex[];
  activities: Activity[];
  amenities: SpotAmenity[];
  photos: SpotPhoto[];
  verified_at: string | null;
  is_manually_verified: boolean;
}
