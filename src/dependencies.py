from fastapi import Header, HTTPException, Request

from src.config import settings
from src.schemas import RequestData


async def valid_tg_secret_token(
    secret_token: str = Header(alias="X-Telegram-Bot-Api-Secret-Token"),
) -> None:
    if secret_token != settings.TELEGRAM_SECRET_TOKEN:
        raise HTTPException(status_code=403, detail="Invalid secret token")


def parse_request_data(
    request: Request,
    user_agent: str = Header(...),
) -> RequestData:
    if request.client is None:
        raise ValueError("Request client is empty")

    return RequestData(
        user_agent=user_agent,
        user_ip=request.client.host,
    )
