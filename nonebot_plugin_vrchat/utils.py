from pathlib import Path
from typing import Any

import yaml


def load_yaml(file_path: Path) -> Any:
    """加载 YAML 文件"""
    with file_path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def dump_yaml(file_path: Path, data: Any) -> None:
    """保存 YAML 文件"""
    with file_path.open("w", encoding="utf-8") as f:
        yaml.safe_dump(
            data,
            f,
            allow_unicode=True,
            default_flow_style=False,
            indent=2,
            sort_keys=False,
        )
