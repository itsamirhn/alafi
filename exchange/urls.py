from django.urls import include, path
from rest_framework import routers

from exchange.views.api.v1 import PurchaseViewSet

api_v1_router = routers.SimpleRouter()
api_v1_router.register("purchase", PurchaseViewSet)

urlpatterns = [
    path("api/v1/", include(api_v1_router.urls)),
]
