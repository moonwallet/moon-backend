from typing import Any

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncConnection

from src.database import execute, fetch_one, oauth_twitter
from src.oauth.schemas import TwitterOauth1TokenData, TwitterProfile


async def init_oauth_twitter(user_id: str, data: TwitterOauth1TokenData) -> None:
    insert_query = (
        insert(oauth_twitter)
        .values(
            user_tg_id=user_id,
            oauth_token=data.oauth_token,
            oauth_token_secret=data.oauth_token_secret,
        )
        .on_conflict_do_update(
            index_elements=["user_tg_id"],
            set_={
                "oauth_token": data.oauth_token,
                "oauth_token_secret": data.oauth_token_secret,
                "access_token": None,
                "access_token_secret": None,
            },
        )
    )

    await execute(insert_query, commit_after=True)


async def get_oauth_by_id(oauth_twitter_id: int, db_connection: AsyncConnection) -> dict[str, Any]:
    select_query = oauth_twitter.select().where(oauth_twitter.c.id == oauth_twitter_id)

    return await fetch_one(select_query, db_connection)


async def get_oauth_by_token(oauth_token: str) -> dict[str, Any]:
    select_query = oauth_twitter.select().where(oauth_twitter.c.oauth_token == oauth_token)

    return await fetch_one(select_query)


async def get_oauth_by_user_id(user_tg_id: str) -> dict[str, Any]:
    select_query = oauth_twitter.select().where(oauth_twitter.c.user_tg_id == user_tg_id)

    return await fetch_one(select_query)


async def setup_oauth_access_tokens(
    oauth_token: str,
    access_token: str,
    access_token_secret: str,
) -> None:
    update_query = (
        oauth_twitter.update()
        .where(oauth_twitter.c.oauth_token == oauth_token)
        .values(
            access_token=access_token,
            access_token_secret=access_token_secret,
        )
    )

    await execute(update_query, commit_after=True)


async def setup_user_twitter_profile(oauth_token: str, profile: TwitterProfile):
    upsert_query = (
        oauth_twitter.update()
        .values(**profile.model_dump(exclude_none=True))
        .where(oauth_twitter.c.oauth_token == oauth_token)
    )

    await execute(upsert_query, commit_after=True)
