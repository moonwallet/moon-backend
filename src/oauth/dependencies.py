from typing import Any

from src.oauth import service
from src.oauth.exceptions import OauthTokenNotFound


async def valid_oauth_token(oauth_token: str) -> dict[str, Any]:
    oauth_data = await service.get_oauth_by_token(oauth_token)
    if not oauth_data:
        raise OauthTokenNotFound()

    return oauth_data
