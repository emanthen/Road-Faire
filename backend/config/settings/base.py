"""Shared settings: apps, DRF, PostGIS, Celery, structlog, drf-spectacular."""

import os
from pathlib import Path

import environ
import structlog
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

BASE_DIR = Path(__file__).resolve().parent.parent.parent

env = environ.Env()
environ.Env.read_env(BASE_DIR.parent / ".env")

SECRET_KEY = env("DJANGO_SECRET_KEY", default="changeme-local-only")
DEBUG = env.bool("DJANGO_DEBUG", default=False)
ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", default=["localhost", "127.0.0.1"])

INSTALLED_APPS = [
    "unfold",
    "unfold.contrib.filters",
    "unfold.contrib.forms",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.gis",
    "rest_framework",
    "rest_framework.authtoken",
    "django_filters",
    "drf_spectacular",
    "corsheaders",
    "apps.core",
    "apps.accounts",
    "apps.catalog",
    "apps.fees",
    "apps.vehicles",
    "apps.weather",
    "apps.planner",
    "apps.ingest",
    "apps.partners",
    "apps.leads",
    "apps.content",
    "apps.dashboard",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

DATABASES = {
    "default": env.db(
        "DATABASE_URL",
        default=(
            f"postgis://{env('POSTGRES_USER', default='roadfare')}:"
            f"{env('POSTGRES_PASSWORD', default='roadfare')}@"
            f"{env('POSTGRES_HOST', default='localhost')}:"
            f"{env('POSTGRES_PORT', default='5432')}/"
            f"{env('POSTGRES_DB', default='roadfare')}"
        ),
    )
}
DATABASES["default"]["ENGINE"] = "django.contrib.gis.db.backends.postgis"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

REST_FRAMEWORK = {
    "DEFAULT_PAGINATION_CLASS": "apps.core.pagination.DefaultCursorPagination",
    "DEFAULT_FILTER_BACKENDS": ["django_filters.rest_framework.DjangoFilterBackend"],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "EXCEPTION_HANDLER": "apps.core.exceptions.structured_exception_handler",
    "PAGE_SIZE": 20,
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.TokenAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ],
    # /api/fees/calculate, /api/plan and /api/leads are public and otherwise unthrottled;
    # /api/plan will soon call a paid LLM API per request. AnonRateThrottle caps all
    # anonymous traffic; ScopedRateThrottle adds a tighter per-endpoint cap wherever a
    # view sets `throttle_scope`.
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.ScopedRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": "120/hour",
        "fees": "60/hour",
        "plan": "10/hour",
        "leads": "5/hour",
    },
}

# The Next.js frontend runs on a different origin (localhost:3000 in dev), so every
# environment needs CORS_ALLOWED_ORIGINS naming it explicitly.
CORS_ALLOWED_ORIGINS = env.list("CORS_ALLOWED_ORIGINS", default=["http://localhost:3000"])

SPECTACULAR_SETTINGS = {
    "TITLE": "Roadfare API",
    "DESCRIPTION": "Cost-transparent US road-trip planning.",
    "VERSION": "0.1.0",
}

