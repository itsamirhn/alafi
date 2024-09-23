import time
from datetime import timedelta
from typing import Self

import pytest
from django.test import TestCase
from model_bakery import baker
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.test import APIRequestFactory, APITestCase

from exchange import authentication, models


class TestTokenManager(TestCase):
    def test_correct(self: Self) -> None:
        manager = authentication.TokenManager("secret", timedelta(seconds=20))
        data = authentication.TokenData(user_id=1234)

        token = manager.generate(data)
        validated_data = manager.validate(token)

        assert data == validated_data

    def test_wrong(self: Self) -> None:
        manager = authentication.TokenManager("secret", timedelta(seconds=20))
        data = authentication.TokenData(user_id=1234)

        token = manager.generate(data)
        with pytest.raises(authentication.InvalidTokenError):
            manager.validate(token + "noise")

    def test_expired(self: Self) -> None:
        manager = authentication.TokenManager("secret", timedelta(seconds=1))
        data = authentication.TokenData(user_id=1234)

        token = manager.generate(data)
        time.sleep(1)
        with pytest.raises(authentication.ExpiredTokenError):
            manager.validate(token)


class TestAuthentication(APITestCase):
    def test_correct_token(self: Self) -> None:
        user = baker.make(models.User, phone_number="09123456789")
        auth = authentication.Authentication()
        token = auth.token_manager.generate(authentication.TokenData(user_id=user.id))
        request_factory = APIRequestFactory()
        req = request_factory.get("/", content_type="application/json", HTTP_AUTHORIZATION=auth.TOKEN_PREFIX + token)

        ret = auth.authenticate(req)

        assert ret == (user, authentication.AuthData(user))

    def test_wrong_token(self: Self) -> None:
        auth = authentication.Authentication()
        request_factory = APIRequestFactory()
        req = request_factory.get("/", content_type="application/json", HTTP_AUTHORIZATION=auth.TOKEN_PREFIX + "token")

        with pytest.raises(AuthenticationFailed):
            auth.authenticate(req)

    def test_no_token(self: Self) -> None:
        auth = authentication.Authentication()
        req = APIRequestFactory().get("/", content_type="application/json")

        with pytest.raises(AuthenticationFailed):
            auth.authenticate(req)
