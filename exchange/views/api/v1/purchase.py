import abc
from typing import Self

from django.db.models import QuerySet
from rest_framework import mixins, viewsets

from exchange import authentication, models
from exchange.serializers.api.v1 import PurchaseSerializer


class PurchaseViewSet(
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,  # type: ignore[type-arg]
    abc.ABC,
):
    serializer_class = PurchaseSerializer
    authentication_classes = (authentication.Authentication,)

    @abc.abstractmethod
    def get_user(self: Self) -> models.User: ...

    def get_queryset(self: Self) -> QuerySet[models.Transaction]:
        return models.Transaction.objects.filter(wallet__user=self.get_user()).select_related("wallet")
