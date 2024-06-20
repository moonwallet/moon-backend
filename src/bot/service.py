from typing import Any

from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncConnection

from src.bot.schemas import TgUserCreate
from src.database import execute, fetch_one, tg_invite, tg_invite_code, tg_user
from src.utils import generate_random_alphanum


async def get_invite(
    *,
    referrer_telegram_id: str = None,
    code: str = None,
    db_connection: AsyncConnection = None,
):
    filters = []
    if referrer_telegram_id:
        filters.append(tg_invite_code.c.referrer_telegram_id == referrer_telegram_id)
    elif code:
        filters.append(tg_invite_code.c.code == code)

    select_query = select(tg_invite_code).where(*filters)

    return await fetch_one(select_query, db_connection)


async def create_user_invite(
    telegram_id: str,
    db_connection: AsyncConnection,
):
    insert_query = (
        insert(tg_invite_code)
        .values(referrer_telegram_id=telegram_id, code=generate_random_alphanum(8))
        .returning(tg_invite_code)
        .on_conflict_do_nothing(index_elements=[tg_invite_code.c.referrer_telegram_id])
    )

    return await fetch_one(insert_query, db_connection, commit_after=True)


async def get_invited_user(
    invited_telegram_id: str,
    db_connection: AsyncConnection,
):
    select_query = select(tg_invite).where(tg_invite.c.referee_telegram_id == invited_telegram_id)

    return await fetch_one(select_query, db_connection)


async def invite_user(invite_code_id: int, invited_telegram: str, db_connection: AsyncConnection):
    insert_query = (
        insert(tg_invite)
        .values(invite_id=invite_code_id, referee_telegram_id=invited_telegram)
        .on_conflict_do_nothing(index_elements=[tg_invite.c.referee_telegram_id])
        .returning(tg_invite)
    )

    return await fetch_one(insert_query, db_connection, commit_after=True)


async def count_invited_users(
    referrer_telegram_id: str,
    db_connection: AsyncConnection,
) -> int:
    select_query = select(func.count(tg_invite.c.id).label("count")).where(
        tg_invite.c.referrer_telegram_id == referrer_telegram_id
    )

    invites_count = await fetch_one(select_query, db_connection)

    return invites_count["count"]


async def get_invite_with_count(
    *,
    code: str = None,
    referrer_telegram_id: str = None,
    db_connection: AsyncConnection = None,
) -> dict[str, Any] | None:
    filters = []
    if code:
        filters.append(tg_invite_code.c.code == code)
    if referrer_telegram_id:
        filters.append(tg_invite_code.c.referrer_telegram_id == referrer_telegram_id)

    select_query = (
        select(
            tg_invite_code.c.id,
            tg_invite_code.c.code,
            tg_invite_code.c.referrer_telegram_id,
            func.count(tg_invite.c.id).label("count"),
        )
        .select_from(tg_invite_code.outerjoin(tg_invite, tg_invite_code.c.id == tg_invite.c.invite_id))
        .where(*filters)
        .group_by(tg_invite_code.c.code, tg_invite_code.c.id, tg_invite_code.c.referrer_telegram_id)
    )

    return await fetch_one(select_query, db_connection)


async def get_telegram_user_by_id(
    telegram_id: str,
    db_connection: AsyncConnection,
):
    select_query = select(tg_user).where(tg_user.c.telegram_id == telegram_id)

    return await fetch_one(select_query, db_connection)


async def insert_telegram_user(
    user_data: TgUserCreate,
    db_connection: AsyncConnection = None,
):
    insert_query = insert(tg_user).values(user_data.model_dump())

    return await execute(insert_query, db_connection, commit_after=False)


async def update_telegram_user(
    telegram_id: str,
    data: dict[str, Any],
    db_connection: AsyncConnection = None,
):
    update_query = tg_user.update().where(tg_user.c.telegram_id == telegram_id).values(data)

    return await execute(update_query, db_connection, commit_after=True)
