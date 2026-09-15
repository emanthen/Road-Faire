import type { MetadataRoute } from "next";
import { apiFetch } from "@/lib/api";

interface SpotListItem {
  slug: string;
}

interface ContentSitemapEntry {
  path: string;
  lastmod: string;
}

const SPOT_SUB_PATHS = ["", "/cost", "/best-time-to-visit", "/reservations", "/campervan"];

async function spotRoutes(base: string): Promise<MetadataRoute.Sitemap> {
  try {
    const response = await apiFetch<{ results: SpotListItem[] }>("/api/spots/");
    return response.results.flatMap((spot) =>
      SPOT_SUB_PATHS.map((subPath) => ({
        url: `${base}/spots/${spot.slug}${subPath}`,
        lastModified: new Date(),
      }))
    );
  } catch {
    // Empty catalog (or API unreachable at build time) — no spot URLs, not a build failure.
    return [];
  }
}

async function contentRoutes(base: string): Promise<MetadataRoute.Sitemap> {
  try {
    const entries = await apiFetch<ContentSitemapEntry[]>("/api/content/sitemap");
    return entries.map((entry) => ({
      url: `${base}${entry.path}`,
      lastModified: new Date(entry.lastmod),
    }));
  } catch {
    return [];
  }
}

/** BUILD_PROMPT §6 / Phase 4 gate: 25 spots x 5 pages = 125 URLs once the catalog is
 * seeded, from /api/spots/. Editorial pages (guides) come from apps.content.sitemap via
 * /api/content/sitemap — the two content types are fetched independently so one being
 * unavailable doesn't drop the other. */
export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const base = process.env.NEXT_PUBLIC_SITE_URL ?? "https://roadfare.com";
  const staticRoutes: MetadataRoute.Sitemap = [{ url: base, lastModified: new Date() }];

  const [spots, content] = await Promise.all([spotRoutes(base), contentRoutes(base)]);

  return [...staticRoutes, ...spots, ...content];
}
