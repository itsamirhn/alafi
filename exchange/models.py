import uuid
from typing import Self

from django.db import models


class User(models.Model):
    id = models.AutoField(primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)
    phone_number = models.CharField(max_length=11, unique=True)

    def __str__(self: Self) -> str:
        return f"User<{self.id}>"


class Coin(models.IntegerChoices):
    USD = 0, "USD"
    ABAN = 1, "Aban"


class Wallet(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    user = models.ForeignKey(User, on_delete=models.PROTECT)
    coin = models.SmallIntegerField(choices=Coin.choices)
    balance = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ("user", "coin")

    def __str__(self: Self) -> str:
        return f"Wallet<{self.id}>"


class Transaction(models.Model):
    class Status(models.IntegerChoices):
        PENDING = 0, "Pending"
        SETTLED = 1, "Settled"
        CANCELLED = 2, "Cancelled"

    class Direction(models.IntegerChoices):
        WITHDRAW = 0, "Withdraw"
        DEPOSIT = 1, "Deposit"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    wallet = models.ForeignKey(Wallet, on_delete=models.PROTECT)
    status = models.SmallIntegerField(choices=Status.choices, default=Status.PENDING)

    amount = models.PositiveIntegerField()
    direction = models.SmallIntegerField(choices=Direction.choices)

    def __str__(self: Self) -> str:
        return f"Transaction<{self.id}>"
