from typing import Any

from fastapi import APIRouter, Depends

from src.bot.app import register_update
from src.bot.config import moon_config
from src.dependencies import valid_tg_secret_token

router = APIRouter()


@router.post(
    f"/tg/{moon_config.WEBHOOK_RANDOM_PATH}/webhook",
    dependencies=[Depends(valid_tg_secret_token)],
)
async def telegram_webhook(update: dict[str, Any]) -> dict[str, bool]:
    await register_update(update)

    return {"ok": True}
