import django_filters

from apps.catalog.models import Spot


class SpotFilter(django_filters.FilterSet):
    state = django_filters.CharFilter(field_name="state__abbreviation", lookup_expr="iexact")
    type = django_filters.CharFilter(field_name="type", lookup_expr="exact")
    vibe = django_filters.CharFilter(field_name="vibe_tags", lookup_expr="contains")
    activity = django_filters.CharFilter(
        field_name="activities__kind", lookup_expr="exact", distinct=True
    )

    class Meta:
        model = Spot
        fields = ["state", "type", "vibe", "activity"]
