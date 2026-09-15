import Image from "next/image";
import Link from "next/link";
import Logo from "@/components/layout/Logo";
import Nav from "@/components/layout/Nav";
import { fetchSiteSettings } from "@/lib/api";

export default async function Header() {
  // Falls back to the hardcoded name/no-logo if content service is unreachable —
  // branding must never be the reason the whole site fails to render.
  const settings = await fetchSiteSettings().catch(() => null);
  const siteName = settings?.site_name || "Roadfare";

  return (
    <header className="route-rule px-6 py-5">
      <div className="mx-auto flex max-w-[1600px] flex-wrap items-center justify-between">
        <Link
          href="/"
          className="flex items-center gap-2 text-xl font-bold tracking-tight text-pine hover:text-ink"
        >
          {settings?.logo_url ? (
            <Image src={settings.logo_url} alt="" width={28} height={28} unoptimized />
          ) : (
            <Logo />
          )}
          {siteName}
        </Link>
        <Nav />
      </div>
    </header>
  );
}
