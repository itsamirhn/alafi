import abc

from rest_framework import mixins, viewsets

from exchange import authentication
from exchange.serializers.api.v1 import PurchaseSerializer


class PurchaseViewSet(
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,  # type: ignore[type-arg]
    abc.ABC,
):
    serializer_class = PurchaseSerializer
    authentication_classes = (authentication.Authentication,)
