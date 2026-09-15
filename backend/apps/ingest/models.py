"""Django only auto-discovers models via <app>/models.py — the actual StagedRecord
definition lives in staging.py per PROJECT_STRUCTURE.md; re-exported here so the app
registry finds it."""

from apps.ingest.staging import StagedRecord

__all__ = ["StagedRecord"]
