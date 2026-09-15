from django.urls import path

from apps.leads.views import create_lead

urlpatterns = [
    path("", create_lead, name="leads-create"),
]
