/** Typed client for the staff-only /api/admin/ dashboard API. Wraps the existing
 * apiFetch (src/lib/api.ts) with the Authorization header every admin call needs. */

import { apiFetch } from "@/lib/api";
import type {
  AdminListResponse,
  FAQAdmin,
  FAQAdminPayload,
  OfferAdmin,
  OfferAdminPayload,
  PageAdmin,
  PageAdminPayload,
  PartnerAdmin,
  PartnerAdminPayload,
  PhotoAdmin,
  PhotoAdminPayload,
  ReservationRuleAdmin,
  ReservationRuleAdminPayload,
  SiteSettingsAdmin,
  SiteSettingsAdminPayload,
  SpotAdmin,
  SpotAdminPayload,
  SpotCostAdmin,
  SpotCostAdminPayload,
  StateAdmin,
  VehicleLimitAdmin,
  VehicleLimitAdminPayload,
} from "@/types/admin";

function authHeaders(token: string): HeadersInit {
  return { Authorization: `Token ${token}` };
}

async function apiFetchAuth<T>(path: string, token: string, init?: RequestInit): Promise<T> {
  return apiFetch<T>(path, { ...init, headers: { ...authHeaders(token), ...init?.headers } });
}

/** One CRUD client per admin resource, all built on the same five operations. `path`
 * is the router prefix under /api/admin/ (e.g. "spots"); `query` lets list() filter by
 * a parent FK (e.g. { spot: 12 }) or search term.
 *
 * `paginated` must match the backend viewset's pagination_class: resources with no
 * `created_at` field (see apps.dashboard.views) run with pagination_class = None and
 * return a plain array, not {next, previous, results} — list() normalizes both into
 * the same AdminListResponse shape so callers never branch on it. */
function crud<T, TPayload>(path: string, { paginated = true }: { paginated?: boolean } = {}) {
  return {
    async list(
      token: string,
      query?: Record<string, string | number>
    ): Promise<AdminListResponse<T>> {
      const params = query
        ? `?${new URLSearchParams(query as Record<string, string>).toString()}`
        : "";
      if (!paginated) {
        const results = await apiFetchAuth<T[]>(`/api/admin/${path}/${params}`, token);
        return { next: null, previous: null, results };
      }
      return apiFetchAuth<AdminListResponse<T>>(`/api/admin/${path}/${params}`, token);
    },
    fetch(token: string, id: string | number) {
      return apiFetchAuth<T>(`/api/admin/${path}/${id}/`, token);
    },
    create(token: string, payload: TPayload) {
      return apiFetchAuth<T>(`/api/admin/${path}/`, token, {
        method: "POST",
        body: JSON.stringify(payload),
      });
    },
    update(token: string, id: string | number, payload: TPayload) {
      return apiFetchAuth<T>(`/api/admin/${path}/${id}/`, token, {
        method: "PATCH",
        body: JSON.stringify(payload),
      });
    },
    remove(token: string, id: string | number) {
      return apiFetchAuth<void>(`/api/admin/${path}/${id}/`, token, { method: "DELETE" });
    },
  };
}

export const statesAdmin = crud<StateAdmin, never>("states", { paginated: false });
export const spotsAdmin = crud<SpotAdmin, SpotAdminPayload>("spots");
export const spotCostsAdmin = crud<SpotCostAdmin, SpotCostAdminPayload>("spot-costs", {
  paginated: false,
});
export const reservationRulesAdmin = crud<ReservationRuleAdmin, ReservationRuleAdminPayload>(
  "reservation-rules",
  { paginated: false }
);
export const vehicleLimitsAdmin = crud<VehicleLimitAdmin, VehicleLimitAdminPayload>(
  "vehicle-limits",
  { paginated: false }
);
export const photosAdmin = crud<PhotoAdmin, PhotoAdminPayload>("photos", { paginated: false });
export const partnersAdmin = crud<PartnerAdmin, PartnerAdminPayload>("partners", {
  paginated: false,
});
export const offersAdmin = crud<OfferAdmin, OfferAdminPayload>("offers");
export const pagesAdmin = crud<PageAdmin, PageAdminPayload>("pages");
export const faqsAdmin = crud<FAQAdmin, FAQAdminPayload>("faqs", { paginated: false });
export const siteSettingsAdmin = crud<SiteSettingsAdmin, SiteSettingsAdminPayload>(
  "site-settings",
  { paginated: false }
);
