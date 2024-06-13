from src.config import CustomBaseSettings


class MoonConfig(CustomBaseSettings):
    MOON_WEBHOOK_DOMAIN: str
    MOON_TELEGRAM_BOT_TOKEN: str
    MOON_WEBHOOK_RANDOM_PATH: str = "8hUaWr3EHDasiWekc6U1KYqwANznLHrPW7"
    MOON_BOT_USERNAME: str = "moonWallet_solbot"
    MOON_START_VIDEO_URL: str

    @property
    def moon_telegram_webhook_url(self) -> str:
        return f"{self.MOON_WEBHOOK_DOMAIN}/moon/telegram/{self.MOON_WEBHOOK_RANDOM_PATH}/webhook"


moon_config = MoonConfig()