import { FileText, HelpCircle, MapPin, Settings, Store } from "lucide-react";
import Link from "next/link";

const SECTIONS = [
  { href: "/dashboard/spots", label: "Spots", description: "National parks and other stops.", icon: MapPin },
  { href: "/dashboard/vendors", label: "Vendors", description: "Partners and their offers.", icon: Store },
  { href: "/dashboard/articles", label: "Articles", description: "Guides and static pages, with SEO fields.", icon: FileText },
  { href: "/dashboard/faqs", label: "FAQs", description: "Frequently asked questions.", icon: HelpCircle },
  { href: "/dashboard/settings", label: "Site settings", description: "Branding and contact info.", icon: Settings },
];

export default function DashboardOverviewPage() {
  return (
    <div>
      <h1 className="text-2xl font-semibold">Dashboard</h1>
      <p className="mt-1 text-muted-foreground">Manage everything that&apos;s on the site.</p>
      <div className="mt-6 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {SECTIONS.map((section) => {
          const Icon = section.icon;
          return (
            <Link
              key={section.href}
              href={section.href}
              className="rounded-lg border border-border bg-card p-5 transition-colors hover:border-primary"
            >
              <Icon className="size-6 text-pine" />
              <p className="mt-3 font-medium">{section.label}</p>
              <p className="mt-1 text-sm text-muted-foreground">{section.description}</p>
            </Link>
          );
        })}
      </div>
    </div>
  );
}
