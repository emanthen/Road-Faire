import type { Metadata } from "next";
import Footer from "@/components/layout/Footer";
import Header from "@/components/layout/Header";
import RootShell from "@/components/layout/RootShell";
import SkipLink from "@/components/layout/SkipLink";
import "../globals.css";

export const metadata: Metadata = {
  metadataBase: new URL(process.env.NEXT_PUBLIC_SITE_URL ?? "http://localhost:3000"),
  title: "Roadfare - know the real cost before you book",
  description:
    "Three fully costed US road-trip itineraries, every fee itemised, including the non-resident national park surcharge almost no other planner accounts for.",
};

export default function SiteLayout({ children }: { children: React.ReactNode }) {
  return (
    <RootShell>
      <SkipLink />
      <Header />
      <main id="main" className="mx-auto max-w-[1600px]">
        {children}
      </main>
      <Footer />
    </RootShell>
  );
}
