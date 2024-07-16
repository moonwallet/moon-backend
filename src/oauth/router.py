from typing import Any

from fastapi import APIRouter, Depends
from fastapi.responses import RedirectResponse

from src import twitter
from src.oauth import service
from src.oauth.config import oauth_settings
from src.oauth.dependencies import valid_oauth_token
from src.points import handler as points_handler

router = APIRouter()


@router.get("/twitter/callback")
async def twitter_callback(
    oauth_verifier: str,
    oauth_data: dict[str, Any] = Depends(valid_oauth_token),
):
    access_token, access_token_secret = await twitter.get_tokens_with_verifier(oauth_data, oauth_verifier)
    await service.setup_oauth_access_tokens(
        oauth_data["oauth_token"],
        access_token,
        access_token_secret,
    )

    user_profile = await twitter.get_user_info(access_token, access_token_secret)
    await service.setup_user_twitter_profile(oauth_data["oauth_token"], user_profile)

    await points_handler.user_x_connected(oauth_data["user_tg_id"])

    return RedirectResponse(url=oauth_settings.OAUTH_TWITTER_REDIRECT_URI)
