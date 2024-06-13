import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext

from src.bot import service
from src.bot.config import moon_config
from src.database import open_db_connection


async def start(update: telegram.Update, context: CallbackContext):
    user_id = str(update.effective_user.id)
    created = True

    db_connection = await open_db_connection()
    try:
        user_invite = await service.create_user_invite(user_id, db_connection)
        if not user_invite:  # already exists
            created = False
            user_invite = await service.get_invite_with_count(user_id, db_connection=db_connection)

        if created and context.args:
            invite_code = context.args[0]
            if user_invite["code"] != invite_code:  # not self-invite
                if invite := await service.get_invite(code=invite_code, db_connection=db_connection):
                    await service.invite_user(invite["id"], user_id, db_connection)
    finally:
        await db_connection.close()

    text = (
        "Welcome to Moon - Telegram wallet for Solana memecoins.\n\n"
        "We are going live in July. Meanwhile, "
        "join our Telegram group for the latest updates "
        "and the warmest memecoin fam 😍.\n\n"
        "P.S. Invite your friends to get an exclusive 50% revenue share! "
        "(offer is only available at the pre-launch stage"
    )

    buttons = [
        [InlineKeyboardButton("Join Telegram Сommunity", url="https://t.me/moon_wallet_xyz")],
        [InlineKeyboardButton("Follow us on X", url="https://x.com/moon_wallet_xyz")],
        [
            InlineKeyboardButton(
                "🎁 Invite friends - get 50% from their fees",
                callback_data="get_referrals",
            )
        ],
    ]
    reply_markup = InlineKeyboardMarkup(buttons)

    await context.bot.send_video(
        chat_id=update.effective_chat.id,
        video=moon_config.MOON_START_VIDEO_URL,
        caption=text,
        reply_markup=reply_markup,
    )


async def get_referrals(update: telegram.Update, context: CallbackContext) -> None:
    user_id = str(update.effective_user.id)
    referrals_count = 0
    created = True
    db_connection = await open_db_connection()
    try:
        user_invite = await service.create_user_invite(user_id, db_connection)
        if not user_invite:  # already exists
            created = False
            user_invite = await service.get_invite_with_count(user_id, db_connection=db_connection)
            referrals_count = user_invite["count"]

        if created and context.args:
            invite_code = context.args[0]
            if user_invite["code"] != invite_code:  # not self-invite
                if invite := await service.get_invite(code=invite_code, db_connection=db_connection):
                    await service.invite_user(invite["id"], user_id, db_connection)
    finally:
        await db_connection.close()

    invite_link = f"https://t.me/{moon_config.MOON_BOT_USERNAME}?start={user_invite['code']}"
    chat_id = update.effective_chat.id

    text = (
        f"*Your referral link:* `{invite_link}`\n"
        f"*Your referrals:* {referrals_count}\n\n"
        "Refer your friends and earn 50% of their fees\\. \n"
        "Help Moon to build the community and start receiving rewards once we launch in July\\."
    )
    buttons = [
        [
            InlineKeyboardButton(
                "Share my Ref",
                switch_inline_query=(
                    "\nJoin Moon community and get early access "
                    f"to a Telegram Wallet for Solana Memecoins: {invite_link}"
                ),
            )
        ],
        [InlineKeyboardButton("Refresh statistics", callback_data="refresh_stat")],
        [InlineKeyboardButton("Go Back", callback_data="delete_message")],
    ]

    reply_markup = InlineKeyboardMarkup(buttons)
    await context.bot.send_photo(
        chat_id=chat_id,
        photo="https://cdn.dappsheriff.com/misc/moon_preview.png",
        reply_markup=reply_markup,
        parse_mode=telegram.constants.ParseMode.MARKDOWN_V2,
        caption=text,
    )


async def query_buttons(update: telegram.Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()

    if query.data == "refresh_stat":
        user_id = str(update.effective_user.id)
        db_connection = await open_db_connection()
        try:
            user_invite = await service.get_invite_with_count(user_id, db_connection=db_connection)
        finally:
            await db_connection.close()

        invite_link = f"https://t.me/{moon_config.MOON_BOT_USERNAME}?start={user_invite['code']}"
        text = (
            f"*Your referral link:* `{invite_link}`\n"
            f"*Your referrals:* {user_invite['count']}\n\n"
            "Refer your friends and earn 50% of their fees\\. \n"
            "Help Moon to build the community and start receiving rewards once we launch in July\\."
        )
        try:
            await query.edit_message_caption(
                caption=text,
                reply_markup=query.message.reply_markup,
                parse_mode=telegram.constants.ParseMode.MARKDOWN_V2,
            )
        except telegram.error.BadRequest as exc:
            if "Message is not modified" not in str(exc):
                raise

    if query.data == "get_referrals":
        await get_referrals(update, context)

    if query.data == "delete_message":
        await context.bot.delete_message(chat_id=query.message.chat_id, message_id=query.message.message_id)


async def echo_videos(update: telegram.Update, context: CallbackContext) -> None:
    print(update.message.video.file_id)
    print(update.message.video.file_unique_id)
