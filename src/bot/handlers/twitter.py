import telegram
from telegram.ext import CallbackContext

from src import twitter
from src.bot import service, utils
from src.bot.handlers import constants as handlers_constants
from src.oauth import service as oauth_service
from src.points import service as points_service


async def send_twitter_redirect_uri(update: telegram.Update, _: CallbackContext, failed_to_send: bool = False):
    user_id = str(update.effective_user.id)
    query = update.callback_query

    tasks_buttons = [
        [telegram.InlineKeyboardButton("Go Back", callback_data=handlers_constants.MESSAGE_RESTORE_POINTS)],
    ]

    oauth_data = await oauth_service.get_oauth_by_user_id(user_id)
    if oauth_data and oauth_data['access_token']:
        await query.edit_message_caption(
            caption="You have already connected your Twitter account.",
            reply_markup=telegram.InlineKeyboardMarkup(tasks_buttons),
        )
        return

    auth_data = await twitter.get_authorization_data()
    await oauth_service.init_oauth_twitter(user_id, auth_data)

    text = f"Click [this]({auth_data.redirect_uri}) link to connect your Twitter account"
    if failed_to_send:
        text = f"It looks like you have not connected the Twitter first\n\n{text}"

    await query.edit_message_caption(
        caption=text,
        reply_markup=telegram.InlineKeyboardMarkup(tasks_buttons),
        parse_mode=telegram.constants.ParseMode.MARKDOWN_V2,
    )


async def send_tweet_referral_menu(update: telegram.Update, callback: CallbackContext):
    user_id = str(update.effective_user.id)
    query = update.callback_query

    oauth_data = await oauth_service.get_oauth_by_user_id(user_id)
    if not oauth_data:
        return await send_twitter_redirect_uri(update, callback)

    user_invite = await service.get_invite_with_count(referrer_telegram_id=str(update.effective_user.id))
    invite_link = utils.prepare_invite_link(user_invite["code"], mark_down_safe=True)

    text = (
        "Share your referral link on Twitter and earn your points\\.\n\n"
        "There is no need to struggle with text \\- we have prepared a tweet for you\\.\n\n"
        "Just click the button below and we will automatically tweet this post for you:\n\n"
    )

    invite_text = (
        ">Your private invite to Moon, a Telegram wallet for Solana memecoin Discover, "
        "Analyze and Trade memecoins in one place\\.\n>\n"
        ">Get your first 100 Moon Points for joining\n>\n"
        f">`{invite_link}`"
    )

    text = f"{text}{invite_text}"

    tasks_buttons = [
        [telegram.InlineKeyboardButton("Post a Tweet", callback_data=handlers_constants.X_TWEET_REFERRAL_SEND)],
        [telegram.InlineKeyboardButton("Go Back", callback_data=handlers_constants.MESSAGE_RESTORE_POINTS)],
    ]

    await query.edit_message_caption(
        caption=text,
        reply_markup=telegram.InlineKeyboardMarkup(tasks_buttons),
        parse_mode=telegram.constants.ParseMode.MARKDOWN_V2,
    )


async def send_tweet(update: telegram.Update, context: CallbackContext):
    user_id = str(update.effective_user.id)
    oauth_data = await oauth_service.get_oauth_by_user_id(user_id)
    if not oauth_data:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="You need to connect your Twitter account first.",
        )
        return

    user_invite = await service.get_invite_with_count(referrer_telegram_id=str(update.effective_user.id))
    invite_link = utils.prepare_invite_link(user_invite["code"])
    invite_text = (
        "Your private invite to Moon, a Telegram wallet for Solana memecoin Discover, "
        "Analyze and Trade memecoins in one place.\n\n"
        "🌚 Get your first 100 Moon Points for joining\n\n"
        f"{invite_link}"
    )

    created_tweet = await twitter.tweet(oauth_data, invite_text)

    x_send_task = await points_service.get_task_by_slug("x_tweet_referral")
    if x_send_task:
        await points_service.complete_task(user_id, x_send_task["id"], x_send_task["points"])

    tasks_buttons = [
        [telegram.InlineKeyboardButton("Go Back", callback_data=handlers_constants.MESSAGE_RESTORE_POINTS)],
    ]

    query = update.callback_query
    await query.edit_message_caption(
        caption=(
            "Awesome! Tweet was sent successfully.\n\n"
            ""
            f"Check it out: https://x.com/{oauth_data['screen_name']}/status/{created_tweet['id']}"
        ),
        reply_markup=telegram.InlineKeyboardMarkup(tasks_buttons),
    )
