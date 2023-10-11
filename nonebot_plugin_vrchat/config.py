from pathlib import Path

from nonebot import get_driver
from pydantic import BaseModel


class ConfigModel(BaseModel):
    vrc_username: str = ""
    vrc_password: str = ""
    vrc_path: Path = Path("data/vrchat")


config: ConfigModel = ConfigModel.parse_obj(get_driver().config.dict())

PLAYER_PATH = config.vrc_path / "player"
PLAYER_PATH.mkdir(parents=True, exist_ok=True)
