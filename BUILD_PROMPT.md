# ROADFARE — MASTER BUILD PROMPT

## 0. ROLE

Lead engineer building **Roadfare**, a US road-trip planning and cost-transparency
platform. Production system, not a demo. Strict phases, review at each gate. Do not skip ahead.
Do not write placeholder logic and call it done.

Non-negotiables before writing any code:

1. `PROJECT_STRUCTURE.md` in this repo is the contract for the file tree. Follow it exactly.
2. Never let an LLM compute money. All pricing, fees and totals are computed in Python with
   `Decimal`, unit-tested, and asserted. The LLM writes prose only.
3. Every fee, rule and price in the database carries a `source_url` and a `verified_at` date.
   If it cannot be cited, it is not stored.
4. Write the test before the feature for anything in the `fees` and `planner` apps.

## 1. WHAT ROADFARE IS

A person tells us: where they fly into, when, how many people, their budget, whether they are a
US resident, and what kind of trip they want. We return three fully costed short-trip itineraries
(3–7 days) built from a database of US outdoor destinations — with every charge itemised, the
best months to go, expected weather, and live rules for permits and timed entry.

We do not own inventory. We refer to partners (campervans, cars, hotels, campsites, tours) and
earn commission. Our product is the accuracy of the number.

### The wedge — build this first and make it the hero

Since 1 January 2026, non-US residents aged 16+ pay a **$100 per-person surcharge** to enter 11
specific national parks, on top of the standard entrance fee. The America the Beautiful annual
pass is **$80 for US residents and $250 for non-residents**; either version exempts the holder
from the surcharge. Fee-free days in 2026 are US-residents-only and do not waive the surcharge.

The 11 surcharge parks: Acadia, Bryce Canyon, Everglades, Glacier, Grand Canyon, Grand Teton,
Rocky Mountain, Sequoia & Kings Canyon, Yellowstone, Yosemite, Zion.

A family of two adults doing Yellowstone + Grand Teton + Yosemite pays $600 in surcharges, or
$500 for two non-resident passes. Our calculator tells them which is cheaper, in one screen,
before they book anything. That calculator is the homepage hero and the primary acquisition tool.

Second wedge: 2026 reservation rules changed and most published guides are stale. Rocky Mountain
still requires timed entry (9am–2pm, 22 May – 12 Oct 2026, with a separate Bear Lake Road product
required 5am–6pm). Yosemite and Arches dropped timed entry entirely. Glacier is piloting a
ticketed shuttle for Going-to-the-Sun Road. Acadia's Cadillac Summit Road reservation is $6.
Zion applies large-vehicle limits (35 ft 9 in long, 11 ft 4 in tall) from 7 June — which matters
enormously for campervan renters and which no generic planner checks.

Treat "correct, dated, cited rules" as the moat. Build the schema so staleness is visible.

## 2. TECH STACK — USE EXACTLY THIS

**Backend**: Python 3.12, Django 5.1, DRF, PostgreSQL 16 + PostGIS, Celery 5 + Redis 7,
`django-environ`, `drf-spectacular`, `django-filter`, `pytest`/`pytest-django`/`factory-boy`,
`ruff`, `mypy` (non-strict), `structlog`, `sentry-sdk`.

**Frontend**: Next.js 15 (App Router, TypeScript, Server Components by default), Tailwind CSS v4,
shadcn/ui, Radix primitives, TanStack Query v5, `zod`, MapLibre GL JS + Protomaps, Recharts,
metadata API + JSON-LD.

**Infra**: Docker Compose (local), AWS ECS Fargate + RDS Postgres + ElastiCache Redis + S3 +
CloudFront (prod), Terraform (`infra/terraform`), GitHub Actions CI/CD, Resend, PostHog, Sentry.

**Explicitly do NOT add:** GraphQL, microservices, Kubernetes, a message queue other than Redis,
an ORM other than Django's, Redux, or any auth provider in Phase 1–4.

## 3. DATA SOURCES

| Purpose | Source | Notes |
|---|---|---|
| Parks, alerts, fees, hours | NPS API (`developer.nps.gov`) | Free key, rate-limited |
| Campgrounds, permits, timed entry | Recreation.gov RIDB API | Free key |
| Forecast weather | Open-Meteo | No key, cache 1h |
| Climate normals | NOAA NCEI 1991–2020 normals | Bulk download, load once |
| Trails, elevation | OpenStreetMap / Overpass | Cache aggressively |
| Businesses near a spot | Google Places API | Paid — cache 30 days |
| Drive times | OSRM self-hosted, fallback Google Routes | Precompute airport→spot matrix |

Ingestion rules: every connector is idempotent, writes to a staging model, diffs against live,
and records what changed. Never blind-overwrite a hand-verified field — use `is_manually_verified`
to protect it.

