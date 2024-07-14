from typing import Any

from sqlalchemy import (
    Column,
    CursorResult,
    DateTime,
    ForeignKey,
    Identity,
    Insert,
    Integer,
    MetaData,
    Select,
    String,
    Table,
    UniqueConstraint,
    Update,
    func,
)
from sqlalchemy.ext.asyncio import AsyncConnection, create_async_engine

from src.config import settings
from src.constants import DB_NAMING_CONVENTION

DATABASE_URL = str(settings.DATABASE_ASYNC_URL)

engine = create_async_engine(
    DATABASE_URL,
    pool_size=settings.DATABASE_POOL_SIZE,
    pool_recycle=settings.DATABASE_POOL_TTL,
    pool_pre_ping=settings.DATABASE_POOL_PRE_PING,
)
metadata = MetaData(naming_convention=DB_NAMING_CONVENTION)

tg_user = Table(
    "tg_user",
    metadata,
    Column("id", Integer, Identity(always=True, start=1, increment=1), primary_key=True),
    Column("telegram_id", String, nullable=False, unique=True),
    Column("chat_id", String, nullable=False),
    Column("username", String),
    Column("first_name", String),
    Column("last_name", String),
    Column("created_at", DateTime, server_default=func.now(), nullable=False),
    Column("updated_at", DateTime, onupdate=func.now()),
    UniqueConstraint("chat_id", "telegram_id", name="tg_user_telegram_id_chat_id_key"),
)

tg_invite_code = Table(
    "tg_invite_code",
    metadata,
    Column("id", Integer, Identity(always=True, start=1, increment=1), primary_key=True),
    Column("referrer_telegram_id", String, nullable=False, unique=True),
    Column("code", String, nullable=False, unique=True),
    Column("created_at", DateTime, server_default=func.now(), nullable=False),
    Column("updated_at", DateTime, onupdate=func.now()),
)

tg_invite = Table(
    "tg_invite",
    metadata,
    Column("id", Integer, Identity(always=True, start=1, increment=1), primary_key=True),
    Column("invite_id", Integer, ForeignKey("tg_invite_code.id"), nullable=False),
    Column("referee_telegram_id", String, nullable=False, unique=True),
    Column("created_at", DateTime, server_default=func.now(), nullable=False),
    Column("updated_at", DateTime, onupdate=func.now()),
)

oauth_twitter = Table(
    "oauth_twitter",
    metadata,
    Column("id", Integer, Identity(always=True, start=1, increment=1), primary_key=True),
    Column("user_tg_id", String, ForeignKey("tg_user.telegram_id"), nullable=True, unique=True),
    Column("oauth_token", String, nullable=False),
    Column("oauth_token_secret", String, nullable=False),
    Column("access_token", String),
    Column("access_token_secret", String),
    Column("twitter_id", String),
    Column("screen_name", String),
    Column("name", String),
    Column("description", String),
    Column("image_url", String),
    Column("created_at", DateTime, server_default=func.now(), nullable=False),
    Column("updated_at", DateTime, onupdate=func.now()),
)

task = Table(
    "task",
    metadata,
    Column("id", Integer, Identity(always=True, start=1, increment=1), primary_key=True),
    Column("name", String, nullable=False, unique=True),
    Column("slug", String, nullable=False, unique=True),
    Column("description", String, nullable=True),
    Column("callback_data", String, nullable=True),
    Column("position_order", Integer, nullable=False),
    Column("points", Integer, nullable=False),
    Column("created_at", DateTime, server_default=func.now(), nullable=False),
    Column("updated_at", DateTime, onupdate=func.now()),
)

task_completion = Table(
    "task_completion",
    metadata,
    Column("id", Integer, Identity(always=True, start=1, increment=1), primary_key=True),
    Column("user_tg_id", String, ForeignKey("tg_user.telegram_id"), nullable=False, unique=True),
    Column("points", Integer, nullable=False),
    Column("task_id", Integer, ForeignKey("task.id"), nullable=False),
    Column("created_at", DateTime, server_default=func.now(), nullable=False),
    Column("updated_at", DateTime, onupdate=func.now()),
    UniqueConstraint("user_tg_id", "task_id", name="points_user_tg_id_task_id_key"),
)


async def fetch_one(
    select_query: Select | Insert | Update,
    connection: AsyncConnection | None = None,
    commit_after: bool = False,
) -> dict[str, Any] | None:
    if not connection:
        async with engine.connect() as connection:
            cursor = await _execute_query(select_query, connection, commit_after)
            return cursor.first()._asdict() if cursor.rowcount > 0 else None

    cursor = await _execute_query(select_query, connection, commit_after)
    return cursor.first()._asdict() if cursor.rowcount > 0 else None


async def fetch_all(
    select_query: Select | Insert | Update,
    connection: AsyncConnection | None = None,
    commit_after: bool = False,
) -> list[dict[str, Any]]:
    if not connection:
        async with engine.connect() as connection:
            cursor = await _execute_query(select_query, connection, commit_after)
            return [r._asdict() for r in cursor.all()]

    cursor = await _execute_query(select_query, connection, commit_after)
    return [r._asdict() for r in cursor.all()]


async def execute(
    query: Insert | Update,
    connection: AsyncConnection = None,
    commit_after: bool = False,
) -> None:
    if not connection:
        async with engine.connect() as connection:
            await _execute_query(query, connection, commit_after)
            return

    await _execute_query(query, connection, commit_after)


async def _execute_query(
    query: Select | Insert | Update,
    connection: AsyncConnection,
    commit_after: bool = False,
) -> CursorResult:
    result = await connection.execute(query)
    if commit_after:
        await connection.commit()

    return result


async def get_db_connection() -> AsyncConnection:
    connection = await engine.connect()
    try:
        yield connection
    finally:
        await connection.close()


async def open_db_connection(autocommit: bool = False) -> AsyncConnection:
    if autocommit:
        return await engine.begin()

    return await engine.connect()
