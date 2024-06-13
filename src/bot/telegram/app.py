from datetime import timedelta

import telegram
from telegram.ext import ApplicationBuilder

from src.config import settings
from src.bot.config import moon_config
from src.bot.telegram import handlers
from src.redis import RedisData, get_by_key, set_redis_key

moon_app = ApplicationBuilder().token(moon_config.MOON_TELEGRAM_BOT_TOKEN).updater(None).build()

# Register handlers
moon_app.add_handler(telegram.ext.CommandHandler("start", handlers.start))
moon_app.add_handler(telegram.ext.CallbackQueryHandler(handlers.query_buttons))
moon_app.add_handler(telegram.ext.MessageHandler(telegram.ext.filters.VIDEO, handlers.echo_videos))


async def set_webhook():
    rate_limit_key = "moon:tg:webhook"
    if await get_by_key(rate_limit_key):
        return

    await set_redis_key(
        RedisData(
            key=rate_limit_key,
            value="1",
            ttl=timedelta(minutes=1),
        )
    )
    await moon_app.bot.set_webhook(
        moon_config.moon_telegram_webhook_url,
        secret_token=settings.TELEGRAM_SECRET_TOKEN,
    )
