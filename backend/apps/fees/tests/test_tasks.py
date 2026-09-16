"""verify_fee_sources_weekly just calls the management command — confirm the wiring."""

from unittest.mock import patch

from apps.fees.tasks import verify_fee_sources_weekly


def test_calls_the_verify_fee_sources_command():
    with patch("apps.fees.tasks.call_command") as mock_call:
        verify_fee_sources_weekly()

    mock_call.assert_called_once_with("verify_fee_sources")
