from typing import Union
from uuid import UUID

from rest_framework_simplejwt.tokens import UntypedToken
from recuperari.utils import generate_token_generic, validate_token_generic
from lsc_recuperari import settings


class AuthService:
    @staticmethod
    def generate_reset_password_link_token(user_pk: Union[UUID, str]) -> UntypedToken:
        return generate_token_generic(
            settings.RESET_PASSWORD_LINK_JWT_LIFETIME_SEC, user_pk=str(user_pk)
        )

    @staticmethod
    def validate_reset_password_link_token(token: str) -> dict:
        return validate_token_generic(
            token, settings.RESET_PASSWORD_LINK_TOKEN_KEY, "Query string", "user_pk"
        )

    @staticmethod
    def generate_reset_password_token(user_pk: Union[UUID, str]) -> UntypedToken:
        return generate_token_generic(
            settings.RESET_PASSWORD_JWT_LIFETIME_SEC, user_pk=str(user_pk)
        )

    @staticmethod
    def validate_reset_password_token(token: str) -> dict:
        return validate_token_generic(
            token,
            settings.RESET_PASSWORD_TOKEN_KEY,
            "Cookie or query string",
            "user_pk",
        )
