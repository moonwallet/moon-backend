from pydantic import BaseModel, Field, HttpUrl


class OauthRedirectUri(BaseModel):
    redirect_uri: HttpUrl


class TwitterOauth1TokenData(BaseModel):
    oauth_token: str
    oauth_token_secret: str
    redirect_uri: HttpUrl


class TwitterMeOauth(BaseModel):
    is_connected: bool


class TwitterProfile(BaseModel):
    twitter_id: str
    screen_name: str
    name: str | None = None
    description: str | None = None
    image_url: str | None = Field(None, alias="profile_image_url")
