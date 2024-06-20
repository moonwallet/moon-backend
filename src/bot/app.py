from datetime import timedelta
from typing import Any

import telegram
from telegram.ext import ApplicationBuilder

from src.bot import handlers
from src.bot.config import moon_config
from src.config import settings
from src.redis import RedisData, set_redis_key

moon_app = ApplicationBuilder().token(moon_config.TELEGRAM_BOT_TOKEN).updater(None).build()

moon_app.add_error_handler(handlers.send_error_message)
moon_app.add_handler(telegram.ext.CommandHandler("start", handlers.start))
moon_app.add_handler(telegram.ext.CallbackQueryHandler(handlers.query_buttons))
# moon_app.add_handler(telegram.ext.MessageHandler(telegram.ext.filters.VIDEO, handlers.echo_videos))
# moon_app.add_handler(telegram.ext.MessageHandler(None, handlers.echo_messages))


async def register_update(update: dict[str, Any]) -> None:
    await moon_app.process_update(telegram.Update.de_json(update, moon_app.bot))


async def set_webhook():
    return
    rate_limit_key = "moon:tg:webhook"

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
