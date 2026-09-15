import { z } from "zod";

/** Mirrors apps.fees.serializers on the backend. */

export const parkFeeInputSchema = z.object({
  slug: z.string(),
  name: z.string(),
  standard_fee: z.string(),
  fee_type: z.enum(["vehicle", "person"]).default("vehicle"),
});
export type ParkFeeInput = z.infer<typeof parkFeeInputSchema>;

export const feeCalculateRequestSchema = z.object({
  parks: z.array(parkFeeInputSchema),
  adults: z.number().int().min(0),
  children: z.number().int().min(0).default(0),
  is_us_resident: z.boolean(),
});
export type FeeCalculateRequest = z.infer<typeof feeCalculateRequestSchema>;

export const entryFeeLineSchema = z.object({
  park_name: z.string(),
  standard_fee: z.string(),
  surcharge: z.string(),
  subtotal: z.string(),
});

export const passRecommendationSchema = z.object({
  cheaper: z.enum(["pay_as_you_go", "annual_pass", "tie"]),
  savings: z.string(),
  explanation: z.string(),
});

export const entryFeeBreakdownSchema = z.object({
  lines: z.array(entryFeeLineSchema),
  pay_as_you_go_total: z.string(),
  annual_pass_total: z.string(),
  recommendation: passRecommendationSchema,
});
export type EntryFeeBreakdown = z.infer<typeof entryFeeBreakdownSchema>;

/** Mirrors apps.vehicles.serializers. */

export const sizeCheckRequestSchema = z.object({
  length_ft: z.string(),
  height_ft: z.string(),
  spot_slug: z.string(),
  travel_date: z.string(),
});
export type SizeCheckRequest = z.infer<typeof sizeCheckRequestSchema>;

export const fitResultSchema = z.object({
  status: z.enum(["fits", "warning", "blocked"]),
  reasons: z.array(z.string()),
});
export type FitResult = z.infer<typeof fitResultSchema>;

export const trueCostRequestSchema = z.object({
  nights: z.number().int().min(1),
  planned_miles: z.string(),
  base_nightly_rate: z.string(),
  included_miles_per_night: z.number().int().min(0).default(0),
  overage_rate_per_mile: z.string().default("0"),
  prep_fee: z.string().default("0"),
  insurance_per_night: z.string().default("0"),
  one_way: z.boolean().default(false),
  one_way_fee: z.string().default("0"),
  generator_hours: z.string().default("0"),
  generator_rate_per_hour: z.string().default("0"),
  hookup_nights: z.number().int().min(0).default(0),
  hookup_premium_per_night: z.string().default("0"),
});
export type TrueCostRequest = z.infer<typeof trueCostRequestSchema>;

export const vanCostBreakdownSchema = z.object({
  base: z.string(),
  mileage_overage: z.string(),
  prep_fee: z.string(),
  insurance: z.string(),
  one_way_fee: z.string(),
  generator: z.string(),
  hookup_premium: z.string(),
  addons: z.string(),
  total: z.string(),
});
export type VanCostBreakdown = z.infer<typeof vanCostBreakdownSchema>;
