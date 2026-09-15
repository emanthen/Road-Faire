/** Metadata + JSON-LD builders (TouristAttraction, FAQPage, BreadcrumbList). */

import type { Metadata } from "next";
import { ApiError, fetchSpot } from "@/lib/api";

export interface SpotSummary {
  slug: string;
  name: string;
  blurb: string;
  latitude: number;
  longitude: number;
  state: number;
  meta_title?: string;
  meta_description?: string;
}

export function buildSpotMetadata(spot: SpotSummary, pageTitle: string): Metadata {
  return {
    title: spot.meta_title || `${pageTitle} - ${spot.name} - Roadfare`,
    description:
      spot.meta_description || spot.blurb || `${pageTitle} for ${spot.name} on Roadfare.`,
  };
}

/** Every spot sub-page's generateMetadata needs this — fetchSpot() 404s for an unknown
 * slug, and an uncaught throw here makes Next fall back to the raw URL as the tab
 * title instead of the page component's own notFound(). Falling back to {} lets the
 * root layout's default title show instead, same as a normal 404. */
export async function safeSpotMetadata(slug: string, pageTitle: string): Promise<Metadata> {
  try {
    const spot = await fetchSpot(slug);
    return buildSpotMetadata(spot, pageTitle);
  } catch (error) {
    if (error instanceof ApiError && error.statusCode === 404) return {};
    throw error;
  }
}

export function touristAttractionJsonLd(spot: SpotSummary) {
  return {
    "@context": "https://schema.org",
    "@type": "TouristAttraction",
    name: spot.name,
    description: spot.blurb,
    geo: {
      "@type": "GeoCoordinates",
      latitude: spot.latitude,
      longitude: spot.longitude,
    },
  };
}

export function breadcrumbJsonLd(items: { name: string; url: string }[]) {
  return {
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    itemListElement: items.map((item, index) => ({
      "@type": "ListItem",
      position: index + 1,
      name: item.name,
      item: item.url,
    })),
  };
}

export function faqPageJsonLd(questions: { question: string; answer: string }[]) {
  return {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    mainEntity: questions.map((q) => ({
      "@type": "Question",
      name: q.question,
      acceptedAnswer: { "@type": "Answer", text: q.answer },
    })),
  };
}
