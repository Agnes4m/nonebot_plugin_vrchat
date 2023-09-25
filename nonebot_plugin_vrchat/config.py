from nonebot import get_driver
from pydantic import BaseModel


class ConfigModel(BaseModel):
    vrc_username: str = ""
    vrc_password: str = ""
    vrc_path: str = "data/vrchat"


config: ConfigModel = ConfigModel.parse_obj(get_driver().config.dict())