# --- Admin dashboard (django-unfold) — sidebar grouped by content domain rather than
# Django's default per-app listing, so staff can find "the vendor" or "the article"
# without knowing which app it lives in. ---
UNFOLD = {
    "SITE_TITLE": "Roadfare Admin",
    "SITE_HEADER": "Roadfare",
    "SITE_SYMBOL": "map",
    "SHOW_HISTORY": True,
    "SHOW_VIEW_ON_SITE": True,
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": False,
        "navigation": [
            {
                "title": _("Dashboard"),
                "separator": False,
                "items": [
                    {
                        "title": _("Overview"),
                        "icon": "dashboard",
                        "link": reverse_lazy("admin:index"),
                    },
                ],
            },
            {
                "title": _("Spots & Catalog"),
                "separator": True,
                "items": [
                    {
                        "title": _("Spots"),
                        "icon": "location_on",
                        "link": reverse_lazy("admin:catalog_spot_changelist"),
                    },
                    {
                        "title": _("Amenities"),
                        "icon": "water_drop",
                        "link": reverse_lazy("admin:catalog_spotamenity_changelist"),
                    },
                    {
                        "title": _("Activities"),
                        "icon": "hiking",
                        "link": reverse_lazy("admin:catalog_activity_changelist"),
                    },
                    {
                        "title": _("Regions"),
                        "icon": "public",
                        "link": reverse_lazy("admin:catalog_region_changelist"),
                    },
                    {
                        "title": _("States"),
                        "icon": "flag",
                        "link": reverse_lazy("admin:catalog_state_changelist"),
                    },
                    {
                        "title": _("Climate normals"),
                        "icon": "thermostat",
                        "link": reverse_lazy("admin:catalog_climatenormal_changelist"),
                    },
                    {
                        "title": _("Crowd index"),
                        "icon": "groups",
                        "link": reverse_lazy("admin:catalog_crowdindex_changelist"),
                    },
                    {
                        "title": _("Drive times"),
                        "icon": "directions_car",
                        "link": reverse_lazy("admin:catalog_drivetime_changelist"),
                    },
                ],
            },
            {
                "title": _("Vendors & Partners"),
                "separator": True,
                "items": [
                    {
                        "title": _("Vendors"),
                        "icon": "storefront",
                        "link": reverse_lazy("admin:partners_partner_changelist"),
                    },
                    {
                        "title": _("Offers"),
                        "icon": "local_offer",
                        "link": reverse_lazy("admin:partners_offer_changelist"),
                    },
                    {
                        "title": _("Clicks"),
                        "icon": "ads_click",
                        "link": reverse_lazy("admin:partners_click_changelist"),
                    },
                    {
                        "title": _("Conversions"),
                        "icon": "paid",
                        "link": reverse_lazy("admin:partners_conversion_changelist"),
                    },
                ],
            },
            {
                "title": _("Articles, SEO & Site"),
                "separator": True,
                "items": [
                    {
                        "title": _("Articles / guides"),
                        "icon": "article",
                        "link": reverse_lazy("admin:content_page_changelist"),
                    },
                    {
                        "title": _("FAQs"),
                        "icon": "quiz",
                        "link": reverse_lazy("admin:content_faq_changelist"),
                    },
                    {
                        "title": _("Change log"),
                        "icon": "history_edu",
                        "link": reverse_lazy("admin:content_changelogentry_changelist"),
                    },
                    {
                        "title": _("Site settings"),
                        "icon": "settings",
                        "link": reverse_lazy("admin:content_sitesettings_changelist"),
                    },
                ],
            },
            {
                "title": _("Fees & Vehicles"),
                "separator": True,
                "items": [
                    {
                        "title": _("Fee schedules"),
                        "icon": "receipt_long",
                        "link": reverse_lazy("admin:fees_feeschedule_changelist"),
                    },
                    {
                        "title": _("Fee-free days"),
                        "icon": "event_available",
                        "link": reverse_lazy("admin:fees_feefreeday_changelist"),
                    },
                    {
                        "title": _("Vehicle classes"),
                        "icon": "rv_hookup",
                        "link": reverse_lazy("admin:vehicles_vehicleclass_changelist"),
                    },
                    {
                        "title": _("Vehicle specs"),
                        "icon": "directions_bus",
                        "link": reverse_lazy("admin:vehicles_vehiclespec_changelist"),
                    },
                ],
            },
            {
                "title": _("Trip Planner"),
                "separator": True,
                "items": [
                    {
                        "title": _("Trip requests"),
                        "icon": "route",
                        "link": reverse_lazy("admin:planner_triprequest_changelist"),
                    },
                    {
                        "title": _("Itineraries"),
                        "icon": "map",
                        "link": reverse_lazy("admin:planner_itinerary_changelist"),
                    },
                    {
                        "title": _("Saved trips"),
                        "icon": "bookmark",
                        "link": reverse_lazy("admin:planner_savedtrip_changelist"),
                    },
                ],
            },
            {
                "title": _("Leads & Accounts"),
                "separator": True,
                "items": [
                    {
                        "title": _("Leads"),
                        "icon": "mail",
                        "link": reverse_lazy("admin:leads_lead_changelist"),
                    },
                    {
                        "title": _("Users"),
                        "icon": "person",
                        "link": reverse_lazy("admin:auth_user_changelist"),
                    },
                    {
                        "title": _("Groups"),
                        "icon": "group",
                        "link": reverse_lazy("admin:auth_group_changelist"),
                    },
                ],
            },
        ],
    },
}

