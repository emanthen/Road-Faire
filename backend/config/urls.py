"""/api/ router, /schema/, /admin/, /go/.

apps.core (health/version), apps.catalog (read-only spots), apps.fees (fee calculator),
apps.partners (/api/partners/ read-only vendor listing, /go/ redirector), apps.leads (lead
capture), apps.vehicles (pricing/compatibility), apps.content (pages/FAQs/sitemap),
apps.weather (forecast/normals), apps.planner (trip planning), and apps.dashboard
(staff-only CRUD for the Next.js /dashboard admin UI) are wired.
"""

from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/", include("apps.accounts.urls")),
    path("api/", include("apps.core.urls")),
    path("api/spots/", include("apps.catalog.urls")),
    path("api/fees/", include("apps.fees.urls")),
    path("api/leads/", include("apps.leads.urls")),
    path("api/vehicles/", include("apps.vehicles.urls")),
    path("api/content/", include("apps.content.urls")),
    path("api/weather/", include("apps.weather.urls")),
    path("api/plan/", include("apps.planner.urls")),
    path("api/partners/", include("apps.partners.api_urls")),
    path("api/admin/", include("apps.dashboard.urls")),
    path("go/", include("apps.partners.urls")),
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
]
