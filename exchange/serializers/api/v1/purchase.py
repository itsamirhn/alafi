from typing import Any, Self

from rest_framework import serializers

from exchange import models


class NotSupportedCoinError(serializers.ValidationError):
    default_detail = "Not supported coin"
    default_code = "not_supported_coin"


def non_usd_coin_validator(coin: models.Coin) -> None:
    if coin == models.Coin.USD:
        raise NotSupportedCoinError


class CoinField(serializers.Field):  # type: ignore[type-arg]
    def to_representation(self: Self, value: models.Coin) -> str:
        return value.name

    def to_internal_value(self: Self, value: Any) -> models.Coin:
        for k, v in models.Coin.choices:
            if isinstance(value, str) and v.lower() == value.lower():
                return models.Coin(k)
        raise NotSupportedCoinError


class PurchaseRequestSerializer(serializers.Serializer):  # type: ignore[type-arg]
    coin = CoinField(required=True, validators=[non_usd_coin_validator])
    amount = serializers.IntegerField(min_value=1, required=True)
