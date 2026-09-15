import {
  faqsAdmin,
  offersAdmin,
  pagesAdmin,
  partnersAdmin,
  photosAdmin,
  reservationRulesAdmin,
  siteSettingsAdmin,
  spotCostsAdmin,
  spotsAdmin,
  statesAdmin,
  vehicleLimitsAdmin,
} from "@/lib/adminApi";
import type {
  FAQAdmin, FAQAdminPayload,
  OfferAdmin, OfferAdminPayload,
  PageAdmin, PageAdminPayload,
  PartnerAdmin, PartnerAdminPayload,
  PhotoAdmin, PhotoAdminPayload,
  ReservationRuleAdmin, ReservationRuleAdminPayload,
  SiteSettingsAdmin, SiteSettingsAdminPayload,
  SpotAdmin, SpotAdminPayload,
  SpotCostAdmin, SpotCostAdminPayload,
  StateAdmin,
  VehicleLimitAdmin, VehicleLimitAdminPayload,
} from "@/types/admin";
import { createAdminResourceHooks } from "@/hooks/admin/useAdminResource";

export const statesAdminHooks = createAdminResourceHooks<StateAdmin, never>(
  "admin-states", statesAdmin
);
export const spotsAdminHooks = createAdminResourceHooks<SpotAdmin, SpotAdminPayload>(
  "admin-spots", spotsAdmin
);
export const spotCostsAdminHooks = createAdminResourceHooks<SpotCostAdmin, SpotCostAdminPayload>(
  "admin-spot-costs", spotCostsAdmin
);
export const reservationRulesAdminHooks = createAdminResourceHooks<
  ReservationRuleAdmin, ReservationRuleAdminPayload
>("admin-reservation-rules", reservationRulesAdmin);
export const vehicleLimitsAdminHooks = createAdminResourceHooks<
  VehicleLimitAdmin, VehicleLimitAdminPayload
>("admin-vehicle-limits", vehicleLimitsAdmin);
export const photosAdminHooks = createAdminResourceHooks<PhotoAdmin, PhotoAdminPayload>(
  "admin-photos", photosAdmin
);
export const partnersAdminHooks = createAdminResourceHooks<PartnerAdmin, PartnerAdminPayload>(
  "admin-partners", partnersAdmin
);
export const offersAdminHooks = createAdminResourceHooks<OfferAdmin, OfferAdminPayload>(
  "admin-offers", offersAdmin
);
export const pagesAdminHooks = createAdminResourceHooks<PageAdmin, PageAdminPayload>(
  "admin-pages", pagesAdmin
);
export const faqsAdminHooks = createAdminResourceHooks<FAQAdmin, FAQAdminPayload>(
  "admin-faqs", faqsAdmin
);
export const siteSettingsAdminHooks = createAdminResourceHooks<
  SiteSettingsAdmin, SiteSettingsAdminPayload
>("admin-site-settings", siteSettingsAdmin);
