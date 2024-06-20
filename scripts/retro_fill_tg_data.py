import asyncio
import logging

from sqlalchemy.ext.asyncio import AsyncConnection
from telegram.error import TelegramError

from src.bot.app import moon_app
from src.database import execute, fetch_all, open_db_connection, tg_user

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


async def get_all_users(db_connection: AsyncConnection):
    return await fetch_all(tg_user.select(), db_connection)


async def update_user_data(user_id: int, data: dict[str, str], db_connection: AsyncConnection):
    update_query = tg_user.update().where(tg_user.c.id == user_id).values(**data)

    await execute(update_query, db_connection, commit_after=True)


async def main():
    db_connection = await open_db_connection()
    try:
        for user in await get_all_users(db_connection):
            try:
                user_profile = await moon_app.bot.get_chat(user["telegram_id"])
            except TelegramError:
                logger.exception(f"Failed to get user profile for user {user['id']}")
                continue

            logger.info(f"Updating user {user_profile.username} data")
            await update_user_data(
                user["id"],
                {
                    "username": user_profile.username,
                    "first_name": user_profile.first_name,
                    "last_name": user_profile.last_name,
                }, db_connection
            )

            await asyncio.sleep(0.2)
    finally:
        await db_connection.close()


if __name__ == '__main__':
    asyncio.run(main())
