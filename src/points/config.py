from src.config import CustomBaseSettings


class PointsSettings(CustomBaseSettings):
    X_CONNECTED_TASK_SLUG: str = "x_connect"


points_settings = PointsSettings()