## 4. THE COST ENGINE — SPECIFICATION

`backend/apps/planner/engine/`. Pure functions, no Django ORM calls inside the math, all inputs
passed in as dataclasses.

```
INPUT: TripRequest(
    origin_airport, start_date, end_date, adults, children,
    budget_usd, is_us_resident, vehicle_pref, vibe_tags, max_drive_hours_per_day
)

STEP 1  candidate_spots = spots within drive radius of origin
                          AND month_score(spot, start_date.month) >= 60
STEP 2  loops = cluster candidates into routes where each leg <= max_drive_hours_per_day
                and total days == trip length
STEP 3  for each loop, cost it:
          transport  = van | car+tent | car+hotel
          lodging    = campsite | motel | mixed
          entry      = entry_fees(loop, adults, children, is_us_resident)
          fuel       = total_miles / mpg * fuel_price_usd
          food       = tier * people * days   (35 self-cook / 75 mixed / 130 restaurant)
          activities = sum(required permits + selected tours)
          subtotal   = sum(above)
          buffer     = subtotal * 0.15
STEP 4  rank loops where total <= budget, tie-break on month_score desc
STEP 5  return exactly 3: LEAN, BALANCED, COMFORT
```

### 4.1 Campervan true-cost rule

Never show a teaser nightly rate. Every van quote itemises: base nightly rate x nights; mileage
overage `max(0, planned_miles - included_miles_per_night * nights) * overage_rate`; prep/cleaning
fee; insurance/damage waiver per night; one-way drop fee if pickup != dropoff; generator hours;
campground hookup premium vs dry camping; propane/bedding/chair add-ons.

Also run `vehicle_fits(spot, vehicle)` for every spot on the route and surface a hard warning if
the vehicle exceeds any park's length/height limit.

### 4.2 Entry fee resolver — write the tests first

```python
def entry_fees(parks, adults_16plus, is_us_resident) -> EntryFeeBreakdown:
    """
    Returns both the pay-as-you-go total and the annual-pass total,
    and recommends the cheaper option with an explanation string.

    Rules (2026):
      - Standard entrance fee applies per park, per vehicle or per person (park-specific).
      - If NOT us_resident: add $100 per adult 16+ for EACH of the 11 surcharge parks,
        charged separately per park, unless an ATB pass is held.
      - ATB annual pass: $80 resident / $250 non-resident. Exempts holder from the surcharge.
      - Children under 16 are always free.
      - Fee-free days in 2026 apply to US residents only and never waive the surcharge.
    """
```

Test cases that must pass:
- 2 non-resident adults, Yellowstone + Grand Teton + Yosemite → pay-as-you-go includes $600
  surcharge; recommendation is 2 non-resident passes at $500.
- 1 non-resident adult, 1 surcharge park → break-even; assert the engine explains the tie.
- 2 US-resident adults, 3 parks → no surcharge; recommend $80 pass only if >2 parks.
- 2 adults + 3 children under 16, non-resident → children contribute $0 surcharge.
- A park not on the list of 11 → no surcharge regardless of residency.

Every fee constant lives in `backend/apps/fees/constants.py` with a `SOURCE_URL` and
`EFFECTIVE_FROM` date next to it. No magic numbers anywhere else in the codebase.

## 5. DESIGN DIRECTION

The subject is American road travel and the honest arithmetic of it. The design should feel like
a well-made trip receipt crossed with a highway sign — legible at speed, numerically confident,
never precious.

**Type.** `Overpass` for all UI and body text — it derives from Highway Gothic, so it is
genuinely of the subject rather than decorative. `Overpass Mono` for every dollar figure, mile
count and date. Numbers are the product; set them in mono at a heavier weight than the label
beside them, right-aligned in every table. One family, two cuts. No display serif.

**Palette.** Six values, used strictly:
```
--ink      #12140F   text
--pine     #24503F   primary surfaces, headers
--asphalt  #6B7169   secondary text, borders
--sodium   #E8A33D   the single accent — costs the user did not expect
--snow     #FAFAF7   page background
--signal   #C1462E   warnings only (vehicle won't fit, permit required, price rising)
```
Sodium appears on one thing per screen. If two things are sodium, one is wrong.

**Hero.** The homepage hero is not a headline over a photograph. It is the non-resident fee
calculator, live and usable above the fold, with three inputs and an immediate dollar answer.
The product demonstrates itself. Copy sits underneath, not above.

**Structure.** Cost breakdowns are tables with hairline rules, not cards. Reserve rounded
containers for interactive controls only.

**Motion.** One orchestrated moment: when the fee calculator recomputes, the changed number
counts to its new value over 400ms. Everything else is static. Respect `prefers-reduced-motion`.

