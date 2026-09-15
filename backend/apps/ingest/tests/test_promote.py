"""Asserts manual edits survive re-ingest."""

from dataclasses import dataclass

from apps.ingest.promote import promote_fields


@dataclass
class _FakeVerifiable:
    """Stands in for a VerifiableModel instance without needing the DB."""

    is_manually_verified: bool
    name: str = ""
    entry_vehicle: float | None = None


def test_promote_applies_changed_fields_when_not_verified():
    target = _FakeVerifiable(is_manually_verified=False, name="Old Name", entry_vehicle=30.0)

    result = promote_fields(target, {"name": "New Name", "entry_vehicle": 35.0})

    assert result.changed
    assert target.name == "New Name"
    assert target.entry_vehicle == 35.0
    assert result.changed_fields["name"] == ("Old Name", "New Name")


def test_promote_skips_manually_verified_target():
    target = _FakeVerifiable(is_manually_verified=True, name="Hand-checked", entry_vehicle=35.0)

    result = promote_fields(target, {"name": "Would-be overwrite", "entry_vehicle": 999.0})

    assert not result.changed
    assert result.skipped_reason == "manually_verified"
    assert target.name == "Hand-checked"
    assert target.entry_vehicle == 35.0


def test_promote_reports_no_change_when_values_match():
    target = _FakeVerifiable(is_manually_verified=False, name="Same", entry_vehicle=35.0)

    result = promote_fields(target, {"name": "Same", "entry_vehicle": 35.0})

    assert not result.changed
    assert result.changed_fields == {}
