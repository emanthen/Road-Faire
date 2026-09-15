from django.urls import path

from apps.weather.views import weather

urlpatterns = [
    path("<slug:slug>", weather, name="weather"),
]
