from dataclasses import asdict, dataclass
from datetime import timedelta
from typing import Self

import jwt
from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext as _
from rest_framework import authentication, exceptions, request
from rest_framework.generics import get_object_or_404

from exchange import models


class TokenError(Exception):
    pass


class ExpiredTokenError(TokenError):
    def __init__(self: Self) -> None:
        super().__init__("token expired")


class InvalidTokenError(TokenError):
    def __init__(self: Self) -> None:
        super().__init__("invalid token")


@dataclass
class TokenData:
    user_id: int


class TokenManager:
    def __init__(self: Self, key: str, ttl: timedelta) -> None:
        self.key = key
        self.ttl = ttl

    def generate(self: Self, data: TokenData) -> str:
        payload = asdict(data)
        now = timezone.now()
        payload["iat"] = int(now.timestamp())
        payload["exp"] = int((now + self.ttl).timestamp())
        return jwt.encode(payload, self.key, algorithm="HS256")

    def validate(self: Self, token: str) -> TokenData:
        try:
            payload = jwt.decode(token, self.key, algorithms=["HS256"])
        except jwt.ExpiredSignatureError as exc:
            raise ExpiredTokenError from exc
        except jwt.InvalidTokenError as exc:
            raise InvalidTokenError from exc
        payload.pop("iat")
        payload.pop("exp")
        return TokenData(**payload)


@dataclass
class AuthData:
    user: models.User


class APIRequest(request.Request):
    auth: AuthData


class Authentication(authentication.BaseAuthentication):
    TOKEN_PREFIX = "Bearer "  # noqa: S105
    token_manager = TokenManager(settings.AUTHENTICATION.key, settings.AUTHENTICATION.ttl)

    def authenticate(self: Self, req: request.Request) -> tuple[models.User, AuthData]:
        try:
            token = req.META.get("HTTP_AUTHORIZATION")
            if not token:
                raise exceptions.AuthenticationFailed(_("Token is missing."))

            if not token.lower().startswith(self.TOKEN_PREFIX.lower()):
                raise exceptions.AuthenticationFailed(_("Invalid token."))

            data = self.token_manager.validate(token[len(self.TOKEN_PREFIX) :])
        except InvalidTokenError as exc:
            raise exceptions.AuthenticationFailed(_("Invalid token.")) from exc
        except ExpiredTokenError as exc:
            raise exceptions.AuthenticationFailed(_("Expired token.")) from exc
        else:
            user = get_object_or_404(models.User, id=data.user_id)
            auth = AuthData(user=user)
            return user, auth

    def authenticate_header(self: Self, _: request.Request) -> str:
        return self.TOKEN_PREFIX
