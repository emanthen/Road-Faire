from django.urls import path

from apps.partners.views import go

urlpatterns = [
    path("<uuid:offer_id>", go, name="go"),
]
