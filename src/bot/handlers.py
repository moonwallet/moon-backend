import asyncio
import logging

import sentry_sdk
import telegram
from telegram.ext import CallbackContext

from src.bot import service, utils
from src.bot.config import moon_config
from src.config import settings
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

    if query.data == "referrals_explanation":
        await send_referrals_explanation(update, context)

    if query.data == "demo_show":
        await send_demo_video(update, context)

    if query.data == "moon_safety":
        await send_moon_safety_info(update, context)

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
        photo=moon_config.REFERRALS_PREVIEW_IMAGE_URL,
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


async def send_referrals_explanation(update: telegram.Update, context: CallbackContext) -> None:
    user_invite = await service.get_invite_with_count(referrer_telegram_id=str(update.effective_user.id))
    invite_link = utils.prepare_invite_link(user_invite["code"])

    await context.bot.send_video(
        chat_id=update.effective_chat.id,
        video=moon_config.REFERRAL_EXPLANATION_VIDEO_URL,
        caption=(
            "Here is a quick video from Dima explaining how the referral system works\\."
            f"\n\n*Copy and share your referral link*: `{invite_link}`"
        ),
        reply_markup=utils.prepare_referrals_explanation_buttons(invite_link),
        parse_mode=telegram.constants.ParseMode.MARKDOWN_V2,
    )


async def send_demo_video(update: telegram.Update, context: CallbackContext) -> None:
    await context.bot.send_video(
        chat_id=update.effective_chat.id,
        video=moon_config.DEMO_VIDEO_URL,
        caption="🔥 Check out the video by Dima, where he showcases the product we're building.",
        reply_markup=utils.prepare_send_demo_buttons(),
    )


async def send_moon_safety_info(update: telegram.Update, context: CallbackContext) -> None:
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=utils.prepare_safety_info_text(),
        reply_markup=utils.prepare_safety_info_buttons(),
        parse_mode=telegram.constants.ParseMode.MARKDOWN_V2,
        disable_web_page_preview=True,
    )


async def echo_videos(update: telegram.Update, context: CallbackContext) -> None:
    if update.effective_user.id != moon_config.ADMIN_ID:
        return

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"Video `{update.message.video.file_id}` received",
        parse_mode=telegram.constants.ParseMode.MARKDOWN_V2,
    )


async def echo_messages(update: telegram.Update, context: CallbackContext) -> None:
    print(update.message.text)
    print(update.message.chat_id)
    print(update.message.message_thread_id)


async def send_error_message(update: telegram.Update, context: CallbackContext) -> None:
    if settings.ENVIRONMENT.is_deployed:
        sentry_sdk.capture_exception(context.error)
    else:
        logger.exception(context.error)

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        reply_to_message_id=update.effective_message.message_id,
        text=(
            f"Sorry, something went wrong. "
            f"Please retry after some time or contact the developers in the chat: {moon_config.SUPPORT_CHAT_LINK}"
        ),
    )


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
