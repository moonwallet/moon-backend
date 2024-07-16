import logging

import sentry_sdk
import telegram
from telegram.ext import CallbackContext

from src.bot.config import moon_config
from src.config import settings

logger = logging.getLogger(__name__)


async def echo_videos(update: telegram.Update, context: CallbackContext) -> None:
    if update.effective_user.id != moon_config.ADMIN_ID:
        return

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"Video `{update.message.video.file_id}` received",
        parse_mode=telegram.constants.ParseMode.MARKDOWN_V2,
    )


async def echo_image(update: telegram.Update, context: CallbackContext) -> None:
    if update.effective_user.id != moon_config.ADMIN_ID:
        return

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"Photo `{update.message}` received",
    )


async def send_error_message(update: telegram.Update, context: CallbackContext) -> None:
    if settings.ENVIRONMENT.is_deployed:
        sentry_sdk.capture_exception(context.error)
    else:
        logger.exception(context.error)

    if "Message is not modified" in str(context.error):
        return

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        reply_to_message_id=update.effective_message.message_id,
        text=(
            f"Sorry, something went wrong. "
            f"Please retry after some time or contact the developers in the chat: {moon_config.SUPPORT_CHAT_LINK}"
        ),
    )
