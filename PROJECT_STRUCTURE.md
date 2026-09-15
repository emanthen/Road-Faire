# ROADFARE — PROJECT STRUCTURE

Monorepo. Django REST backend, Next.js frontend, Terraform infra.
Every file below is specified. Created as stubs in Phase 1, filled in by phase.

```
roadfare/
├── README.md
├── PROJECT_STRUCTURE.md
├── BUILD_PROMPT.md
├── .env.example
├── .gitignore
├── .dockerignore
├── docker-compose.yml
├── docker-compose.prod.yml
├── Makefile
└── .github/
    └── workflows/
        ├── backend-ci.yml
        ├── frontend-ci.yml
        └── deploy.yml
```

## BACKEND — Django 5.1 + DRF

```
backend/
├── Dockerfile
├── pyproject.toml                  ruff, mypy, pytest config; deps via uv
├── uv.lock
├── manage.py
├── pytest.ini
├── conftest.py                     shared fixtures: db, api_client, spot_factory
│
├── config/
│   ├── settings/
│   │   ├── base.py                 apps, DRF, PostGIS, Celery, structlog, spectacular
│   │   ├── local.py                DEBUG, django-extensions, silk
│   │   ├── test.py                 in-memory cache, eager Celery, fast hasher
│   │   └── production.py           S3, CloudFront, Sentry, secure cookies, CORS allowlist
│   ├── urls.py                     /api/ router, /schema/, /admin/, /go/
│   ├── celery.py                   app + beat schedule
│   ├── asgi.py
│   └── wsgi.py
│
├── apps/
│   ├── core/                       shared base — no business logic
│   │   ├── models.py               TimeStampedModel, SluggedModel, VerifiableModel
│   │   ├── fields.py               MoneyField (Decimal 10,2), URLSourceField
│   │   ├── mixins.py               CachedPropertyMixin, SoftDeleteQuerySet
│   │   ├── pagination.py           CursorPagination default
│   │   ├── exceptions.py           DRF handler -> structured error envelope
│   │   ├── http.py                 retrying session (timeout, backoff, UA) — use everywhere
│   │   ├── admin.py                base admin with verified_at column
│   │   └── views.py                /api/health, /api/version
│   │
│   ├── catalog/                    the spot database — the asset
│   │   ├── models/
│   │   │   ├── region.py           Region, State — hierarchy for browse pages
│   │   │   ├── spot.py             Spot: slug, geom(Point), type, min_days, vibe_tags,
│   │   │   │                       nearest_airports, blurb, is_manually_verified
│   │   │   ├── cost.py             SpotCost: entry_vehicle, entry_person, parking,
│   │   │   │                       campsite_low/high, shuttle, source_url, verified_at
│   │   │   ├── reservation.py      ReservationRule: kind(timed_entry|vehicle|permit|
│   │   │   │                       shuttle|lottery), season_start/end, window_start/end,
│   │   │   │                       booking_url, processing_fee, notes, verified_at
│   │   │   ├── vehicle_limit.py    VehicleLimit: max_length_ft, max_height_ft, max_weight_lb,
│   │   │   │                       effective_from, applies_to_roads[]
│   │   │   ├── climate.py          ClimateNormal: spot, month, high_f, low_f, precip_in, snow_in
│   │   │   ├── crowd.py            CrowdIndex: spot, month, score 0-100
│   │   │   ├── activity.py         Activity: trail/tour, distance, elevation, permit_required
│   │   │   ├── photo.py            Photo: source, credit, license, s3_key
│   │   │   └── drive_time.py       DriveTime: origin_code, spot, minutes, miles
│   │   ├── managers.py             SpotQuerySet.within_drive_of(), .best_in_month()
│   │   ├── scoring.py              month_score(spot, month) from climate + crowd + closures
│   │   ├── serializers.py
│   │   ├── views.py                read-only spot list/detail, filters, geo bbox search
│   │   ├── filters.py
│   │   ├── admin.py                inline editing, "mark verified" bulk action
│   │   ├── migrations/
│   │   └── tests/
│   │       ├── test_scoring.py
│   │       ├── test_managers.py
│   │       └── test_api.py
│   │
│   ├── fees/                       THE WEDGE — highest test bar in the repo
│   │   ├── constants.py            ATB_RESIDENT=80, ATB_NONRESIDENT=250,
│   │   │                           NONRESIDENT_SURCHARGE=100, SURCHARGE_PARK_SLUGS=[11],
│   │   │                           SURCHARGE_MIN_AGE=16, each with SOURCE_URL + EFFECTIVE_FROM
│   │   ├── models.py               FeeSchedule (versioned, effective_from/to), FeeFreeDay
│   │   ├── engine.py               entry_fees() -> EntryFeeBreakdown dataclass; pure, no ORM
│   │   ├── dataclasses.py          EntryFeeLine, EntryFeeBreakdown, PassRecommendation
│   │   ├── explain.py              human sentence for the recommendation, template-based
│   │   ├── serializers.py
│   │   ├── views.py                POST /api/fees/calculate
│   │   ├── admin.py
│   │   ├── migrations/
│   │   └── tests/
│   │       ├── test_engine.py      every case from BUILD_PROMPT §4.2 — 100% branch coverage
│   │       ├── test_breakeven.py   1/2/3+ adults across 1/2/3 surcharge parks
│   │       ├── test_children.py    under-16 free, mixed parties
│   │       └── test_api.py
│   │
│   ├── vehicles/                   campervan / RV / car
│   │   ├── models.py               VehicleClass, VehicleSpec (length, height, mpg,
│   │   │                           sleeps, included_miles_per_night, overage_rate)
│   │   ├── pricing.py              true_cost(spec, nights, miles, one_way) — itemised
│   │   ├── compatibility.py        vehicle_fits(spot, spec) -> Fit | Warning | Blocked
│   │   ├── serializers.py
│   │   ├── views.py                /api/vehicles/, /api/vehicles/size-check
│   │   ├── migrations/
│   │   └── tests/
│   │       ├── test_pricing.py     mileage overage, prep fee, one-way, hookup premium
│   │       └── test_compatibility.py   Zion 35'9" limit case
│   │
│   ├── weather/
│   │   ├── clients.py              OpenMeteoClient (forecast), cached 1h
│   │   ├── services.py             forecast_for(spot, date_range), normals_for(spot)
│   │   ├── views.py                /api/weather/<slug>
│   │   ├── tasks.py                warm cache for top 100 spots hourly
│   │   └── tests/test_services.py
│   │
│   ├── planner/                    itinerary + cost engine
│   │   ├── models.py               TripRequest, Itinerary, ItineraryDay, ItineraryStop,
│   │   │                           CostLine, SavedTrip
│   │   ├── engine/
│   │   │   ├── candidates.py       filter spots by radius + month_score
│   │   │   ├── clustering.py       build loops under max_drive_hours_per_day
│   │   │   ├── costing.py          transport + lodging + entry + fuel + food + activities
│   │   │   ├── tiers.py            LEAN / BALANCED / COMFORT presets
│   │   │   ├── budget.py           rank, filter to budget, 15% buffer
│   │   │   └── types.py            frozen dataclasses for all engine I/O
│   │   ├── narrative.py            Claude API call — PROSE ONLY, numbers injected, never generated
│   │   ├── pdf.py                  WeasyPrint itinerary export
│   │   ├── serializers.py
│   │   ├── views.py                POST /api/plan, GET /api/plan/<uuid>
│   │   ├── tasks.py                async plan generation for slow requests
│   │   ├── migrations/
│   │   └── tests/
│   │       ├── test_costing.py
│   │       ├── test_clustering.py
│   │       ├── test_budget.py
│   │       └── test_golden.py      fixed request -> fixed dollar total, byte-comparable
│   │
│   ├── ingest/                     external data in
│   │   ├── clients/
│   │   │   ├── base.py             rate limit, retry, ETag caching, fixture recording
│   │   │   ├── nps.py              parks, fees, alerts, hours
│   │   │   ├── ridb.py             campgrounds, permits, timed entry
│   │   │   ├── noaa.py             1991-2020 climate normals bulk loader
│   │   │   ├── overpass.py         trails, dump stations, water
│   │   │   ├── places.py           Google Places — cache 30 days, never on request path
│   │   │   └── osrm.py             drive-time matrix
│   │   ├── staging.py              StagedRecord model — raw payload + diff before promote
│   │   ├── promote.py              diff -> apply, respecting is_manually_verified
│   │   ├── tasks.py                Celery beat: nps_daily, ridb_daily, places_monthly
│   │   ├── management/commands/
│   │   │   ├── ingest_all.py
│   │   │   ├── ingest_nps.py
│   │   │   ├── ingest_ridb.py
│   │   │   ├── load_climate_normals.py
│   │   │   ├── build_drive_matrix.py
│   │   │   └── seed_spots.py       the hand-verified starter 25
│   │   ├── fixtures/               recorded HTTP responses for tests
│   │   └── tests/
│   │       ├── test_nps_client.py
│   │       ├── test_promote.py     asserts manual edits survive re-ingest
│   │       └── test_idempotent.py
│   │
│   ├── partners/                   monetisation
│   │   ├── models.py               Partner, Offer, Click, Conversion
│   │   ├── links.py                build_url(offer, spot, session) with tracking params
│   │   ├── views.py                /go/<uuid> -> record Click -> 302
│   │   ├── admin.py
│   │   ├── migrations/
│   │   └── tests/test_links.py
│   │
│   ├── leads/
│   │   ├── models.py               Lead, EmailEvent
│   │   ├── views.py                POST /api/leads (honeypot + rate limit)
│   │   ├── tasks.py                Resend send, welcome sequence
│   │   └── tests/
│   │
│   └── content/                    editorial + freshness surface
│       ├── models.py               Page, FAQ, ChangeLogEntry (what rule changed, when)
│       ├── views.py
│       ├── sitemap.py              feeds Next.js sitemap.ts
│       └── migrations/
│
└── scripts/
    ├── entrypoint.sh                migrate -> collectstatic -> gunicorn
    ├── wait_for_db.py
    └── verify_fees.py               prints every fee row older than 90 days
```

