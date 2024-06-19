from src.schemas import CustomModel


class TgUserCreate(CustomModel):
    telegram_id: str
    chat_id: str
    username: str | None = None
    first_name: str | None = None
    last_name: str | None = None
