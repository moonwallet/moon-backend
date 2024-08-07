import urllib

import telegram
from sqlalchemy.ext.asyncio import AsyncConnection
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext

from src.bot import service
from src.bot.config import moon_config
from src.bot.handlers import constants as handlers_constants
from src.bot.schemas import TgUserCreate
from src.points import service as points_service


async def register_user(
    db_connection: AsyncConnection, update: telegram.Update, context: CallbackContext
) -> dict[str, bool] | None:
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

        return None

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
        return {
            "used_invite": False,
        }

    invite_code = context.args[0]
    if user_invite["code"] == invite_code:  # is self-invite
        return {
            "used_invite": True,
            "self_invite": True,
            "invalid_invite": True,
        }

    if invite := await service.get_invite_with_count(code=invite_code, db_connection=db_connection):
        await service.invite_user(invite["id"], user_id, db_connection)

        inviter_account = await service.get_telegram_user_by_id(invite["referrer_telegram_id"], db_connection)
        inviter_username = f"@{inviter_account['username']}" if inviter_account["username"] else "anon"
        inviter_username = inviter_username.replace("_", "\\_")

        inviter_points = await points_service.count_user_points(invite["referrer_telegram_id"])

        return {
            "used_invite": True,
            "invited_by": inviter_username,
            "inviter_points": inviter_points["points"],
            "total_invites": invite["count"] + 1,
        }

    return {
        "used_invite": True,
        "invalid_invite": True,
        "invite_code": invite_code,
    }


def prepare_referrals_stat_text(
    invites_count: int,
    invite_link: str,
) -> str:
    return (
        f"*Your referral link:* `{invite_link}`\n"
        f"*Your referrals:* {invites_count}\n\n"
        "Refer your friends and get an exclusive 🔥 50% 🔥 revenue share\\. \n\n"
        "You'll start receiving rewards once we launch in August\\."
    )


def prepare_invite_link(invite_code: str, mark_down_safe: bool = False) -> str:
    if not mark_down_safe:
        return f"https://t.me/{moon_config.BOT_USERNAME}?start={invite_code}"

    return f"https://t\\.me/{moon_config.BOT_USERNAME}?start\\={invite_code}"


def prepare_start_text() -> str:
    return (
        "*Welcome to Moon — Telegram wallet for Solana memecoins going live in August\\.*\n\n"
        "While you are early:\n\n"
        "🌚 Complete tasks, earn Moon Points and increase your future rewards allocations\n\n"
        "🎁 Invite your frens and get an exclusive 50% revenue share\n\n"
    )


def prepare_start_buttons() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton("🌚 Moon Points", callback_data=handlers_constants.MOON_POINTS)],
        [InlineKeyboardButton("🎁 Invite friends", callback_data=handlers_constants.REFERRALS_DASHBOARD)],
        [InlineKeyboardButton("👀 Tell me more about Moon", callback_data=handlers_constants.MOON_DEMO)],
        [InlineKeyboardButton("Join Telegram Community", url="https://t.me/moon_wallet_xyz")],
        [InlineKeyboardButton("Follow us on X", url="https://x.com/moon_wallet_xyz")],
    ]

    return InlineKeyboardMarkup(buttons)


def prepare_safety_info_buttons() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton("🌚 Tell me more about Moon", callback_data=handlers_constants.MOON_DEMO)],
        [InlineKeyboardButton("Go Back", callback_data=handlers_constants.MESSAGE_DELETE)],
    ]

    return InlineKeyboardMarkup(buttons)


def prepare_safety_info_text() -> str:
    return (
        "That's a good question, and here are the good reasons to trust us:\n\n"
        "1️⃣ Our founders have open identities: [Dima](https://www\\.linkedin\\.com/in/vazhenin), "
        "[Yera](https://www\\.linkedin\\.com/in/zhanymkanov)\n\n"
        "2️⃣ We actively participate in Solana events: "
        "[SolanaKZ](https://x\\.com/Rustemzzzz/status/1806381234437685634)\n\n"
        "3️⃣ The team has a solid proof of work — previously we built [dappSheriff](https://dappsheriff\\.com), "
        "a web3 reviews platform with over 2m reviews that was "
        "[supported by Linea](https://x\\.com/LineaBuild/status/1760068999587471857) blockchain\\.\n\n"
        "4️⃣ We are part of the [Backdrop](https://x.com/withBackdrop) accelerator program\\.\n\n"
        "5️⃣ We use open\\-source APIs of Raydium & Jupiter that are proven by time and audited by the best teams\\. "
        "The wallet itself is non\\-custodial, i\\.e\\. we do not interact with users' "
        "funds anywhere and don't have any access to them\\.\n\n"
    )


def prepare_referrals_buttons(invite_link: str) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(
                "Share in Telegram",
                switch_inline_query=(
                    "\nGet your early access to Moon 🌚 - Telegram Wallet for Solana Memecoins:\n" f"{invite_link}"
                ),
            )
        ],
        [
            InlineKeyboardButton("Connect X", callback_data=handlers_constants.X_CONNECT),
        ],
        [
            InlineKeyboardButton("Share on X", url=_prepare_twitter_link(invite_link)),
        ],
        [InlineKeyboardButton("How do referrals work?", callback_data=handlers_constants.REFERRALS_VIDEO_EXPLANATION)],
        [InlineKeyboardButton("Refresh statistics", callback_data=handlers_constants.REFERRALS_STATS_REFRESH)],
        [InlineKeyboardButton("Go Back", callback_data=handlers_constants.MESSAGE_DELETE)],
    ]

    return InlineKeyboardMarkup(buttons)


def prepare_referrals_explanation_buttons(invite_link: str) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(
                "Share in Telegram",
                switch_inline_query=(
                    "\nGet your early access to Moon 🌚 - Telegram Wallet for Solana Memecoins:\n" f"{invite_link}"
                ),
            )
        ],
        [
            InlineKeyboardButton("Share on X", url=_prepare_twitter_link(invite_link)),
        ],
        [
            InlineKeyboardButton("Show statistics", callback_data=handlers_constants.REFERRALS_DASHBOARD),
        ],
        [InlineKeyboardButton("Go Back", callback_data=handlers_constants.MESSAGE_DELETE)],
    ]

    return InlineKeyboardMarkup(buttons)


def prepare_send_demo_buttons() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton("🎁 Invite friends", callback_data=handlers_constants.REFERRALS_DASHBOARD)],
        [InlineKeyboardButton("🔓 How safe is Moon?", callback_data=handlers_constants.MOON_SAFETY)],
        [InlineKeyboardButton("Join Telegram Community", url="https://t.me/moon_wallet_xyz")],
        [InlineKeyboardButton("Follow us on X", url="https://x.com/moon_wallet_xyz")],
        [InlineKeyboardButton("Go Back", callback_data=handlers_constants.MESSAGE_DELETE)],
    ]

    return InlineKeyboardMarkup(buttons)


def _prepare_twitter_link(invite_link: str) -> str:
    encoded_text = urllib.parse.quote(
        "Here is your private invite to @moon_wallet_xyz, a Telegram wallet for Solana memecoins. "
        "Discover, analyze and trade memecoins in one place.\n\n"
        "Get your exclusive 250 Moon Points for joining early:\n\n"
        f"{invite_link}"
    )

    return f"https://twitter.com/intent/tweet?text={encoded_text}"