## FRONTEND — Next.js 15 App Router

```
frontend/
├── Dockerfile
├── package.json
├── tsconfig.json
├── next.config.ts
├── tailwind.config.ts              the six tokens from BUILD_PROMPT §5
├── postcss.config.mjs
├── components.json                 shadcn config
├── .eslintrc.json
├── playwright.config.ts
│
├── public/
│   ├── fonts/                      Overpass, Overpass Mono (self-hosted, subset)
│   ├── favicon.ico
│   └── og-default.png
│
└── src/
    ├── app/
    │   ├── layout.tsx               fonts, tokens, header, footer, PostHog, skip-link
    │   ├── page.tsx                 HOME — fee calculator is the hero, above the fold
    │   ├── globals.css              @theme tokens, base type scale, focus-visible ring
    │   ├── sitemap.ts               generated from /api/content/sitemap
    │   ├── robots.ts
    │   ├── opengraph-image.tsx
    │   ├── not-found.tsx
    │   ├── error.tsx
    │   │
    │   ├── spots/
    │   │   ├── page.tsx                     browse + map + filters
    │   │   └── [slug]/
    │   │       ├── layout.tsx               shared header, tabs, JSON-LD
    │   │       ├── page.tsx                 overview
    │   │       ├── cost/page.tsx            full fee table, resident toggle
    │   │       ├── best-time-to-visit/page.tsx   month table + climate chart
    │   │       ├── reservations/page.tsx    rules + verified_at banner
    │   │       ├── campervan/page.tsx       size limits, hookups, dump stations
    │   │       └── opengraph-image.tsx
    │   │
    │   ├── plan/
    │   │   ├── page.tsx                     multi-step request form
    │   │   ├── [id]/page.tsx                three costed options
    │   │   └── loading.tsx
    │   │
    │   ├── trips/
    │   │   ├── page.tsx
    │   │   └── [slug]/page.tsx              published itineraries
    │   │
    │   ├── tools/
    │   │   ├── national-park-fee-calculator/page.tsx   the viral tool, standalone
    │   │   ├── campervan-cost-calculator/page.tsx
    │   │   └── vehicle-size-checker/page.tsx
    │   │
    │   ├── guides/[slug]/page.tsx
    │   ├── about/page.tsx
    │   ├── disclosure/page.tsx              FTC affiliate disclosure
    │   └── api/
    │       └── revalidate/route.ts          webhook from Django on data change
    │
    ├── components/
    │   ├── ui/                              shadcn primitives
    │   ├── fee-calculator/
    │   │   ├── FeeCalculator.tsx            client component, the hero
    │   │   ├── ParkPicker.tsx
    │   │   ├── ResidencyToggle.tsx
    │   │   ├── PartySizeInput.tsx
    │   │   └── ResultPanel.tsx              count-up on change, reduced-motion safe
    │   ├── cost/
    │   │   ├── CostTable.tsx                hairline rules, mono right-aligned figures
    │   │   ├── CostLine.tsx
    │   │   ├── SurchargeCallout.tsx          sodium accent — the unexpected charge
    │   │   └── PassRecommendation.tsx
    │   ├── spot/
    │   │   ├── SpotHero.tsx
    │   │   ├── AtAGlance.tsx
    │   │   ├── MonthGrid.tsx                12-month best-time heat table
    │   │   ├── ClimateChart.tsx             Recharts
    │   │   ├── ReservationRules.tsx
    │   │   └── VerifiedAt.tsx               "Fees verified 14 Aug 2026"
    │   ├── vehicle/
    │   │   ├── SizeChecker.tsx
    │   │   ├── FitBadge.tsx                 fits / warning / blocked (signal red)
    │   │   └── VanCostBreakdown.tsx
    │   ├── planner/
    │   │   ├── TripForm.tsx
    │   │   ├── ItineraryCard.tsx            LEAN / BALANCED / COMFORT
    │   │   ├── DayTimeline.tsx
    │   │   └── ExportPdfButton.tsx
    │   ├── map/
    │   │   ├── SpotMap.tsx                  MapLibre + Protomaps
    │   │   └── RouteLayer.tsx
    │   ├── partners/
    │   │   ├── OfferLink.tsx                always routes through /go/
    │   │   └── DisclosureBanner.tsx
    │   └── layout/
    │       ├── Header.tsx
    │       ├── Footer.tsx
    │       └── SkipLink.tsx
    │
    ├── lib/
    │   ├── api.ts                   typed fetch wrapper, base URL, error envelope
    │   ├── schemas.ts               zod schemas mirroring every DRF serializer
    │   ├── money.ts                 formatUSD — never do arithmetic here
    │   ├── seo.ts                   metadata + JSON-LD builders
    │   ├── analytics.ts             PostHog events: fee_calculated, plan_created, offer_clicked
    │   └── utils.ts                 cn()
    │
    ├── hooks/
    │   ├── useFeeCalculator.ts
    │   ├── useCountUp.ts            respects prefers-reduced-motion
    │   └── useTripPlan.ts
    │
    ├── types/
    │   └── api.ts                   generated from OpenAPI schema
    │
    └── tests/
        ├── e2e/
        │   ├── fee-calculator.spec.ts
        │   ├── spot-pages.spec.ts
        │   └── plan-flow.spec.ts
        └── unit/
            └── money.test.ts
```

## INFRA

```
infra/
├── terraform/
│   ├── main.tf
│   ├── variables.tf
│   ├── outputs.tf
│   ├── modules/
│   │   ├── network/            VPC, subnets, NAT, security groups
│   │   ├── ecs/                cluster, backend + frontend + worker services, ALB
│   │   ├── rds/                Postgres 16 + PostGIS param group
│   │   ├── redis/              ElastiCache
│   │   ├── s3_cloudfront/      media + static
│   │   └── secrets/            SSM Parameter Store
│   └── envs/
│       ├── staging.tfvars
│       └── production.tfvars
└── docker/
    ├── nginx.conf
    └── postgres/init-postgis.sql
```

## PHASE-1 FILE COUNT

| Area | Files |
|---|---|
| Root + CI | 12 |
| Backend config | 10 |
| Backend apps | ~95 |
| Frontend | ~85 |
| Infra | ~20 |

Create all as stubs in Phase 1 — a stub is a file with correct imports, docstring stating its
responsibility, and `raise NotImplementedError` or a typed empty return. An empty tree that
imports cleanly is worth more than three finished features and no skeleton.
