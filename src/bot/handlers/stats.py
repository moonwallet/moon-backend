import telegram
from sqlalchemy import func, select
from telegram.ext import CallbackContext

from src.bot.config import moon_config
from src.database import fetch_one, tg_user


async def get_admin_stats(update: telegram.Update, context: CallbackContext):
    if update.effective_user.id != moon_config.ADMIN_ID:
        return

    users_count = await count_users()

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"Users count: {users_count['count']}",
    )


async def count_users() -> dict[str, int]:
    select_query = select(func.count(tg_user.c.id).label("count"))
    return await fetch_one(select_query)
