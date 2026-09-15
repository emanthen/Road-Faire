"""mileage overage, prep fee, one-way, hookup premium."""

from decimal import Decimal

from apps.vehicles.pricing import Addon, VehicleSpecInput, true_cost


def _spec(**overrides) -> VehicleSpecInput:
    defaults = dict(
        length_ft=Decimal("22"),
        height_ft=Decimal("10"),
        included_miles_per_night=100,
        overage_rate_per_mile=Decimal("0.45"),
        base_nightly_rate=Decimal("150"),
        prep_fee=Decimal("75"),
        insurance_per_night=Decimal("25"),
        one_way_fee=Decimal("400"),
        generator_rate_per_hour=Decimal("5"),
        hookup_premium_per_night=Decimal("15"),
    )
    defaults.update(overrides)
    return VehicleSpecInput(**defaults)


def test_base_scales_with_nights():
    cost = true_cost(_spec(), nights=4, planned_miles=Decimal("300"), one_way=False)
    assert cost.base == Decimal("600")  # 150 * 4


def test_mileage_overage_only_charges_miles_past_included():
    # 4 nights * 100 included = 400 included miles; 300 planned miles is under that.
    under = true_cost(_spec(), nights=4, planned_miles=Decimal("300"), one_way=False)
    assert under.mileage_overage == Decimal("0")

    # 600 planned miles - 400 included = 200 overage miles * 0.45
    over = true_cost(_spec(), nights=4, planned_miles=Decimal("600"), one_way=False)
    assert over.mileage_overage == Decimal("90.00")


def test_prep_fee_is_one_time_not_per_night():
    cost = true_cost(_spec(), nights=5, planned_miles=Decimal("0"), one_way=False)
    assert cost.prep_fee == Decimal("75")  # not 75*5


def test_insurance_scales_with_nights():
    cost = true_cost(_spec(), nights=3, planned_miles=Decimal("0"), one_way=False)
    assert cost.insurance == Decimal("75")  # 25 * 3


def test_one_way_fee_only_when_pickup_neq_dropoff():
    same_location = true_cost(_spec(), nights=2, planned_miles=Decimal("0"), one_way=False)
    assert same_location.one_way_fee == Decimal("0")

    different_location = true_cost(_spec(), nights=2, planned_miles=Decimal("0"), one_way=True)
    assert different_location.one_way_fee == Decimal("400")


def test_hookup_premium_only_for_hookup_nights():
    cost = true_cost(
        _spec(), nights=5, planned_miles=Decimal("0"), one_way=False, hookup_nights=2
    )
    assert cost.hookup_premium == Decimal("30")  # 15 * 2, not 15 * 5


def test_generator_hours_are_optional_and_billed_by_the_hour():
    no_generator = true_cost(_spec(), nights=2, planned_miles=Decimal("0"), one_way=False)
    assert no_generator.generator == Decimal("0")

    with_generator = true_cost(
        _spec(), nights=2, planned_miles=Decimal("0"), one_way=False,
        generator_hours=Decimal("3"),
    )
    assert with_generator.generator == Decimal("15")  # 5 * 3


def test_addons_sum_into_the_total():
    cost = true_cost(
        _spec(),
        nights=2,
        planned_miles=Decimal("0"),
        one_way=False,
        addons=[Addon("propane", Decimal("20")), Addon("bedding kit", Decimal("30"))],
    )
    assert cost.addons == Decimal("50")


def test_total_is_the_sum_of_every_line_item():
    cost = true_cost(
        _spec(),
        nights=3,
        planned_miles=Decimal("500"),
        one_way=True,
        generator_hours=Decimal("2"),
        hookup_nights=1,
        addons=[Addon("camp chair", Decimal("10"))],
    )
    expected = (
        cost.base
        + cost.mileage_overage
        + cost.prep_fee
        + cost.insurance
        + cost.one_way_fee
        + cost.generator
        + cost.hookup_premium
        + cost.addons
    )
    assert cost.total == expected
