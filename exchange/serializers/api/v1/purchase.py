from typing import Any, Self, cast

from django.db import transaction
from rest_framework import serializers

from exchange import abc, authentication, models


class InsufficientBalanceError(serializers.ValidationError):
    default_detail = "Insufficient balance"
    default_code = "insufficient_balance"


class PurchaseSerializer(serializers.Serializer[list[models.Transaction]]):
    coin = serializers.ChoiceField(choices=models.Coin.choices, required=True)
    amount = serializers.IntegerField(min_value=0, required=True)

    def context_user(self: Self) -> models.User:
        return cast(authentication.APIRequest, self.context["request"]).auth.user

    @transaction.atomic
    def create(self: Self, validated_data: dict[str, Any]) -> list[models.Transaction]:
        coin = validated_data["coin"]
        coin_amount = validated_data["amount"]
        usd_amount = coin_amount * abc.get_rate_by_usd(coin)

        wallets = (
            models.Wallet.objects.filter(
                user=self.context_user(),
                coin__in=[models.Coin.USD, coin],
            )
            .select_for_update()
            .all()
        )

        if coin_wallets := [w.coin == coin for w in wallets]:
            assert len(coin_wallets) == 1
            coin_wallet = coin_wallets[0]
        else:
            coin_wallet = models.Wallet(user=self.context_user(), coin=coin, balance=0)

        usd_wallet = next(w for w in wallets if w.coin == models.Coin.USD)

        if usd_wallet.balance < usd_amount:
            raise InsufficientBalanceError

        usd_wallet.balance -= usd_amount
        coin_wallet.balance += coin_amount

        usd_wallet.save()
        coin_wallet.save()

        usd_transaction = models.Transaction(
            wallet=usd_wallet,
            amount=usd_amount,
            direction=models.Transaction.Direction.WITHDRAW,
            status=models.Transaction.Status.PENDING,
        )

        coin_transaction = models.Transaction(
            wallet=coin_wallet,
            amount=coin_amount,
            direction=models.Transaction.Direction.DEPOSIT,
            status=models.Transaction.Status.PENDING,
        )

        usd_transaction.save()
        coin_transaction.save()

        return [usd_transaction, coin_transaction]
