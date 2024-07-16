import telegram
from telegram.ext import CallbackContext

from src.bot import service, utils
from src.bot.config import moon_config


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
