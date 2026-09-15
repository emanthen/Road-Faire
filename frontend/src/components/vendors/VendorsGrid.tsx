"use client";

import { useMemo, useState } from "react";
import { Bike, Car, Home, Star, Tent } from "lucide-react";
import type { LucideIcon } from "lucide-react";
import OfferLink from "@/components/partners/OfferLink";
import type { OfferCategory, Partner } from "@/types/api";

const CATEGORY_LABELS: Record<OfferCategory, string> = {
  campervan: "Campervan / RV rental",
  car: "Car rental",
  hotel: "Hotel",
  campsite: "Campsite",
  activity: "Activity",
  insurance: "Insurance",
  bicycle: "Bicycle rental",
  camping_gear: "Camping gear rental",
};

const CATEGORY_ICONS: Record<OfferCategory, LucideIcon> = {
  campervan: Car,
  car: Car,
  hotel: Home,
  campsite: Tent,
  activity: Tent,
  insurance: Home,
  bicycle: Bike,
  camping_gear: Tent,
};

// Fixed order so the filter row doesn't reshuffle as data changes.
const CATEGORY_ORDER: OfferCategory[] = [
  "campervan",
  "car",
  "bicycle",
  "camping_gear",
  "campsite",
  "hotel",
  "activity",
  "insurance",
];

export default function VendorsGrid({ partners }: { partners: Partner[] }) {
  const presentCategories = useMemo(
    () =>
      CATEGORY_ORDER.filter((category) =>
        partners.some((partner) => partner.offers.some((offer) => offer.category === category))
      ),
    [partners]
  );

  const [selected, setSelected] = useState<OfferCategory | "all">("all");

  const visiblePartners = partners.filter(
    (partner) =>
      selected === "all" || partner.offers.some((offer) => offer.category === selected)
  );

  return (
    <div>
      {presentCategories.length > 1 && (
        <div className="mb-8 flex flex-wrap gap-2">
          <button
            type="button"
            onClick={() => setSelected("all")}
            className={`rounded-full border px-4 py-1.5 text-sm transition-colors ${
              selected === "all"
                ? "border-pine bg-pine text-snow"
                : "border-asphalt/30 text-asphalt hover:border-pine/50"
            }`}
          >
            All
          </button>
          {presentCategories.map((category) => (
            <button
              key={category}
              type="button"
              onClick={() => setSelected(category)}
              className={`rounded-full border px-4 py-1.5 text-sm transition-colors ${
                selected === category
                  ? "border-pine bg-pine text-snow"
                  : "border-asphalt/30 text-asphalt hover:border-pine/50"
              }`}
            >
              {CATEGORY_LABELS[category]}
            </button>
          ))}
        </div>
      )}

      {visiblePartners.length === 0 ? (
        <p className="mt-10 text-asphalt">No vendors in this category yet.</p>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {visiblePartners.map((partner) => {
            const primaryCategory = partner.offers[0]?.category;
            const Icon = primaryCategory ? CATEGORY_ICONS[primaryCategory] : Home;
            const offers =
              selected === "all"
                ? partner.offers
                : partner.offers.filter((offer) => offer.category === selected);

            return (
              <div
                key={partner.slug}
                className="flex flex-col gap-3 rounded-xl border border-asphalt/20 p-6"
              >
                <span className="flex h-10 w-10 items-center justify-center rounded-full bg-pine/10 text-pine">
                  <Icon size={20} strokeWidth={1.75} />
                </span>
                <div>
                  <h2 className="font-medium text-ink">{partner.name}</h2>
                  <p className="text-sm text-asphalt">{partner.service_area}</p>
                  {partner.contact_phone && (
                    <p className="text-sm text-asphalt">{partner.contact_phone}</p>
                  )}
                  {partner.rating && (
                    <p className="mt-1 flex items-center gap-1 text-sm text-asphalt">
                      <Star size={14} className="fill-sodium text-sodium" />
                      <span className="figure">{partner.rating}</span>
                      <span className="text-xs text-asphalt/70">on {partner.rating_source}</span>
                    </p>
                  )}
                </div>
                <ul className="mt-1 flex flex-col gap-2">
                  {offers.map((offer) => (
                    <li key={offer.id}>
                      <OfferLink
                        offerId={offer.id}
                        sponsored={false}
                        className="text-sm text-pine underline hover:text-pine/80"
                      >
                        {CATEGORY_LABELS[offer.category]} &rarr;
                      </OfferLink>
                      {offer.description && (
                        <p className="mt-0.5 text-xs text-asphalt">{offer.description}</p>
                      )}
                      {offer.price_note && (
                        <p className="mt-0.5 text-xs text-asphalt/80">{offer.price_note}</p>
                      )}
                    </li>
                  ))}
                </ul>
                {partner.terms_note && (
                  <p className="text-xs text-asphalt/80">{partner.terms_note}</p>
                )}
                {partner.verified_at === null && (
                  <p className="mt-auto text-xs text-asphalt/70">Not yet manually verified.</p>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
