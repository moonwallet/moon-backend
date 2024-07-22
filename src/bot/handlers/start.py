import asyncio

import telegram
from telegram.ext import CallbackContext

from src.bot import service, utils
from src.bot.config import moon_config
from src.database import open_db_connection


async def command_start(update: telegram.Update, context: CallbackContext):
    if update.effective_chat.id in moon_config.NOTIFICATIONS_CHAT_IDS:
        return

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
        parse_mode=telegram.constants.ParseMode.MARKDOWN_V2,
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
    if username := update.effective_user.username:
        inviter_username = f"@{username}"
    else:
        inviter_username = "anon"

    inviter_username = inviter_username.replace("_", "\\_")

    base_text = f"*New user created:* {inviter_username}\n"
    if creation_data["used_invite"]:
        if creation_data.get("invited_by"):
            base_text += f"\n\\-*Invited by:* {creation_data['invited_by']}"
            if creation_data.get("total_invites"):
                base_text += f"\n\\-*Total invitees:* {creation_data['total_invites']}"

            base_text += f"\n\\-*Total inviter points:* {creation_data['inviter_points']}"

    for chat_id, topic_id in zip(moon_config.NOTIFICATIONS_CHAT_IDS, moon_config.NOTIFICATIONS_CHAT_TOPIC_IDS):
        await context.bot.send_message(
            chat_id=chat_id,
            reply_to_message_id=topic_id,
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
