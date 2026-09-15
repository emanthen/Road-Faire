from django.urls import path

from apps.accounts.views import google_login, login, logout, me, register

urlpatterns = [
    path("register", register, name="register"),
    path("login", login, name="login"),
    path("google", google_login, name="google-login"),
    path("logout", logout, name="logout"),
    path("me", me, name="me"),
]
