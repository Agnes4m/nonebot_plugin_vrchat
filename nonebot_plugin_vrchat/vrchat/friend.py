import asyncio
import json
from typing import Dict, List, Optional

import vrchatapi
from nonebot.log import logger

from ..classes import UsrMsg
from ..config import config
from .cookies import load_cookies
from .utils import get_login_msg

# from nonebot_plugin_vrchat.config import config

# api_client: vrchatapi.ApiClient = vrchatapi.ApiClient()


async def get_all_friends(usr_id: str) -> Optional[List[vrchatapi.LimitedUser]]:
    # global api_client
    try:
        usr_ms = await get_login_msg(usr_id)
    except Exception:
        return None
    usr_msg: UsrMsg = UsrMsg(username=usr_ms["username"], password=usr_ms["password"])
    configuration = vrchatapi.Configuration(
        username=usr_msg.username,
        password=usr_msg.password,
    )
    # configuration.api_key["authCookie"] = usr_msg.cookie

    api_client: vrchatapi.ApiClient = vrchatapi.ApiClient(configuration)
    load_cookies(api_client, "./cookies.txt")
    api_instance = vrchatapi.FriendsApi(api_client)
    friends: List[vrchatapi.LimitedUser] = []
    offset = 0
    while True:
        api_response: List[vrchatapi.LimitedUser] = api_instance.get_friends(
            offset=offset,
            n=60,
            offline=False,
        )  # type: ignore
        if len(api_response) == 0:
            break
        friends.extend(api_response)
        offset += 100
    offset = 0
    while True:
        api_response = api_instance.get_friends(offset=offset, n=100, offline="true")  # type: ignore
        if len(api_response) == 0:
            break
        friends.extend(api_response)
        offset += 100
        await asyncio.sleep(0.5)
    # friend: vrchatapi.LimitedUser
    # friends_map: Dict[str, vrchatapi.LimitedUser] = {}
    # for friend in friends:
    #     friends_map[friend.display_name] = friend
    # logger.info(friends_map)
    # return friends_map
    return friends


friends: Dict[str, vrchatapi.LimitedUser]


async def get_online_friends(usr_id: str):
    """
    Get all online and active(on the website) friends list
    and send it via discord.
    """
    global friends

    with config.vrc_path.joinpath(f"player/9{usr_id}.json").open(
        mode="r",
        encoding="utf-8",
    ) as f:
        usr_dict = json.load(f)
        usr_msg = UsrMsg(**usr_dict)
    configuration = vrchatapi.Configuration(
        username=usr_msg.username,
        password=usr_msg.password,
    )
    # configuration.api_key["authCookie"] = usr_msg.cookie

    api_client: vrchatapi.ApiClient = vrchatapi.ApiClient(configuration)
    load_cookies(api_client, "./cookies.txt")
    try:
        api_instance = vrchatapi.FriendsApi(api_client)
        offset = 0
        online_friends: List[vrchatapi.LimitedUser] = []
        while True:
            api_response = api_instance.get_friends(
                offset=offset,
                n=100,
                offline="false",
            )
            await asyncio.sleep(0.5)
            assert isinstance(api_response, List)
            if len(api_response) == 0:
                break
            online_friends.extend(api_response)
            offset += 100

        msg: str = ""
        for f in online_friends:
            emoji = await get_status_emoji(f.status, f.location)  # type: ignore
            msg += f"{emoji} {f.display_name}\n"
        # await ctx.followup.send(discord.utils.escape_markdown(msg))
        print(msg)
        if msg:
            return msg
    except Exception as e:
        # await ctx.followup.send(f"get_online_friends failed with error: {e}")
        logger.info(e)
        return str(e)


async def get_status_emoji(status: str, location: str) -> str:
    """
    Get the emoji to represent the status.
    """
    if location == "offline":
        if status == "active":
            return "🌐"
        return "⚫"
    if status == "join me":
        return "🔵"
    if status == "active":
        return "🟢"
    if status == "ask me":
        return "🟠"
    if status == "do not disturb":
        return "🔴"
    return "❌"


# async def update_friends_status():
#     global friends
#     logger.info("Strat to update friend status")
#     try:
#         new_friends: Dict[str, vrchatapi.LimitedUser] = await get_all_friends()

#     except Exception:
#         logger.error("get all friends failed")
#         return
#     if not isinstance(new_friends, dict):
#         return
#     # name: str
#     # conf: ListenFriends
#     if len(friends) == 0:
#         friends = new_friends
#         return
# for name, conf in config.listen_friends.items():
#     # find ambiguous dispaly name
#     if name not in new_friends:
#         for n in new_friends:
#             if name in n:
#                 name = n
#     if name not in new_friends or name not in friends:
#         logger.info(f"{name} not found")
#         continue
#     online_just_now = False

#     if (
#         "online" in conf.on_events
#         and friends[name].status == "offline"
#         and new_friends[name].status != "offline"
#     ):
#         online_just_now = True
#         status_emoji = get_status_emoji(
#             new_friends[name].status, new_friends[name].location
#         )
#         for ch_id in conf.to_channels:
#             ch = bot.get_channel(config.channels[ch_id])
#             if ch is None:
#                 continue
#             await ch.send(f"{status_emoji} {name} is online now!")

#     if (
#         "status_change" in conf.on_events
#         and (
#             friends[name].status != new_friends[name].status
#             or (
#                 friends[name].location != new_friends[name].location
#                 and (
#                     friends[name].location == "offline"
#                     or new_friends[name].location == "offline"
#                 )
#             )
#         )
#         and not online_just_now
#     ):
#         old_status_emoji = get_status_emoji(
#             friends[name].status, friends[name].location
#         )
#         status_emoji = get_status_emoji(
#             new_friends[name].status, new_friends[name].location
#         )
#         for ch_id in conf.to_channels:
#             ch = bot.get_channel(config.channels[ch_id])
#             if ch is None:
#                 continue
#             await ch.send(
#                 f"{name} status changed: {old_status_emoji} -> {status_emoji}"
#             )
# friends = new_friends


if __name__ == "__main__":
    asyncio.run(get_online_friends(usr_id="735803792"))
