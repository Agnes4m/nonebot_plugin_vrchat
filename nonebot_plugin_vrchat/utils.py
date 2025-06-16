from pathlib import Path
from typing import Any

from nonebot_plugin_session import SessionId, SessionIdType
from ruamel.yaml import YAML
from typing_extensions import Annotated

yaml = YAML(typ="safe")
yaml.indent = 2
yaml.allow_unicode = True
yaml.default_flow_style = False


def load_yaml(file_path: Path) -> Any:
    with file_path.open("r", encoding="u8") as f:
        return yaml.load(f)


def dump_yaml(file_path: Path, data: Any) -> None:
    with file_path.open("w", encoding="u8") as f:
        yaml.dump(data, f)
