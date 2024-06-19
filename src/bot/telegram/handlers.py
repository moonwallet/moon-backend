import logging

import telegram
from telegram.ext import CallbackContext

from src.bot import service
from src.bot.config import moon_config
from src.bot.telegram import utils
from src.database import open_db_connection

logger = logging.getLogger(__name__)


async def start(update: telegram.Update, context: CallbackContext):
    db_connection = await open_db_connection()
    try:
        created = await utils.register_user(db_connection, update, context)
    finally:
        await db_connection.close()

    await context.bot.send_video(
        chat_id=update.effective_chat.id,
        video=moon_config.MOON_START_VIDEO_URL,
        caption=utils.prepare_start_text(),
        reply_markup=utils.prepare_start_buttons(),
    )


async def query_buttons(update: telegram.Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()

    if query.data == "refresh_stat":
        await refresh_user_stats(query, update)

    if query.data == "get_referrals":
        await get_referrals(update, context)

    if query.data == "delete_message":
        await context.bot.delete_message(chat_id=query.message.chat_id, message_id=query.message.message_id)

    if moon_config.UPDATE_USER_DATA_ON_INTERACTION:
        await service.update_telegram_user(
            telegram_id=str(update.effective_user.id),
            data={
                "username": update.effective_user.username,
                "first_name": update.effective_user.first_name,
                "last_name": update.effective_user.last_name,
            },
        )


async def get_referrals(update: telegram.Update, context: CallbackContext) -> None:
    user_invite = await service.get_invite_with_count(str(update.effective_user.id))
    invite_link = utils.prepare_invite_link(user_invite["code"])
    text = utils.prepare_referrals_stat_text(user_invite["count"], invite_link)

    await context.bot.send_photo(
        chat_id=update.effective_chat.id,
        photo="https://cdn.dappsheriff.com/misc/moon_preview.png",
        reply_markup=utils.prepare_referrals_buttons(invite_link),
        parse_mode=telegram.constants.ParseMode.MARKDOWN_V2,
        caption=text,
    )


async def refresh_user_stats(query: telegram.CallbackQuery, update: telegram.Update):
    user_invite = await service.get_invite_with_count(str(update.effective_user.id))
    invite_link = utils.prepare_invite_link(user_invite["code"])
    text = utils.prepare_referrals_stat_text(user_invite["count"], invite_link)
    try:
        await query.edit_message_caption(
            caption=text,
            reply_markup=query.message.reply_markup,
            parse_mode=telegram.constants.ParseMode.MARKDOWN_V2,
        )
    except telegram.error.BadRequest as exc:
        if "Message is not modified" not in str(exc):
            raise


async def echo_videos(update: telegram.Update, context: CallbackContext) -> None:
    print(update.message.video.file_id)
    print(update.message.video.file_unique_id)
