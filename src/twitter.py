from datetime import timedelta
from typing import Any

import orjson
import tweepy
from fastapi.concurrency import run_in_threadpool
from pydantic_settings import SettingsConfigDict
from tweepy.asynchronous import AsyncClient as TwitterClient

from src import redis
from src.config import CustomBaseSettings
from src.oauth.schemas import TwitterOauth1TokenData, TwitterProfile
from src.redis import RedisData

BASE_URL = "https://api.twitter.com"


class TwitterConfigs(CustomBaseSettings):
    model_config = SettingsConfigDict(env_prefix="TWITTER_")

    CONSUMER_KEY: str
    CONSUMER_SECRET: str
    REDIRECT_URL: str = "http://127.0.0.1:8000/twitter/callback"


twitter_settings = TwitterConfigs()


async def get_authorization_data() -> TwitterOauth1TokenData:
    auth = tweepy.OAuth1UserHandler(
        twitter_settings.CONSUMER_KEY,
        twitter_settings.CONSUMER_SECRET,
        callback=twitter_settings.REDIRECT_URL,
    )

    redirect_uri = await run_in_threadpool(auth.get_authorization_url)

    return TwitterOauth1TokenData(
        oauth_token=auth.request_token["oauth_token"],
        oauth_token_secret=auth.request_token["oauth_token_secret"],
        redirect_uri=redirect_uri,
    )


async def get_tokens_with_verifier(oauth_data: dict[str, Any], verifier: str) -> tuple[str, str]:
    auth = tweepy.OAuth1UserHandler(
        twitter_settings.CONSUMER_KEY,
        twitter_settings.CONSUMER_SECRET,
        callback=twitter_settings.REDIRECT_URL,
    )
    auth.request_token = {
        "oauth_token": oauth_data["oauth_token"],
        "oauth_token_secret": oauth_data["oauth_token_secret"],
    }

    return await run_in_threadpool(auth.get_access_token, verifier)


async def get_user_info(
    access_token: str,
    access_token_secret: str,
    raise_on_error: bool = True,
) -> TwitterProfile | None:
    user_info_key = f"twitter:access_token:{access_token}"
    if user_info := await redis.get_by_key(user_info_key):
        return TwitterProfile.model_validate_json(user_info)

    auth = tweepy.OAuth1UserHandler(
        twitter_settings.CONSUMER_KEY,
        twitter_settings.CONSUMER_SECRET,
        access_token=access_token,
        access_token_secret=access_token_secret,
    )

    client = tweepy.API(auth)
    try:
        user = await run_in_threadpool(client.verify_credentials, include_entities=False, skip_status=True)
    except tweepy.TweepyException as e:
        if raise_on_error:
            raise e

        return None

    await redis.set_redis_key(
        RedisData(
            key=user_info_key,
            value=orjson.dumps(
                {
                    "twitter_id": user.id_str,
                    "screen_name": user.screen_name,
                    "name": user.name,
                    "description": user.description,
                    "profile_image_url": user.profile_image_url_https,
                }
            ),
            ttl=timedelta(hours=1),
        )
    )

    return TwitterProfile(
        twitter_id=user.id_str,
        screen_name=user.screen_name,
        name=user.name,
        description=user.description,
        profile_image_url=user.profile_image_url_https,
    )


async def tweet(oauth_data: dict[str, Any], message: str) -> dict[str, str]:
    client = TwitterClient(
        consumer_key=twitter_settings.CONSUMER_KEY,
        consumer_secret=twitter_settings.CONSUMER_SECRET,
        access_token=oauth_data["access_token"],
        access_token_secret=oauth_data["access_token_secret"],
    )

    response = await client.create_tweet(text=message)
    return response.data
