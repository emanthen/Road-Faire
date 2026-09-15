from django.urls import path

from apps.planner.views import (
    create_plan,
    get_plan,
    get_plan_pdf,
    get_plan_waypoints,
    list_featured_plans,
)

urlpatterns = [
    path("", create_plan, name="plan-create"),
    path("featured", list_featured_plans, name="plan-featured"),
    path("<uuid:plan_id>", get_plan, name="plan-detail"),
    path("<uuid:plan_id>/pdf", get_plan_pdf, name="plan-pdf"),
    path("<uuid:plan_id>/waypoints", get_plan_waypoints, name="plan-waypoints"),
]
