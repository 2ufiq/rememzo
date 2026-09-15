import hashlib
from datetime import UTC
from uuid import UUID

from fastmcp.exceptions import ToolError
from fastmcp.server.auth import AccessToken, TokenVerifier
from fastmcp.server.dependencies import get_access_token
from sqlalchemy import select

from rememzo.db import SessionFactory
from rememzo.models import APIKey, User
from rememzo.utils import utc_now


class RememzoTokenVerifier(TokenVerifier):
    async def verify_token(self, token: str) -> AccessToken | None:
        if not await is_apikey_valid(token):
            return None

        user_id = await get_user_id_from_apikey(token)
        if user_id is None:
            return None

        return AccessToken(
            token=token,
            client_id="rememzo-api-key",
            scopes=[],
            subject=str(user_id),
        )


def hash_apikey(presented_key: str) -> str:
    return hashlib.sha256(presented_key.encode()).hexdigest()


def is_expired(expired_at) -> bool:
    if expired_at is None:
        return False
    if expired_at.tzinfo is None:
        expired_at = expired_at.replace(tzinfo=UTC)
    return expired_at <= utc_now()


async def is_apikey_valid(presented_key: str) -> bool:
    presented_hash = hash_apikey(presented_key)
    async with SessionFactory() as session:
        api_key = await session.scalar(
            select(APIKey)
            .join(User, User.id == APIKey.user_id)
            .where(
                APIKey.key_hash == presented_hash,
                APIKey.is_active.is_(True),
                User.is_active.is_(True),
            )
        )
        if api_key is None:
            return False
        return not is_expired(api_key.expired_at)


async def get_user_id_from_apikey(presented_key: str) -> UUID | None:
    presented_hash = hash_apikey(presented_key)
    async with SessionFactory() as session:
        api_key = await session.scalar(
            select(APIKey)
            .join(User, User.id == APIKey.user_id)
            .where(
                APIKey.key_hash == presented_hash,
                APIKey.is_active.is_(True),
                User.is_active.is_(True),
            )
        )
        if api_key is None or is_expired(api_key.expired_at):
            return None
        return api_key.user_id


def get_authenticated_user_id() -> UUID:
    access_token = get_access_token()
    if access_token is None or access_token.subject is None:
        raise ToolError("Authenticated user is missing")

    try:
        return UUID(access_token.subject)
    except ValueError as error:
        raise ToolError("Authenticated user ID is invalid") from error
