from datetime import timedelta
from pathlib import Path

from nonebot import get_driver
from pydantic import BaseModel


class ConfigModel(BaseModel):
    session_expire_timeout: timedelta

    vrc_path: Path = Path("data/vrchat")


config: ConfigModel = ConfigModel.parse_obj(get_driver().config.dict())
