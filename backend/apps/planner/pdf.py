"""WeasyPrint itinerary export. Renders apps/planner/templates/planner/itinerary_pdf.html
against already-fetched Itinerary rows — no fresh DB/engine calls, no LLM, just layout."""

from django.template.loader import render_to_string

from apps.planner.models import Itinerary, TripRequest


def render_itinerary_pdf(trip_request: TripRequest, itineraries: list[Itinerary]) -> bytes:
    # Imported lazily: weasyprint dlopen's Pango/GObject on import, and apps.planner.views
    # (hence this module) loads on every manage.py invocation via Django's URL system
    # checks — a top-level import paid that cost on every command, not just PDF requests.
    from weasyprint import HTML

    html = render_to_string(
        "planner/itinerary_pdf.html",
        {"trip_request": trip_request, "itineraries": itineraries},
    )
    return HTML(string=html).write_pdf()
