import asyncio
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

    if created:
        asyncio.create_task(notify_devs(created, update, context))

    await context.bot.send_video(
        chat_id=update.effective_chat.id,
        video=moon_config.START_VIDEO_URL,
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
    user_invite = await service.get_invite_with_count(referrer_telegram_id=str(update.effective_user.id))
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
    user_invite = await service.get_invite_with_count(referrer_telegram_id=str(update.effective_user.id))
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


async def notify_devs(creation_data: dict[str, bool], update: telegram.Update, context: CallbackContext):
    base_text = f"*New user created:* @{update.effective_user.username}\n"
    if creation_data["used_invite"]:
        if creation_data.get("invited_by"):
            base_text += f"\n\\-*Invited by:* {creation_data['invited_by']}"
            if creation_data.get("total_invites"):
                base_text += f"\n\\-*Total invitees:* {creation_data['total_invites']}"
        if creation_data.get("self_invite"):
            base_text += "\n\\- Tried to self\\-invite"
        elif creation_data.get("invalid_invite"):
            base_text += f"\n\\- Invalid invite code: {creation_data.get('invite_code')}"

    await context.bot.send_message(
        chat_id=moon_config.NOTIFICATIONS_CHAT_ID,
        reply_to_message_id=moon_config.NOTIFICATIONS_CHAT_TOPIC_ID,
        parse_mode=telegram.constants.ParseMode.MARKDOWN_V2,
        text=base_text,
    )


async def echo_videos(update: telegram.Update, context: CallbackContext) -> None:
    print(update.message.video.file_id)
    print(update.message.video.file_unique_id)


async def echo_messages(update: telegram.Update, context: CallbackContext) -> None:
    print(update.message.text)
    print(update.message.chat_id)
    print(update.message.message_thread_id)
