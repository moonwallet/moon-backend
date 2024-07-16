import telegram

from src.bot.app import moon_app
from src.bot.handlers import constants as handlers_constants
from src.points import service as points_service
from src.points.config import points_settings


async def user_x_connected(user_id: str):
    x_connected_task = await points_service.get_task_by_slug(points_settings.X_CONNECTED_TASK_SLUG)
    if not x_connected_task:
        raise ValueError(f"Task with slug {points_settings.X_CONNECTED_TASK_SLUG} not found")

    await points_service.complete_task(user_id, x_connected_task["id"], x_connected_task["points"])

    await _send_twitter_connected_successfully(user_id)


async def _send_twitter_connected_successfully(user_tg_id: str):
    tasks_buttons = [
        [telegram.InlineKeyboardButton("Go Back", callback_data=handlers_constants.MESSAGE_DELETE)],
    ]

    await moon_app.bot.send_message(
        chat_id=user_tg_id,
        text="Awesome! Your Twitter account is now connected to Moon Wallet ✅",
        reply_markup=telegram.InlineKeyboardMarkup(tasks_buttons),
    )
