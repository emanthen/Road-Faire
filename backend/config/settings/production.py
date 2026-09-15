"""Production overrides: S3, CloudFront, Sentry, secure cookies, CORS allowlist."""

import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

from .base import *  # noqa: F403
from .base import SENTRY_DSN, env

DEBUG = False

SECURE_SSL_REDIRECT = True
# The ALB terminates TLS and forwards plain HTTP to the ECS tasks, so Django must trust
# the X-Forwarded-Proto header it sets rather than inspecting the (always-HTTP) request
# itself — otherwise SECURE_SSL_REDIRECT sees "http" forever and redirect-loops.
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = True
CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS", default=[])
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True

CLOUDFRONT_DOMAIN = env("CLOUDFRONT_DOMAIN", default="")
AWS_STORAGE_BUCKET_NAME = env("AWS_STORAGE_BUCKET_NAME", default="")
AWS_S3_REGION_NAME = env("AWS_S3_REGION_NAME", default="us-east-1")
STORAGES = {
    "default": {"BACKEND": "storages.backends.s3.S3Storage"},
    "staticfiles": {"BACKEND": "storages.backends.s3.S3StaticStorage"},
}

if SENTRY_DSN:
    sentry_sdk.init(dsn=SENTRY_DSN, integrations=[DjangoIntegration()], traces_sample_rate=0.1)
