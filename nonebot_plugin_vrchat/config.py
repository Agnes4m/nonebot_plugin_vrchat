from datetime import timedelta
from pathlib import Path
from typing import Dict, List

from pydantic import BaseModel, Field
from ruamel import yaml

DATA_PATH = Path("data/vrchat")
CONFIG_PATH = DATA_PATH / "config.yml"
CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)


class VrcGroupConfig(BaseModel):
    enable: bool = Field(True, alias="是否启用vrc功能")

    def update(self, **kwargs):
        for key, value in kwargs.items():
            if key in self.__fields__:
                self.__setattr__(key, value)


class VrcConfig(BaseModel):
    session_expire_timeout: timedelta = Field(timedelta(seconds=120), alias="默认验证码时间")
    group_config: Dict[int, VrcGroupConfig] = Field({}, alias="分群配置")

    def update(self, **kwargs):
        for key, value in kwargs.items():
            if key in self.__fields__:
                self.__setattr__(key, value)


class VrChatConfigManager:
    def __init__(self):
        self.file_path = CONFIG_PATH
        if self.file_path.exists():
            self.config = VrcConfig.parse_obj(
                yaml.load(
                    self.file_path.read_text(encoding="utf-8"),
                    Loader=yaml.Loader,
                ),
            )
        else:
            self.config = VrcConfig()  # type: ignore
        self.save()

    def get_group_config(self, group_id: int) -> VrcGroupConfig:
        if group_id not in self.config.group_config:
            self.config.group_config[group_id] = VrcGroupConfig()  # type: ignore
            self.save()
        return self.config.group_config[group_id]

    @property
    def config_list(self) -> List[str]:
        return list(self.config.dict(by_alias=True).keys())

    def save(self):
        with self.file_path.open("w", encoding="utf-8") as f:
            yaml.dump(
                self.config.dict(by_alias=True),
                f,
                indent=2,
                Dumper=yaml.RoundTripDumper,
                allow_unicode=True,
            )


config_manager = VrChatConfigManager()
config = config_manager.config
