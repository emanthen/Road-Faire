import type { ReactNode } from "react";
import localFont from "next/font/local";
import Providers from "@/components/layout/Providers";

const overpass = localFont({
  src: [
    { path: "../../../public/fonts/Overpass-Regular.ttf", weight: "400", style: "normal" },
    { path: "../../../public/fonts/Overpass-Medium.ttf", weight: "500", style: "normal" },
    { path: "../../../public/fonts/Overpass-SemiBold.ttf", weight: "600", style: "normal" },
    { path: "../../../public/fonts/Overpass-Bold.ttf", weight: "700", style: "normal" },
  ],
  variable: "--font-overpass",
  display: "swap",
});

const overpassMono = localFont({
  src: [
    { path: "../../../public/fonts/OverpassMono-Regular.ttf", weight: "400", style: "normal" },
    { path: "../../../public/fonts/OverpassMono-Medium.ttf", weight: "500", style: "normal" },
    { path: "../../../public/fonts/OverpassMono-Bold.ttf", weight: "700", style: "normal" },
  ],
  variable: "--font-overpass-mono",
  display: "swap",
});

/** Shared `<html>/<body>` shell for both root layouts — the public site's
 * `(site)/layout.tsx` and the dashboard's `dashboard/layout.tsx`. Next.js's App Router
 * only supports distinct chrome per top-level segment via "multiple root layouts"
 * (no shared app/layout.tsx), so this exists purely to keep fonts/providers from
 * drifting between the two. */
export default function RootShell({ children }: { children: ReactNode }) {
  return (
    <html lang="en" className={`${overpass.variable} ${overpassMono.variable}`}>
      <body>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
