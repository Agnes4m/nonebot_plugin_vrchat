import ujson as json

from ..config import config


async def get_login_msg(usr_id: str):
    with config.vrc_path.joinpath(f"player/{usr_id}.json").open(
        mode="r",
        encoding="utf-8",
    ) as f:
        usr_ms: dict = json.load(f)
    return usr_ms
