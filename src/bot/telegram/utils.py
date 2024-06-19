import urllib

import telegram
from sqlalchemy.ext.asyncio import AsyncConnection
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext

from src.bot import service
from src.bot.config import moon_config
from src.bot.schemas import TgUserCreate


async def register_user(db_connection: AsyncConnection, update: telegram.Update, context: CallbackContext) -> bool:
    """Register user in the database. Return True if user is created."""
    user_id = str(update.effective_user.id)
    if await service.get_telegram_user_by_id(user_id, db_connection):
        if moon_config.UPDATE_USER_DATA_ON_INTERACTION:
            await service.update_telegram_user(
                telegram_id=user_id,
                data={
                    "username": update.effective_user.username,
                    "first_name": update.effective_user.first_name,
                    "last_name": update.effective_user.last_name,
                },
            )

        return False

    await service.insert_telegram_user(
        TgUserCreate(
            telegram_id=user_id,
            chat_id=str(update.effective_chat.id),
            username=update.effective_user.username,
            first_name=update.effective_user.first_name,
            last_name=update.effective_user.last_name,
        ),
        db_connection=db_connection,
    )

    user_invite = await service.create_user_invite(user_id, db_connection)
    if not user_invite:  # magically, user has already an invite code
        user_invite = await service.get_invite(referrer_telegram_id=user_id, db_connection=db_connection)

    if not context.args:  # no invite code
        return True

    invite_code = context.args[0]
    if user_invite["code"] == invite_code:  # is self-invite
        return True

    if invite := await service.get_invite(code=invite_code, db_connection=db_connection):
        await service.invite_user(invite["id"], user_id, db_connection)


def prepare_referrals_stat_text(
    invites_count: int,
    invite_link: str,
) -> str:
    return (
        f"*Your referral link:* `{invite_link}`\n"
        f"*Your referrals:* {invites_count}\n\n"
        "Refer your friends and get an exclusive 🔥 50% 🔥 revenue share\\. \n\n"
        "You'll start receiving rewards once we launch in July\\."
    )


def prepare_invite_link(invite_code: str) -> str:
    return f"https://t.me/{moon_config.MOON_BOT_USERNAME}?start={invite_code}"


def prepare_start_text() -> str:
    return (
        "Welcome to Moon - Telegram wallet for Solana memecoins.\n\n"
        "We are going live in July. Meanwhile, invite your friends to get an exclusive 🔥 50% 🔥 revenue share!"
    )


def prepare_start_buttons() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton("🎁 Invite friends - get 50% from their fees", callback_data="get_referrals")],
        [InlineKeyboardButton("Join Telegram Community", url="https://t.me/moon_wallet_xyz")],
        [InlineKeyboardButton("Follow us on X", url="https://x.com/moon_wallet_xyz")],
    ]

    return InlineKeyboardMarkup(buttons)


def prepare_referrals_buttons(invite_link: str) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(
                "Share with Telegram Contacts",
                switch_inline_query=(
                    "\nGet your early access to Moon 🌚 - Telegram Wallet for Solana Memecoins:\n" f"{invite_link}"
                ),
            )
        ],
        [
            InlineKeyboardButton("Share on X", url=_prepare_twitter_link(invite_link)),
        ],
        [InlineKeyboardButton("Refresh statistics", callback_data="refresh_stat")],
        [InlineKeyboardButton("Go Back", callback_data="delete_message")],
    ]

    return InlineKeyboardMarkup(buttons)


def _prepare_twitter_link(invite_link: str) -> str:
    encoded_text = urllib.parse.quote(
        f"Get your early access to Moon 🌚 - Telegram Wallet for Solana Memecoins:\n{invite_link}"
    )

    return f"https://twitter.com/intent/tweet?text={encoded_text}"
