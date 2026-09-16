/** Typed fetch wrapper, base URL, error envelope -- matches
 * apps.core.exceptions.structured_exception_handler's { error: { status_code, detail } } shape.
 */

import type {
  AuthResponse,
  AuthUser,
  ContentPage,
  ContentPageListResponse,
  Partner,
  SiteSettings,
  SpotDetail,
  SpotListResponse,
} from "@/types/api";
import type { FeaturedTrip, TierWaypoints, TripOption, TripRequest } from "@/types/planner";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export class ApiError extends Error {
  constructor(
    public statusCode: number,
    public detail: unknown
  ) {
    super(typeof detail === "string" ? detail : JSON.stringify(detail));
  }
}

export async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: { "Content-Type": "application/json", ...init?.headers },
  });

  const body = response.status === 204 ? null : await response.json();

  if (!response.ok) {
    throw new ApiError(response.status, body?.error?.detail ?? body);
  }

  return body as T;
}

export async function fetchSpot(slug: string): Promise<SpotDetail> {
  return apiFetch<SpotDetail>(`/api/spots/${slug}/`);
}

export async function fetchSpots(filters: {
  state?: string;
  type?: string;
  activity?: string;
}): Promise<SpotListResponse> {
  const params = new URLSearchParams();
  if (filters.state) params.set("state", filters.state);
  if (filters.type) params.set("type", filters.type);
  if (filters.activity) params.set("activity", filters.activity);
  const query = params.toString();
  return apiFetch<SpotListResponse>(`/api/spots/${query ? `?${query}` : ""}`);
}

export interface PlanRequestSummary {
  origin_airport: string;
  start_date: string;
  end_date: string;
  adults: number;
  children: number;
  vehicle_pref: "car" | "van";
  is_us_resident: boolean;
}

export interface PlanResponse {
  id: string;
  status: "pending" | "running" | "done" | "failed";
  request: PlanRequestSummary;
  options: TripOption[];
}

export async function createPlan(request: TripRequest): Promise<PlanResponse> {
  return apiFetch<PlanResponse>("/api/plan/", {
    method: "POST",
    body: JSON.stringify(request),
  });
}

export async function fetchPlan(id: string): Promise<PlanResponse> {
  return apiFetch<PlanResponse>(`/api/plan/${id}`);
}

export async function fetchPlanWaypoints(id: string): Promise<TierWaypoints[]> {
  return apiFetch<TierWaypoints[]>(`/api/plan/${id}/waypoints`);
}

export function planPdfUrl(id: string): string {
  return `${API_BASE_URL}/api/plan/${id}/pdf`;
}

export async function fetchPages(): Promise<ContentPageListResponse> {
  return apiFetch<ContentPageListResponse>("/api/content/pages/");
}

export async function fetchPage(slug: string): Promise<ContentPage> {
  return apiFetch<ContentPage>(`/api/content/pages/${slug}/`);
}

export async function fetchFeaturedTrips(): Promise<FeaturedTrip[]> {
  return apiFetch<FeaturedTrip[]>("/api/plan/featured");
}

export async function fetchPartners(): Promise<Partner[]> {
  return apiFetch<Partner[]>("/api/partners/");
}

export async function fetchSiteSettings(): Promise<SiteSettings> {
  return apiFetch<SiteSettings>("/api/content/settings");
}

export async function register(
  username: string,
  email: string,
  password: string
): Promise<AuthResponse> {
  return apiFetch<AuthResponse>("/api/auth/register", {
    method: "POST",
    body: JSON.stringify({ username, email, password }),
  });
}

export async function login(username: string, password: string): Promise<AuthResponse> {
  return apiFetch<AuthResponse>("/api/auth/login", {
    method: "POST",
    body: JSON.stringify({ username, password }),
  });
}

export async function loginWithGoogle(idToken: string): Promise<AuthResponse> {
  return apiFetch<AuthResponse>("/api/auth/google", {
    method: "POST",
    body: JSON.stringify({ id_token: idToken }),
  });
}

export async function logout(token: string): Promise<void> {
  await apiFetch<void>("/api/auth/logout", {
    method: "POST",
    headers: { Authorization: `Token ${token}` },
  });
}

export async function fetchMe(token: string): Promise<AuthUser> {
  return apiFetch<AuthUser>("/api/auth/me", {
    headers: { Authorization: `Token ${token}` },
  });
}
