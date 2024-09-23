from typing import Self
from unittest.mock import Mock, patch

from django.test import TestCase
from model_bakery import baker

from exchange import models
from exchange.management.commands.run_transaction_settler import Command


class TestSettle(TestCase):
    @patch("exchange.abc.minimum_settlement_threshold", lambda _: 4)
    @patch("exchange.abc.buy_from_exchange")
    def test_not_settle_bellow_threshold(self: Self, buy_from_exchange: Mock) -> None:
        wallet = baker.make(models.Wallet, coin=models.Coin.ABAN)
        baker.make(
            models.Transaction,
            wallet=wallet,
            amount=1,
            status=models.Transaction.Status.PENDING,
            direction=models.Transaction.Direction.DEPOSIT,
        )
        baker.make(
            models.Transaction,
            wallet=wallet,
            amount=2,
            status=models.Transaction.Status.PENDING,
            direction=models.Transaction.Direction.DEPOSIT,
        )

        Command.settle_pending_transactions()

        assert models.Transaction.objects.filter(status=models.Transaction.Status.SETTLED).count() == 0
        assert buy_from_exchange.call_count == 0

    @patch("exchange.abc.minimum_settlement_threshold", lambda _: 4)
    @patch("exchange.abc.buy_from_exchange")
    def test_settle_above_threshold(self: Self, buy_from_exchange: Mock) -> None:
        wallet = baker.make(models.Wallet, coin=models.Coin.ABAN)
        baker.make(
            models.Transaction,
            wallet=wallet,
            amount=1,
            status=models.Transaction.Status.PENDING,
            direction=models.Transaction.Direction.DEPOSIT,
        )
        baker.make(
            models.Transaction,
            wallet=wallet,
            amount=2,
            status=models.Transaction.Status.PENDING,
            direction=models.Transaction.Direction.DEPOSIT,
        )
        baker.make(
            models.Transaction,
            wallet=wallet,
            amount=3,
            status=models.Transaction.Status.PENDING,
            direction=models.Transaction.Direction.DEPOSIT,
        )

        Command.settle_pending_transactions()

        assert models.Transaction.objects.filter(status=models.Transaction.Status.SETTLED).count() == 3  # noqa: PLR2004
        assert buy_from_exchange.call_count == 1