# --- Celery ---
CELERY_BROKER_URL = env("CELERY_BROKER_URL", default="redis://localhost:6379/0")
CELERY_RESULT_BACKEND = env("CELERY_RESULT_BACKEND", default="redis://localhost:6379/1")
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = TIME_ZONE

# --- structlog ---
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {
            "()": "structlog.stdlib.ProcessorFormatter",
            "processor": structlog.processors.JSONRenderer(),
        },
    },
    "handlers": {
        "console": {"class": "logging.StreamHandler", "formatter": "json"},
    },
    "root": {"handlers": ["console"], "level": "INFO"},
}

structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
    ],
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

SENTRY_DSN = env("SENTRY_DSN", default="")

# --- apps.ingest connector credentials ---
NPS_API_KEY = env("NPS_API_KEY", default="")
RIDB_API_KEY = env("RIDB_API_KEY", default="")
EIA_API_KEY = env("EIA_API_KEY", default="")

# --- apps.leads ---
RESEND_API_KEY = env("RESEND_API_KEY", default="")

# --- apps.accounts: "Sign in with Google" verifies the ID token's audience against
# this. Get a real value from https://console.cloud.google.com/apis/credentials
# (OAuth client ID, type "Web application") — there is no working default. ---
GOOGLE_OAUTH_CLIENT_ID = env("GOOGLE_OAUTH_CLIENT_ID", default="")

# GeoDjango needs the native GDAL/GEOS libraries. On Windows these aren't found via the
# usual ctypes.util.find_library() lookup, so point at them explicitly when present
# (installed via `winget install GISInternals.GDAL`). No-op on Linux (apt-get gdal-bin
# in the Dockerfile, or the postgis/postgis image, already put these on the loader path).
# ponytail: hardcoded to GISInternals' default install path (C:\Program Files\GDAL) --
# breaks if GDAL is installed elsewhere or a version bump changes it. Real upgrade path
# is Docker (docker-compose.yml's postgis/postgis image sidesteps native GDAL entirely);
# this only exists for native Windows dev while Docker is deferred.
if os.name == "nt":
    _gdal_dll = r"C:\Program Files\GDAL\gdal.dll"
    if os.path.exists(_gdal_dll):
        GDAL_LIBRARY_PATH = _gdal_dll
    _geos_dll = r"C:\Program Files\GDAL\geos_c.dll"
    if os.path.exists(_geos_dll):
        GEOS_LIBRARY_PATH = _geos_dll

    # WeasyPrint (apps.planner.pdf) loads Pango/GObject via cffi's dlopen, which uses the
    # OS loader search path, not GDAL_LIBRARY_PATH. Installed via
    # `winget install tschoonj.GTKForWindows`. Same ponytail as above: hardcoded default
    # install path, no-op and unnecessary on Linux (apt-get libpango-1.0-0 in the Dockerfile).
    _gtk_bin = r"C:\Program Files\GTK3-Runtime Win64\bin"
    if os.path.isdir(_gtk_bin) and _gtk_bin not in os.environ["PATH"]:
        os.environ["PATH"] = _gtk_bin + os.pathsep + os.environ["PATH"]
