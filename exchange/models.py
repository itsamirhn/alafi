import uuid
from typing import Self, Any

from django.contrib.auth import base_user
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class User(base_user.AbstractBaseUser):
    phone_number = models.CharField(max_length=11, unique=True, db_index=True)
    USERNAME_FIELD = "phone_number"
    REQUIRED_FIELDS = ["phone_number"]  # noqa: RUF012

    def __str__(self: Self) -> str:
        return f"{self.phone_number}"


class Coin(models.IntegerChoices):
    USD = 0, "USD"
    ABAN = 1, "Aban"


class Wallet(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    user = models.ForeignKey(User, on_delete=models.PROTECT)
    coin = models.SmallIntegerField(choices=Coin.choices)
    balance = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ("user", "coin")

    def __str__(self: Self) -> str:
        return f"{self.id}"


class Transaction(models.Model):
    class Status(models.IntegerChoices):
        PENDING = 0, "Pending"
        SETTLED = 1, "Settled"
        CANCELLED = 2, "Cancelled"

    class Direction(models.IntegerChoices):
        WITHDRAW = 0, "Withdraw"
        DEPOSIT = 1, "Deposit"

    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    wallet = models.ForeignKey(Wallet, on_delete=models.PROTECT)
    status = models.SmallIntegerField(choices=Status.choices, default=Status.PENDING)

    amount = models.PositiveIntegerField()
    direction = models.SmallIntegerField(choices=Direction.choices)

    def __str__(self: Self) -> str:
        return f"{self.id}"


@receiver(post_save, sender=User)
def add_wallet_after_creation(instance: User, created: bool, *args: Any, **kwargs: Any) -> None:  # noqa: ARG001, FBT001
    if not created:
        return
    usd_wallet = Wallet(
        coin=Coin.USD,
        user=instance,
        balance=0
    )
    usd_wallet.save()
