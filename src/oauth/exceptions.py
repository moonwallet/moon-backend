from src.exceptions import BadRequest, NotFound
from src.oauth.constants import ErrorCode


class UserAlreadyOauth(BadRequest):
    DETAIL = ErrorCode.USER_ALREADY_OAUTH


class UserInvalidOauth(BadRequest):
    DETAIL = ErrorCode.USER_INVALID_OAUTH


class OauthTokenNotFound(NotFound):
    DETAIL = "Oauth token not found"
