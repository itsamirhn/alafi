from rest_framework import serializers

from exchange import models


class NotSupportedCoinError(serializers.ValidationError):
    default_detail = "Not supported coin"
    default_code = "not_supported_coin"


def non_usd_coin_validator(coin: models.Coin) -> None:
    if coin == models.Coin.USD:
        raise NotSupportedCoinError


class PurchaseRequestSerializer(serializers.Serializer):  # type: ignore[type-arg]
    coin = serializers.ChoiceField(choices=models.Coin.choices, required=True, validators=[non_usd_coin_validator])
    amount = serializers.IntegerField(min_value=1, required=True)