**Copy.** Plain verbs, sentence case. "You'll pay $600 in surcharges" not "Surcharge total:
$600.00". Errors say what to fix. Empty states say what to do next. No exclamation marks.

**Avoid**: tracked-out all-caps eyebrow labels above headings, meta strings joined with middle
dots, `→` appended to button text, gradient washes, a soft grey shadow under every card,
warm-cream backgrounds with a terracotta accent.

**Floor.** Responsive to 375px, visible keyboard focus rings, WCAG AA contrast, works with JS
disabled for all content pages (they are Server Components).

## 6. SEO ARCHITECTURE — GROWTH STRATEGY

Every spot generates a static page set, Server Components with ISR (revalidate 24h):

```
/spots/[slug]                      overview, at-a-glance costs, map
/spots/[slug]/cost                 full fee breakdown, resident vs non-resident
/spots/[slug]/best-time-to-visit   month-by-month table from climate normals + crowd index
/spots/[slug]/reservations         permits, timed entry, lotteries, with verified_at date
/spots/[slug]/campervan            vehicle size limits, nearby hookups, dump stations
/trips/[slug]                      published itineraries
/tools/national-park-fee-calculator   the viral tool
/tools/campervan-cost-calculator
/tools/vehicle-size-checker
```

Unique `<title>`/meta description per page generated from data, JSON-LD (`TouristAttraction`,
`FAQPage`, `BreadcrumbList`), `sitemap.ts` generated from the DB, `robots.ts`, canonical URLs, OG
images via `next/og`. Show a visible **"Fees verified 14 Aug 2026"** line on every cost page —
freshness as a UI feature, not metadata.

## 7. MONETISATION

Affiliate links built server-side by `apps/partners`, never hardcoded in the frontend.

```python
class Offer(models.Model):
    partner        # outdoorsy | rvshare | discovercars | booking | hipcamp | viator | insurance
    category       # campervan | car | hotel | campsite | activity | insurance
    base_url
    tracking_params  # JSONField
    commission_note  # e.g. "flat $60/booking", "4% + $7 per listing"
```

Every outbound link goes through `/go/<offer_id>?spot=<slug>` which records a `Click` row (offer,
spot, session, referrer, utm) then 302s. FTC disclosure component renders above the fold on any
page containing affiliate links — legally required for US traffic, not optional.

## 8. PHASES AND GATES

Stop after each phase. Print a summary, run the tests, wait for approval.

- **Phase 1 — Skeleton.** Repo per `PROJECT_STRUCTURE.md`, Docker Compose up, Django + Next both
  serving, Postgres + PostGIS + Redis healthy, CI green, `/api/health` and `/api/schema` live.
  Gate: `docker compose up` works from a clean clone with only `.env` filled in.
- **Phase 2 — Catalog + ingest.** All models migrated. NPS/RIDB connectors with recorded HTTP
  fixtures. NOAA normals loader. 25 spots seeded and verified by hand.
  Gate: `python manage.py ingest_all` populates a clean DB and is safely re-runnable.
- **Phase 3 — Fees engine.** `apps/fees` complete with every test case from §4.2 passing. Public
  API endpoint. The calculator page on the frontend.
  Gate: 100% branch coverage on `fees/engine.py`.
- **Phase 4 — Spot pages.** All five page types rendering from real data, JSON-LD, sitemap, OG
  images, verified-at line. Lighthouse SEO and accessibility both ≥95.
  Gate: 25 spots × 5 pages = 125 URLs in the sitemap, all returning 200.
- **Phase 5 — Planner.** Cost engine, loop clustering, three-option output, PDF export. Claude API
  writes only the narrative prose around numbers the engine computed.
  Gate: a golden-file test asserting a known request produces a known dollar total.
- **Phase 6 — Partners + leads.** Offer model, `/go/` redirector, click tracking, email capture,
  Resend integration, PostHog events, FTC disclosure.
  Gate: an end-to-end test from planner result → outbound click → recorded row.
- **Phase 7 — Deploy.** Terraform for ECS Fargate, RDS, ElastiCache, S3, CloudFront. GitHub
  Actions building and pushing both images. Staging environment live.

## 9. HOUSE RULES

- Conventional commits. One logical change per commit.
- No secrets in the repo. `.env.example` documents every variable with a comment.
- `ruff check` and `mypy` clean before any commit.
- Any external HTTP call is wrapped in a retry with backoff and a timeout. No bare `requests.get`.
- All money is `Decimal`, stored as `DecimalField(max_digits=10, decimal_places=2)`. Never float.
- All dates are timezone-aware. Store park rules with explicit `season_start`/`season_end`.
- When uncertain about a real-world fee or rule, do not guess — leave the field null, set
  `needs_verification=True`, and list it in the phase summary for confirmation.
