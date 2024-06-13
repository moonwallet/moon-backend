from fastapi import Header, HTTPException

from src.config import settings


async def valid_tg_secret_token(
    secret_token: str = Header(alias="X-Telegram-Bot-Api-Secret-Token"),
) -> None:
    if secret_token != settings.TELEGRAM_SECRET_TOKEN:
        raise HTTPException(status_code=403, detail="Invalid secret token")
