"""diff -> apply, respecting is_manually_verified.

Field-mapping from a source's raw payload to model fields is the ingest command's job
(it knows the NPS/RIDB/NOAA response shape); promote_fields() only does the generic part:
apply values onto a VerifiableModel instance without clobbering a hand-verified row, and
report what actually changed.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class PromoteResult:
    changed_fields: dict[str, tuple[Any, Any]] = field(default_factory=dict)  # field -> (old, new)
    skipped_reason: str | None = None  # e.g. "manually_verified"

    @property
    def changed(self) -> bool:
        return bool(self.changed_fields)


def promote_fields(target: Any, field_values: dict[str, Any]) -> PromoteResult:
    """Apply field_values onto target in place, unless target.is_manually_verified is True.

    target must have an `is_manually_verified` attribute (any apps.core.models.VerifiableModel
    subclass). Doesn't call target.save() — the caller controls the transaction.
    """
    if getattr(target, "is_manually_verified", False):
        return PromoteResult(skipped_reason="manually_verified")

    result = PromoteResult()
    for field_name, new_value in field_values.items():
        old_value = getattr(target, field_name, None)
        if old_value != new_value:
            result.changed_fields[field_name] = (old_value, new_value)
            setattr(target, field_name, new_value)
    return result
