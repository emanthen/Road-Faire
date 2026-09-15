import Link from "next/link";
import { fetchSiteSettings } from "@/lib/api";

const PRODUCT_LINKS = [
  { href: "/plan", label: "Plan a trip" },
  { href: "/spots", label: "Browse spots" },
  { href: "/tools/national-park-fee-calculator", label: "Fee calculator" },
  { href: "/vendors", label: "Vendors" },
] as const;

const COMPANY_LINKS = [
  { href: "/guides", label: "Travel stories" },
  { href: "/about", label: "About" },
  { href: "/disclosure", label: "How we make money" },
] as const;

export default async function Footer() {
  const settings = await fetchSiteSettings().catch(() => null);
  const siteName = settings?.site_name || "Roadfare";

  return (
    <footer className="border-t border-asphalt/20 px-6 py-12 text-sm">
      <div className="mx-auto grid max-w-[1600px] gap-10 sm:grid-cols-[2fr_1fr_1fr]">
        <div>
          <p className="text-lg font-bold tracking-tight text-pine">{siteName}</p>
          <p className="mt-3 max-w-xs text-asphalt">
            {settings?.tagline ||
              "Every fee and rule cited to a real source or flagged for review. We don't guess at numbers that cost you money."}
          </p>
          {(settings?.twitter_url || settings?.instagram_url) && (
            <div className="mt-4 flex gap-4">
              {settings.twitter_url && (
                <a href={settings.twitter_url} className="text-asphalt hover:text-pine">
                  Twitter
                </a>
              )}
              {settings.instagram_url && (
                <a href={settings.instagram_url} className="text-asphalt hover:text-pine">
                  Instagram
                </a>
              )}
            </div>
          )}
        </div>

        <nav aria-label="Product">
          <p className="text-xs font-semibold uppercase tracking-[0.1em] text-asphalt">
            Product
          </p>
          <ul className="mt-3 flex flex-col gap-2">
            {PRODUCT_LINKS.map((link) => (
              <li key={link.href}>
                <Link href={link.href} className="text-ink hover:text-pine">
                  {link.label}
                </Link>
              </li>
            ))}
          </ul>
        </nav>

        <nav aria-label="Company">
          <p className="text-xs font-semibold uppercase tracking-[0.1em] text-asphalt">
            Company
          </p>
          <ul className="mt-3 flex flex-col gap-2">
            {COMPANY_LINKS.map((link) => (
              <li key={link.href}>
                <Link href={link.href} className="text-ink hover:text-pine">
                  {link.label}
                </Link>
              </li>
            ))}
          </ul>
        </nav>
      </div>

      <div className="mx-auto mt-10 flex max-w-[1600px] flex-wrap items-center justify-between gap-4 border-t border-asphalt/20 pt-6 text-asphalt">
        <p>
          &copy; {new Date().getFullYear()} {siteName}.
        </p>
        <p>Not affiliated with the National Park Service or any government agency.</p>
      </div>
    </footer>
  );
}
