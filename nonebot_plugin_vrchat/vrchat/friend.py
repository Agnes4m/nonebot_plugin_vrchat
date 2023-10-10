import asyncio
from typing import Dict, List, Optional

import vrchatapi

from .utils import get_login_msg

# from nonebot_plugin_vrchat.config import config

# api_client: vrchatapi.ApiClient = vrchatapi.ApiClient()


async def get_all_friends(usr_id: str) -> Optional[List[vrchatapi.LimitedUser]]:
    # global api_client
    try:
        api_client = await get_login_msg(usr_id)
    except Exception:
        return None
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


async def get_status_emoji(status: str, location: Optional[str]) -> str:
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
    ...
