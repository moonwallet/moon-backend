import asyncio

import telegram
from telegram.ext import CallbackContext

from src.bot import service, utils
from src.bot.config import moon_config
from src.database import open_db_connection


async def command_start(update: telegram.Update, context: CallbackContext):
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


async def send_demo_video(update: telegram.Update, context: CallbackContext) -> None:
    await context.bot.send_video(
        chat_id=update.effective_chat.id,
        video=moon_config.DEMO_VIDEO_URL,
        caption="🔥 Check out the video by Dima, where he showcases the product we're building.",
        reply_markup=utils.prepare_send_demo_buttons(),
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


async def send_moon_safety_info(update: telegram.Update, context: CallbackContext) -> None:
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=utils.prepare_safety_info_text(),
        reply_markup=utils.prepare_safety_info_buttons(),
        parse_mode=telegram.constants.ParseMode.MARKDOWN_V2,
        disable_web_page_preview=True,
    )
