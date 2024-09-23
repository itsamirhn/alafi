from typing import Any, Self, cast

from rest_framework import mixins, response, status, viewsets
from rest_framework.request import Request

from exchange import authentication
from exchange.serializers.api.v1 import PurchaseRequestSerializer
from exchange.trade import CoinTrader


class PurchaseViewSet(
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,  # type: ignore[type-arg]
):
    serializer_class = PurchaseRequestSerializer
    authentication_classes = (authentication.Authentication,)

    def create(self: Self, request: Request, *args: Any, **kwargs: Any) -> response.Response:  # noqa: ARG002
        request = cast(authentication.APIRequest, request)
        purchase = self.serializer_class(data=request.data)
        purchase.is_valid(raise_exception=True)
        data = purchase.validated_data
        CoinTrader(data["coin"]).trade(request.user, data["amount"])
        return response.Response(data={"ok": True}, status=status.HTTP_201_CREATED)
