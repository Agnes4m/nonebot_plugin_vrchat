import ujson as json
import vrchatapi

from ..classes import UsrMsg
from ..config import config
from .cookies import load_cookies


async def get_login_msg(usr_id: str):
    with config.vrc_path.joinpath(f"player/{usr_id}.json").open(
        mode="r",
        encoding="utf-8",
    ) as f:
        usr_ms: dict = json.load(f)
    usr_msg: UsrMsg = UsrMsg(username=usr_ms["username"], password=usr_ms["password"])
    configuration = vrchatapi.Configuration(
        username=usr_msg.username,
        password=usr_msg.password,
    )
    # configuration.api_key["authCookie"] = usr_msg.cookie

    api_client: vrchatapi.ApiClient = vrchatapi.ApiClient(configuration)
    load_cookies(api_client, "./cookies.txt")
    return api_client
