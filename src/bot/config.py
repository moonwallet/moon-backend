from pydantic_settings import SettingsConfigDict

from src.config import CustomBaseSettings


class MoonConfig(CustomBaseSettings):
    model_config = SettingsConfigDict(env_prefix="MOON_")

    WEBHOOK_DOMAIN: str
    TELEGRAM_BOT_TOKEN: str
    WEBHOOK_RANDOM_PATH: str = "8hUaWr3EHDasiWekc6U1KYqwANznLHrPW7"
    BOT_USERNAME: str = "moonWallet_solbot"
    START_VIDEO_URL: str
    REFERRAL_EXPLANATION_VIDEO_URL: str
    DEMO_VIDEO_URL: str
    REFERRALS_PREVIEW_IMAGE_URL: str = "https://cdn.dappsheriff.com/misc/moon_preview.png"
    ADMIN_ID: str = ""

    NOTIFICATIONS_CHAT_ID: str
    NOTIFICATIONS_CHAT_TOPIC_ID: str

    UPDATE_USER_DATA_ON_INTERACTION: bool = True

    SUPPORT_CHAT_LINK: str

    def moon_telegram_webhook_url(self, domain: str) -> str:
        return f"{domain}/tg/{self.WEBHOOK_RANDOM_PATH}/webhook"


moon_config = MoonConfig()
