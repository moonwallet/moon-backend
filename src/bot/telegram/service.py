import telegram

from src.bot.telegram.app import moon_app


async def register_update(update):
    await moon_app.process_update(telegram.Update.de_json(update, moon_app.bot))
