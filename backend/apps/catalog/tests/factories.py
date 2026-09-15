import factory
from django.contrib.gis.geos import Point

from apps.catalog.models import ClimateNormal, CrowdIndex, Region, Spot, SpotCost, State


class RegionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Region

    name = factory.Sequence(lambda n: f"Region {n}")
    slug = factory.Sequence(lambda n: f"region-{n}")


class StateFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = State

    name = factory.Sequence(lambda n: f"State {n}")
    # 2-letter combos AA..ZZ (676 unique values) — the previous f"S{n:02d}"[:2] scheme
    # collided as soon as n reached double digits (S10 and S11 both truncated to "S1").
    abbreviation = factory.Sequence(lambda n: f"{chr(65 + n // 26 % 26)}{chr(65 + n % 26)}")
    region = factory.SubFactory(RegionFactory)


class SpotFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Spot

    name = factory.Sequence(lambda n: f"Test Spot {n}")
    slug = factory.Sequence(lambda n: f"test-spot-{n}")
    state = factory.SubFactory(StateFactory)
    type = Spot.SpotType.NATIONAL_PARK
    geom = Point(-110.5885, 44.4280)
    min_days = 2


class SpotCostFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = SpotCost

    spot = factory.SubFactory(SpotFactory)
    entry_vehicle = "35.00"


class ClimateNormalFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ClimateNormal

    spot = factory.SubFactory(SpotFactory)
    month = 7
    high_f = "80.0"
    low_f = "50.0"
    precip_in = "1.0"
    snow_in = "0.0"


class CrowdIndexFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CrowdIndex

    spot = factory.SubFactory(SpotFactory)
    month = 7
    score = 50
