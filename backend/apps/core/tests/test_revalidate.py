"""notify_revalidate — no-op without a secret, swallows any request failure."""

from unittest.mock import MagicMock, patch

from apps.core.revalidate import notify_revalidate


def test_noops_without_a_secret():
    with (
        patch("apps.core.revalidate.settings.REVALIDATE_SECRET", ""),
        patch("apps.core.revalidate.get_session") as mock_get_session,
    ):
        notify_revalidate("spot", "zion")

    mock_get_session.assert_not_called()


def test_posts_kind_and_slug_with_the_shared_secret_header():
    mock_session = MagicMock()
    with (
        patch("apps.core.revalidate.settings.REVALIDATE_SECRET", "shh"),
        patch("apps.core.revalidate.settings.FRONTEND_BASE_URL", "https://roadfare.com"),
        patch("apps.core.revalidate.get_session", return_value=mock_session),
    ):
        notify_revalidate("spot", "zion")

    mock_session.post.assert_called_once_with(
        "https://roadfare.com/api/revalidate",
        json={"kind": "spot", "slug": "zion"},
        headers={"x-revalidate-secret": "shh"},
        timeout=5,
    )


def test_swallows_a_request_failure():
    mock_session = MagicMock()
    mock_session.post.side_effect = ConnectionError("down")
    with (
        patch("apps.core.revalidate.settings.REVALIDATE_SECRET", "shh"),
        patch("apps.core.revalidate.get_session", return_value=mock_session),
    ):
        notify_revalidate("spot", "zion")  # must not raise
