import logging
from collections.abc import Iterator
from time import sleep
from typing import Any, Self

from django.core.management.base import BaseCommand
from django.db import transaction

from exchange import abc, models

logger = logging.getLogger(__name__)


class TransactionAggregator:
    def __init__(self: Self) -> None:
        self.MIN_ORDER = {
            models.Coin.ABAN.value: 10,
            models.Coin.USD.value: 0,
        }

    def __call__(self: Self, stream: Iterator[models.Transaction]) -> Iterator[list[models.Transaction]]:
        batch_by_coin: dict[int, list[models.Transaction]] = {}
        for t in stream:
            batch = batch_by_coin.get(t.wallet.coin, [])
            batch.append(t)
            batch_by_coin[t.wallet.coin] = batch

            if sum(t.amount for t in batch) >= self.MIN_ORDER[t.wallet.coin]:
                yield batch_by_coin.pop(t.wallet.coin)


class Command(BaseCommand):
    BATCH_SIZE = 100
    help = "Settle pending transactions"

    @classmethod
    def handle(cls: type[Self], *_args: Any, **_kwargs: Any) -> None:
        while True:
            with transaction.atomic():
                cls.settle_pending_transactions()
            sleep(1)

    @classmethod
    def settle_pending_transactions(cls: type[Self]) -> None:
        pending_transactions = (
            models.Transaction.objects.select_related("wallet")
            .filter(
                status=models.Transaction.Status.PENDING,
                direction=models.Transaction.Direction.DEPOSIT,
            )
            .select_for_update()
            .iterator(cls.BATCH_SIZE)
        )

        aggregator = TransactionAggregator()
        for batch in aggregator(pending_transactions):
            cls.settle(batch)

    @classmethod
    def settle(cls: type[Self], batch: list[models.Transaction]) -> None:
        assert len(batch) > 0
        coin = models.Coin(next(iter(batch)).wallet.coin)
        assert all(t.wallet.coin == coin for t in batch)

        amount = sum(t.amount for t in batch)
        if abc.buy_from_exchange(coin, amount):
            models.Transaction.objects.filter(
                pk__in=[t.pk for t in batch],
            ).update(
                status=models.Transaction.Status.SETTLED,
            )
            logger.info("Settled %s transactions", len(batch))
