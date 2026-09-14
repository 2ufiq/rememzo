from uuid import UUID

from fastmcp.exceptions import ToolError
from fastmcp.server.auth import AccessToken, TokenVerifier
from fastmcp.server.dependencies import get_access_token

from rememzo import services


class RememzoTokenVerifier(TokenVerifier):
    async def verify_token(self, token: str) -> AccessToken | None:
        if not await services.is_apikey_valid(token):
            return None

        user_id = await services.get_user_id_from_apikey(token)
        if user_id is None:
            return None

        return AccessToken(
            token=token,
            client_id="rememzo-api-key",
            scopes=[],
            subject=str(user_id),
        )


def get_authenticated_user_id() -> UUID:
    access_token = get_access_token()
    if access_token is None or access_token.subject is None:
        raise ToolError("Authenticated user is missing")

    try:
        return UUID(access_token.subject)
    except ValueError as error:
        raise ToolError("Authenticated user ID is invalid") from error
