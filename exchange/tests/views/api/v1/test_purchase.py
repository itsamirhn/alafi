from http import HTTPStatus
from typing import Self
from unittest.mock import patch

from django.urls.base import reverse
from model_bakery import baker
from rest_framework.test import APITestCase

from exchange import authentication, models


class TestPurchase(APITestCase):
    @patch("exchange.abc.get_rate_by_usd", lambda _: 2)
    def test_insufficient_balance(self: Self) -> None:
        user = baker.make(models.User, phone_number="09361796325")
        models.Wallet.objects.filter(user=user, coin=models.Coin.USD).update(balance=100)
        token = authentication.Authentication.token_manager.generate(
            authentication.TokenData(
                user_id=user.id,
            ),
        )

        resp = self.client.post(
            path=reverse("purchase-list"),
            data={"coin": "Aban", "amount": 51},
            format="json",
            HTTP_AUTHORIZATION=f"Bearer {token}",
        )

        assert resp.status_code == HTTPStatus.BAD_REQUEST
        assert models.Transaction.objects.count() == 0

    @patch("exchange.abc.get_rate_by_usd", lambda _: 2)
    def test_transactions(self: Self) -> None:
        user = baker.make(models.User, phone_number="09361796325")
        models.Wallet.objects.filter(user=user, coin=models.Coin.USD).update(balance=100)
        token = authentication.Authentication.token_manager.generate(
            authentication.TokenData(
                user_id=user.id,
            ),
        )

        resp = self.client.post(
            path=reverse("purchase-list"),
            data={"coin": "Aban", "amount": 50},
            format="json",
            HTTP_AUTHORIZATION=f"Bearer {token}",
        )

        assert resp.status_code == HTTPStatus.CREATED
        assert (
            models.Transaction.objects.filter(
                wallet__user=user,
                wallet__coin=models.Coin.ABAN,
                amount=50,
                direction=models.Transaction.Direction.DEPOSIT,
                status=models.Transaction.Status.PENDING,
            ).count()
            == 1
        )
        assert (
            models.Transaction.objects.filter(
                wallet__user=user,
                wallet__coin=models.Coin.USD,
                amount=100,
                direction=models.Transaction.Direction.WITHDRAW,
                status=models.Transaction.Status.SETTLED,
            ).count()
            == 1
        )
        assert models.Wallet.objects.get(user=user, coin=models.Coin.USD).balance == 0
        assert models.Wallet.objects.get(user=user, coin=models.Coin.ABAN).balance == 50  # noqa: PLR2004
