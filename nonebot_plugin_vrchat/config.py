# from pathlib import Path
# from typing import Dict, List

# from pydantic import BaseModel, Field
# from ruamel import yaml

# DATA_PATH = Path("data/vrchat")
# CONFIG_PATH = DATA_PATH / "config.yml"
# CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)


# class VrcGroupConfig(BaseModel):
#     enable: bool = Field(default=True, alias="是否启用vrc功能")

#     def update(self, **kwargs):
#         for key, value in kwargs.items():
#             if key in self.__fields__:
#                 self.__setattr__(key, value)


# class VrcConfig(BaseModel):
#     session_expire_timeout: int = Field(default=120, alias="默认验证码时间(秒)")
#     vrc_path: str = Field(default="data/vrchat", alias="插件地址")
#     group_config: Dict[int, VrcGroupConfig] = Field(default_factory=dict, alias="分群配置")

#     def update(self, **kwargs):
#         for key, value in kwargs.items():
#             if key in self.__fields__:
#                 self.__setattr__(key, value)


# class VrChatConfigManager:
#     def __init__(self):
#         self.file_path = CONFIG_PATH
#         if self.file_path.is_file():
#             try:
#                 self.config = VrcConfig.parse_obj(
#                     yaml.load(
#                         self.file_path.read_text(encoding="utf-8"),
#                         Loader=yaml.Loader,
#                     ),
#                 )
#             except Exception:
#                 self.config = VrcConfig()
#         else:
#             self.config = VrcConfig()
#         self.save()

#     def get_group_config(self, group_id: int) -> VrcGroupConfig:
#         if group_id not in self.config.group_config:
#             self.config.group_config[group_id] = VrcGroupConfig()  # type: ignore
#             self.save()
#         return self.config.group_config[group_id]

#     @property
#     def config_list(self) -> List[str]:
#         return list(self.config.dict(by_alias=True).keys())

#     def save(self):
#         with self.file_path.open("w", encoding="utf-8") as f:
#             yaml.dump(
#                 self.config.dict(by_alias=True),
#                 f,
#                 indent=2,
#                 Dumper=yaml.RoundTripDumper,
#                 allow_unicode=True,
#             )


# config_manager = VrChatConfigManager()
# config = config_manager.config
from datetime import timedelta
from pathlib import Path

from nonebot import get_driver
from pydantic import BaseModel


class ConfigModel(BaseModel):
    session_expire_timeout: timedelta

    vrc_path: Path = Path("data/vrchat")


config: ConfigModel = ConfigModel.parse_obj(get_driver().config.dict())
