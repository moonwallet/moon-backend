from src.config import CustomBaseSettings


class OauthSettings(CustomBaseSettings):
    OAUTH_TWITTER_REDIRECT_URI: str = "https://moonwallet.xyz/twitter"


oauth_settings = OauthSettings()
