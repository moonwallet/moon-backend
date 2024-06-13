from typing import Any

from fastapi import APIRouter, Depends

from src.bot.config import moon_config
from src.bot.telegram import service as telegram_service
from src.dependencies import valid_tg_secret_token

router = APIRouter(prefix="/moon")


@router.post(
    f"/telegram/{moon_config.MOON_WEBHOOK_RANDOM_PATH}/webhook",
    dependencies=[Depends(valid_tg_secret_token)],
)
async def telegram_webhook(update: dict[str, Any]) -> dict[str, bool]:
    await telegram_service.register_update(update)

    return {"ok": True}
