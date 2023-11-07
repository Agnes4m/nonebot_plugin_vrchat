from datetime import timedelta
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from nonebot import get_driver
from pydantic import BaseModel, PrivateAttr
from pydantic.fields import Field

from .utils import dump_yaml, load_yaml

DATA_DIR = Path.cwd() / "data" / "vrchat"
DATA_DIR.mkdir(parents=True, exist_ok=True)

PLUGIN_CONFIG_PATH = DATA_DIR / "config.yml"
SESSION_CONFIG_PATH = DATA_DIR / "session_config.yml"


class ConfigBaseModel(BaseModel):
    _path: Path = PrivateAttr(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self._path:
            raise ValueError("ConfigBaseModel must be subclassed with _path set")
        self.update()

    def read(self) -> Dict[str, Any]:
        if not self._path.exists():
            self.save()
            return {}
        return load_yaml(self._path)

    def update(self):
        for k, v in self.read().items():
            if k in self.__fields__:
                setattr(self, k, v)

    def save(self):
        data = self.dict(by_alias=True)
        if "__root__" in data:
            data = data["__root__"]
        dump_yaml(self._path, data)


# region env config


class EnvConfig(BaseModel):
    session_expire_timeout: timedelta


env_config = EnvConfig.parse_obj(get_driver().config)


# endregion


# region plugin config


class PluginConfig(ConfigBaseModel):
    _path = PrivateAttr(PLUGIN_CONFIG_PATH)

    locale: str = "zh-CN"


plugin_config = PluginConfig()


# endregion


# region session config


class SessionConfig(BaseModel):
    enable: bool = True
    locale: Optional[str] = None


default_session_config = SessionConfig()


class SessionConfigManager(ConfigBaseModel):
    _path = PrivateAttr(SESSION_CONFIG_PATH)
    __root__: Dict[str, SessionConfig] = Field(default_factory=dict)

    def __getitem__(self, session_id: str) -> SessionConfig:
        return self.__root__[session_id]

    def __setitem__(self, session_id: str, config: SessionConfig) -> None:
        self.__root__[session_id] = config
        self.save()

    def __delitem__(self, session_id: str) -> None:
        del self.__root__[session_id]
        self.save()

    def __contains__(self, session_id: str) -> bool:
        return session_id in self.__root__

    def get(
        self,
        *session_ids: str,
    ) -> Tuple[SessionConfig, Optional[str]]:
        """
        按 session_ids 的顺序返回第一个匹配的 SessionConfig。

        Args:
            *session_ids: 会话 ID 列表。

        Returns:
            Tuple[SessionConfig 实例, 该实例所属的 Session ID]

            注意当返回的 Session ID 为 None 时，不会新建 SessionConfig，
            而是使用 **共享的** 默认 SessionConfig 实例，
            所以请尽量 **不要直接修改** 返回的 SessionConfig！
        """

        for session in session_ids:
            if session in self.__root__:
                return self.__root__[session], session
        return default_session_config, None


session_config = SessionConfigManager()


# endregion
