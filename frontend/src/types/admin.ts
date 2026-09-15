/** Request/response shapes for the staff-only /api/admin/ dashboard API
 * (apps.dashboard on the backend). Kept separate from types/api.ts, which describes
 * the read-optimized public API — the admin API is flat, these types are flat too. */

export interface AdminListResponse<T> {
  next: string | null;
  previous: string | null;
  results: T[];
}

export interface StateAdmin {
  id: number;
  name: string;
  abbreviation: string;
  region: number;
}

export interface SpotAdmin {
  id: number;
  name: string;
  slug: string;
  state: number;
  type: "national_park" | "state_park" | "monument" | "forest" | "other";
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
  latitude: number;
  longitude: number;
  source_url: string;
  verified_at: string | null;
  is_manually_verified: boolean;
  needs_verification: boolean;
  created_at: string;
  updated_at: string;
}

export type SpotAdminPayload = Partial<Omit<SpotAdmin, "id" | "created_at" | "updated_at">>;

export interface SpotCostAdmin {
  id: number;
  spot: number;
  entry_vehicle: string | null;
  entry_person: string | null;
  parking: string | null;
  campsite_low: string | null;
  campsite_high: string | null;
  shuttle: string | null;
  source_url: string;
  verified_at: string | null;
  is_manually_verified: boolean;
  needs_verification: boolean;
}

export type SpotCostAdminPayload = Partial<Omit<SpotCostAdmin, "id">>;

export interface ReservationRuleAdmin {
  id: number;
  spot: number;
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
  is_manually_verified: boolean;
  needs_verification: boolean;
}

export type ReservationRuleAdminPayload = Partial<Omit<ReservationRuleAdmin, "id">>;

export interface VehicleLimitAdmin {
  id: number;
  spot: number;
  max_length_ft: string | null;
  max_height_ft: string | null;
  max_weight_lb: number | null;
  effective_from: string | null;
  applies_to_roads: string[];
  source_url: string;
  verified_at: string | null;
  is_manually_verified: boolean;
  needs_verification: boolean;
}

export type VehicleLimitAdminPayload = Partial<Omit<VehicleLimitAdmin, "id">>;

export interface PhotoAdmin {
  id: number;
  spot: number;
  source: string;
  credit: string;
  license: string;
  s3_key: string;
  alt_text: string;
  caption: string;
  is_primary: boolean;
  sort_order: number;
}

export type PhotoAdminPayload = Partial<Omit<PhotoAdmin, "id">>;

export interface PartnerAdmin {
  id: number;
  name: string;
  slug: string;
  service_area: string;
  contact_phone: string;
  terms_note: string;
  rating: string | null;
  rating_count: number | null;
  rating_source: string;
  rating_url: string;
  source_url: string;
  verified_at: string | null;
  is_manually_verified: boolean;
  needs_verification: boolean;
}

export type PartnerAdminPayload = Partial<Omit<PartnerAdmin, "id">>;

export interface OfferAdmin {
  id: string;
  partner: number;
  category:
    | "campervan" | "car" | "hotel" | "campsite" | "activity" | "insurance"
    | "bicycle" | "camping_gear";
  base_url: string;
  tracking_params: Record<string, string>;
  commission_note: string;
  description: string;
  price_note: string;
  created_at: string;
  updated_at: string;
}

export type OfferAdminPayload = Partial<Omit<OfferAdmin, "id" | "created_at" | "updated_at">>;

export interface PageAdmin {
  id: number;
  title: string;
  slug: string;
  body: string;
  published: boolean;
  meta_title: string;
  meta_description: string;
  created_at: string;
  updated_at: string;
}

export type PageAdminPayload = Partial<Omit<PageAdmin, "id" | "created_at" | "updated_at">>;

export interface FAQAdmin {
  id: number;
  question: string;
  answer: string;
  order: number;
}

export type FAQAdminPayload = Partial<Omit<FAQAdmin, "id">>;

export interface SiteSettingsAdmin {
  id: number;
  site_name: string;
  tagline: string;
  logo_url: string;
  twitter_url: string;
  instagram_url: string;
  contact_email: string;
}

export type SiteSettingsAdminPayload = Partial<Omit<SiteSettingsAdmin, "id">>;
