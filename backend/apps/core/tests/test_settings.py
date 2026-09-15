"""Guards the production-only settings that keep Django correct behind the ALB.

Imported directly (not via DJANGO_SETTINGS_MODULE) so this runs under any settings
module without needing a second pytest-django configuration.
"""

import importlib


def test_production_trusts_the_alb_forwarded_proto_header():
    production = importlib.import_module("config.settings.production")

    assert production.SECURE_PROXY_SSL_HEADER == ("HTTP_X_FORWARDED_PROTO", "https")
    assert production.USE_X_FORWARDED_HOST is True
    assert production.SECURE_SSL_REDIRECT is True


def test_production_csrf_trusted_origins_is_configurable():
    production = importlib.import_module("config.settings.production")

    assert hasattr(production, "CSRF_TRUSTED_ORIGINS")
    assert isinstance(production.CSRF_TRUSTED_ORIGINS, list)
