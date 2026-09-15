/** PostHog events: fee_calculated, plan_created, offer_clicked.
 * Safe no-op without a configured NEXT_PUBLIC_POSTHOG_KEY (not set yet). */

function track(event: string, properties?: Record<string, unknown>) {
  if (typeof window === "undefined") return;
  const posthog = (window as { posthog?: { capture: (e: string, p?: object) => void } }).posthog;
  posthog?.capture(event, properties);
}

export function trackFeeCalculated() {
  track("fee_calculated");
}

export function trackPlanCreated() {
  track("plan_created");
}

export function trackOfferClicked(offerId: string) {
  track("offer_clicked", { offerId });
}
