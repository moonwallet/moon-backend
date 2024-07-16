import telegram
from telegram.ext import CallbackContext

from src.bot import service, utils
from src.bot.config import moon_config
from src.bot.handlers.constants import (
    MESSAGE_DELETE,
    MESSAGE_RESTORE_POINTS,
    MOON_DEMO,
    MOON_POINTS,
    MOON_POINTS_TASK,
    MOON_SAFETY,
    REFERRALS_DASHBOARD,
    REFERRALS_STATS_REFRESH,
    REFERRALS_VIDEO_EXPLANATION,
    X_CONNECT,
    X_TWEET_REFERRAL,
    X_TWEET_REFERRAL_SEND,
)
from src.bot.handlers.points import get_points_task, send_points_dashboard
from src.bot.handlers.referrals import refresh_user_stats, send_referrals_explanation
from src.bot.handlers.start import get_referrals, send_demo_video, send_moon_safety_info
from src.bot.handlers.twitter import send_tweet, send_tweet_referral_menu, send_twitter_redirect_uri


async def query_buttons(update: telegram.Update, context: CallbackContext) -> None:
    query = update.callback_query

    if query.data == REFERRALS_STATS_REFRESH:
        await refresh_user_stats(query, update)

    if query.data == REFERRALS_DASHBOARD:
        await get_referrals(update, context)

    if query.data == REFERRALS_VIDEO_EXPLANATION:
        await send_referrals_explanation(update, context)

    if query.data == MOON_DEMO:
        await send_demo_video(update, context)

    if query.data == MOON_SAFETY:
        await send_moon_safety_info(update, context)

    if query.data == MOON_POINTS:
        await send_points_dashboard(update, context)

    if query.data == MESSAGE_RESTORE_POINTS:
        await send_points_dashboard(update, context, send_message=False)

    if query.data == X_CONNECT:
        await send_twitter_redirect_uri(update, context)

    if query.data == X_TWEET_REFERRAL:
        await send_tweet_referral_menu(update, context)

    if query.data == X_TWEET_REFERRAL_SEND:
        await send_tweet(update, context)

    if query.data.startswith(MOON_POINTS_TASK):
        await get_points_task(update, context)

    if query.data == MESSAGE_DELETE:
        try:
            await context.bot.delete_message(chat_id=query.message.chat_id, message_id=query.message.message_id)
        except telegram.error.BadRequest as exc:
            if "Message can't be deleted for everyone" in str(exc):
                await context.bot.send_video(
                    chat_id=update.effective_chat.id,
                    video=moon_config.START_VIDEO_URL,
                    caption=utils.prepare_start_text(),
                    reply_markup=utils.prepare_start_buttons(),
                )
            else:
                raise

    await query.answer()

    if moon_config.UPDATE_USER_DATA_ON_INTERACTION:
        await service.update_telegram_user(
            telegram_id=str(update.effective_user.id),
            data={
                "username": update.effective_user.username,
                "first_name": update.effective_user.first_name,
                "last_name": update.effective_user.last_name,
            },
        )