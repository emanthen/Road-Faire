from django.urls import path

from apps.fees.views import calculate

urlpatterns = [
    path("calculate", calculate, name="fees-calculate"),
]
