from typing import Any

from fastapi import APIRouter, BackgroundTasks, Depends
from pydantic import HttpUrl

from src import twitter
from src.dependencies import parse_request_data
from src.oauth import service
from src.oauth.dependencies import valid_oauth_token
from src.oauth.schemas import OauthRedirectUri
from src.schemas import RequestData

router = APIRouter()


@router.get("/twitter/redirect_url", response_model=OauthRedirectUri)
async def twitter_redirect_uri() -> dict[str, HttpUrl]:
    auth_data = await twitter.get_authorization_data()

    user_id = None
    await service.init_oauth_twitter(user_id, auth_data)

    return {
        "redirect_uri": auth_data.redirect_uri,
    }


@router.get("/twitter/callback")
async def twitter_callback(
    oauth_verifier: str,
    worker: BackgroundTasks,
    request_data: RequestData = Depends(parse_request_data),
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


# @router.get("/twitter/me", response_model=TwitterMeOauth)
# async def verify_user_connected(
#     oauth_data: dict[str, Any] = Depends(valid_user_with_oauth),
# ) -> TwitterMeOauth:
#     user_profile = await twitter.get_user_info(
#         oauth_data["access_token"], oauth_data["access_token_secret"], raise_on_error=False
#     )
#
#     return TwitterMeOauth(
#         is_connected=user_profile is not None,
#     )
