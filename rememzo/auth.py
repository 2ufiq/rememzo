from uuid import UUID
import hashlib

from fastmcp.exceptions import ToolError
from fastmcp.server.auth import AccessToken, TokenVerifier
from fastmcp.server.dependencies import get_access_token
from sqlalchemy import select

from rememzo.db import SessionFactory
from rememzo.models import APIKey


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


async def is_apikey_valid(presented_key: str):
    presented_hash = hashlib.sha256(presented_key.encode()).hexdigest()
    async with SessionFactory() as session:
        api_key = await session.scalar(
            select(APIKey).where(APIKey.key_hash == presented_hash)
        )
        if not api_key or not api_key.is_active:
            return False
        if api_key.expired_at:
            expired_at = api_key.expired_at
            if expired_at.tzinfo is None:
                expired_at = expired_at.replace(tzinfo=UTC)
            if expired_at <= utc_now():
                return False
        return True


async def get_user_id_from_apikey(presented_key: str) -> UUID | None:
    presented_hash = hashlib.sha256(presented_key.encode()).hexdigest()
    async with SessionFactory() as session:
        return await session.scalar(
            select(APIKey.user_id).where(APIKey.key_hash == presented_hash)
        )

def get_authenticated_user_id() -> UUID:
    access_token = get_access_token()
    if access_token is None or access_token.subject is None:
        raise ToolError("Authenticated user is missing")

    try:
        return UUID(access_token.subject)
    except ValueError as error:
        raise ToolError("Authenticated user ID is invalid") from error
