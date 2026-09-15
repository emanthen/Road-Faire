"use client";

import { Menu, X } from "lucide-react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useRef, useState } from "react";
import { useAuth } from "@/lib/auth";

const NAV_LINKS = [
  { href: "/plan", label: "Plan a trip" },
  { href: "/spots", label: "Browse spots" },
  { href: "/tools/national-park-fee-calculator", label: "Fee calculator" },
  { href: "/vendors", label: "Vendors" },
  { href: "/guides", label: "Travel stories" },
  { href: "/about", label: "About" },
] as const;

export default function Nav() {
  const [isOpen, setIsOpen] = useState(false);
  const pathname = usePathname();
  const router = useRouter();
  const toggleRef = useRef<HTMLButtonElement>(null);
  const { user, isLoading, logout } = useAuth();

  function isActive(href: string): boolean {
    return href === "/" ? pathname === "/" : pathname.startsWith(href);
  }

  function close() {
    setIsOpen(false);
    toggleRef.current?.focus();
  }

  async function handleLogout() {
    await logout();
    close();
    router.push("/");
  }

  return (
    <nav
      aria-label="Primary"
      className="flex w-full flex-wrap items-center justify-end sm:w-auto"
      onKeyDown={(e) => {
        if (e.key === "Escape" && isOpen) close();
      }}
    >
      <ul className="hidden items-center gap-6 sm:flex">
        {NAV_LINKS.map((link) => (
          <li key={link.href}>
            <Link
              href={link.href}
              aria-current={isActive(link.href) ? "page" : undefined}
              className={`text-sm font-medium hover:text-pine ${
                isActive(link.href) ? "text-pine" : "text-ink"
              }`}
            >
              {link.label}
            </Link>
          </li>
        ))}
      </ul>

      {!isLoading && (
        <div className="ml-6 hidden items-center gap-4 sm:flex">
          {user ? (
            <>
              <span className="text-sm text-asphalt">{user.username}</span>
              <button
                type="button"
                onClick={handleLogout}
                className="text-sm font-medium text-ink hover:text-pine"
              >
                Log out
              </button>
            </>
          ) : (
            <>
              <Link href="/login" className="text-sm font-medium text-ink hover:text-pine">
                Log in
              </Link>
              <Link
                href="/signup"
                className="rounded bg-pine px-4 py-2 text-sm font-medium text-snow hover:bg-ink"
              >
                Sign up
              </Link>
            </>
          )}
        </div>
      )}

      <button
        ref={toggleRef}
        type="button"
        onClick={() => setIsOpen((open) => !open)}
        aria-expanded={isOpen}
        aria-controls="mobile-nav"
        aria-label={isOpen ? "Close menu" : "Open menu"}
        className="flex min-h-11 min-w-11 items-center justify-center rounded text-ink sm:hidden"
      >
        {isOpen ? <X size={22} /> : <Menu size={22} />}
      </button>

      {isOpen && (
        <ul id="mobile-nav" className="mt-4 flex w-full flex-col gap-1 sm:hidden">
          {NAV_LINKS.map((link) => (
            <li key={link.href}>
              <Link
                href={link.href}
                onClick={() => setIsOpen(false)}
                aria-current={isActive(link.href) ? "page" : undefined}
                className={`block min-h-11 py-2.5 text-base font-medium hover:text-pine ${
                  isActive(link.href) ? "text-pine" : "text-ink"
                }`}
              >
                {link.label}
              </Link>
            </li>
          ))}
          <li className="mt-2 border-t border-asphalt/20 pt-2">
            {user ? (
              <button
                type="button"
                onClick={handleLogout}
                className="block min-h-11 py-2.5 text-base font-medium text-ink hover:text-pine"
              >
                Log out ({user.username})
              </button>
            ) : (
              <div className="flex gap-4">
                <Link
                  href="/login"
                  onClick={() => setIsOpen(false)}
                  className="block min-h-11 py-2.5 text-base font-medium text-ink hover:text-pine"
                >
                  Log in
                </Link>
                <Link
                  href="/signup"
                  onClick={() => setIsOpen(false)}
                  className="block min-h-11 py-2.5 text-base font-medium text-ink hover:text-pine"
                >
                  Sign up
                </Link>
              </div>
            )}
          </li>
        </ul>
      )}
    </nav>
  );
}
