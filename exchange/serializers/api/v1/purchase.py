from typing import Any, Self

from rest_framework import serializers

from exchange import models


class PurchaseSerializer(serializers.Serializer[dict[str, Any]]):
    coin = serializers.ChoiceField(choices=models.Coin.choices, required=True)
    amount = serializers.IntegerField(min_value=0, required=True)

    def create(self: Self, validated_data: dict[str, Any]) -> dict[str, Any]:  # noqa: ARG002
        return {}
