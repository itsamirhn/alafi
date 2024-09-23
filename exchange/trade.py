from typing import Self

from django.db import transaction
from rest_framework import exceptions

from exchange import abc, models


class InsufficientBalanceError(exceptions.ValidationError):
    default_detail = "Insufficient balance"
    default_code = "insufficient_balance"


class CoinTrader:
    def __init__(self: Self, coin: models.Coin) -> None:
        assert coin != models.Coin.USD
        self.coin = coin

    def _get_rate_by_usd(self: Self) -> int:
        return abc.get_rate_by_usd(self.coin)

    @transaction.atomic
    def trade(self: Self, user: models.User, amount: int) -> tuple[models.Transaction, models.Transaction]:
        assert amount > 0

        usd_amount = amount * self._get_rate_by_usd()

        wallets = (
            models.Wallet.objects.filter(
                user=user,
                coin__in=[models.Coin.USD, self.coin],
            )
            .select_for_update()
            .all()
        )

        if coin_wallets := [w for w in wallets if w.coin == self.coin]:
            assert len(coin_wallets) == 1
            coin_wallet = coin_wallets[0]
        else:
            coin_wallet = models.Wallet(user=user, coin=self.coin, balance=0)

        usd_wallet = next(w for w in wallets if w.coin == models.Coin.USD)

        if usd_wallet.balance < usd_amount:
            raise InsufficientBalanceError

        usd_wallet.balance -= usd_amount
        coin_wallet.balance += amount

        usd_wallet.save()
        coin_wallet.save()

        usd_transaction = models.Transaction(
            wallet=usd_wallet,
            amount=usd_amount,
            direction=models.Transaction.Direction.WITHDRAW,
            status=models.Transaction.Status.SETTLED,
        )

        coin_transaction = models.Transaction(
            wallet=coin_wallet,
            amount=amount,
            direction=models.Transaction.Direction.DEPOSIT,
            status=models.Transaction.Status.PENDING,
        )

        usd_transaction.save()
        coin_transaction.save()

        return usd_transaction, coin_transaction
