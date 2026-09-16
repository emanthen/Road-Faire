/** Mirrors apps.planner.engine.types — hand-written until /api/plan exists to generate
 * against. */

export interface TripRequest {
  origin_airport: string;
  start_date: string;
  end_date: string;
  adults: number;
  children: number;
  budget_usd: string;
  is_us_resident: boolean;
  vehicle_pref: "van" | "car";
  vibe_tags: string[];
  max_drive_hours_per_day: string;
}

export interface LoopStopActivity {
  name: string;
  kind: "trail" | "tour";
}

export interface LoopStop {
  slug: string;
  name: string;
  nights: number;
  standard_fee: string;
  fee_type: "vehicle" | "person";
  latitude: number;
  longitude: number;
  activities: LoopStopActivity[];
}

export interface Loop {
  stops: LoopStop[];
  total_miles: string;
  days: number;
  month_score: number;
}

export interface VanCostBreakdown {
  base: string;
  mileage_overage: string;
  prep_fee: string;
  insurance: string;
  one_way_fee: string;
  generator: string;
  hookup_premium: string;
  addons: string;
  total: string;
}

export interface EntryPassRecommendation {
  cheaper: "pay_as_you_go" | "annual_pass" | "tie";
  savings: string;
  explanation: string;
}

export interface CostRange {
  low: string;
  high: string;
}

export interface CostBreakdown {
  transport: string;
  lodging: string;
  entry: string;
  fuel: string;
  food: string;
  activities: string;
  subtotal: string;
  buffer: string;
  total: string;
  entry_annual_pass_total: string;
  entry_recommendation: EntryPassRecommendation;
  van_breakdown: VanCostBreakdown | null;
  // Categories among {"transport", "lodging", "fuel"} whose figure is a bootstrap
  // assumption rather than cited data — render as a range with an estimate badge,
  // never as the fake-precise dollar amount (BUILD_PROMPT C2).
  estimated_categories: string[];
  lodging_range: CostRange | null;
  transport_range: CostRange | null;
}

export interface TripOption {
  tier: "LEAN" | "BALANCED" | "COMFORT";
  loop: Loop;
  cost: CostBreakdown;
  narrative: string;
}

export interface RouteWaypoint {
  name: string;
  latitude: number;
  longitude: number;
  distance_mi: number;
}

export interface LegWaypoints {
  from_name: string;
  to_name: string;
  fuel: RouteWaypoint | null;
  restaurant: RouteWaypoint | null;
  source_url: string;
}

export interface TierWaypoints {
  tier: "LEAN" | "BALANCED" | "COMFORT";
  legs: LegWaypoints[];
}

export interface FeaturedTrip {
  id: string;
  origin_airport: string;
  start_date: string;
  end_date: string;
  destinations: string[];
  days: number;
  from_total: string | null;
}
