"""POST /api/auth/register, /login, /google, /logout, GET /api/auth/me — token auth
via DRF's built-in rest_framework.authtoken (no new dependency)."""

from django.conf import settings
from django.contrib.auth.models import User
from google.auth.exceptions import GoogleAuthError
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token as google_id_token
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import APIException, AuthenticationFailed
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from apps.accounts.serializers import (
    GoogleLoginSerializer,
    LoginSerializer,
    RegisterSerializer,
    UserSerializer,
)


@api_view(["POST"])
@permission_classes([AllowAny])
def register(request):
    serializer = RegisterSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.save()
    token, _ = Token.objects.get_or_create(user=user)
    return Response({"token": token.key, "user": UserSerializer(user).data}, status=201)


@api_view(["POST"])
@permission_classes([AllowAny])
def login(request):
    serializer = LoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.validated_data["user"]
    token, _ = Token.objects.get_or_create(user=user)
    return Response({"token": token.key, "user": UserSerializer(user).data})


class GoogleNotConfigured(APIException):
    status_code = 503
    default_detail = "Sign in with Google isn't configured on this server."
    default_code = "not_configured"


@api_view(["POST"])
@permission_classes([AllowAny])
def google_login(request):
    if not settings.GOOGLE_OAUTH_CLIENT_ID:
        raise GoogleNotConfigured()

    serializer = GoogleLoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    try:
        claims = google_id_token.verify_oauth2_token(
            serializer.validated_data["id_token"],
            google_requests.Request(),
            settings.GOOGLE_OAUTH_CLIENT_ID,
        )
    except (ValueError, GoogleAuthError) as exc:
        raise AuthenticationFailed(f"Invalid Google token: {exc}") from exc

    email = claims.get("email")
    if not email:
        raise AuthenticationFailed("Google account has no email.")

    # Match by email so someone who registered directly and later uses "Sign in with
    # Google" with the same address lands in the same account, not a duplicate one.
    user, created = User.objects.get_or_create(
        email=email,
        defaults={"username": email, "first_name": claims.get("given_name", "")},
    )
    if created:
        user.set_unusable_password()
        user.save()

    token, _ = Token.objects.get_or_create(user=user)
    return Response({"token": token.key, "user": UserSerializer(user).data})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout(request):
    request.user.auth_token.delete()
    return Response(status=204)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def me(request):
    return Response(UserSerializer(request.user).data)
