import asyncio
from typing import Dict, List

import vrchatapi

from .cookies import load_cookies

# from nonebot_plugin_vrchat.config import config

api_client: vrchatapi.ApiClient = vrchatapi.ApiClient()


async def get_all_friends(usr_id: str) -> Dict[str, vrchatapi.LimitedUser]:
    global api_client
    load_cookies(api_client, filename=usr_id)
    api_instance = vrchatapi.FriendsApi(api_client)
    friends: List[vrchatapi.LimitedUser] = []
    offset = 0
    while True:
        api_response: List[vrchatapi.LimitedUser] = api_instance.get_friends(
            offset=offset,
            n=100,
            offline="false",
        )
        if len(api_response) == 0:
            break
        friends.extend(api_response)
        offset += 100
    offset = 0
    while True:
        api_response = api_instance.get_friends(offset=offset, n=100, offline="true")
        if len(api_response) == 0:
            break
        friends.extend(api_response)
        offset += 100
        await asyncio.sleep(0.5)
    friend: vrchatapi.LimitedUser
    friends_map: Dict[str, vrchatapi.LimitedUser] = {}
    for friend in friends:
        friends_map[friend.display_name] = friend
    return friends_map


async def get_online_friends(usr_id: str):
    """
    Get all online and active(on the website) friends list
    and send it via discord.
    """

    global api_client
    load_cookies(api_client, filename=usr_id)
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
            emoji = get_status_emoji(f.status, f.location)
            msg += f"{emoji} {f.display_name}\n"
        # await ctx.followup.send(discord.utils.escape_markdown(msg))
        print(msg)
    except Exception as e:
        # await ctx.followup.send(f"get_online_friends failed with error: {e}")
        print(e)


friends: Dict[str, vrchatapi.LimitedUser]


def get_status_emoji(status: str, location: str) -> str:
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
#     global friends, bot
#     logging.info("Strat to update friend status")
#     try:
#         new_friends = await get_all_friends()
#     except:
#         logging.error("get all friends failed")
#         return
#     name: str
#     conf: ListenFriends
#     if len(friends) == 0:
#         friends = new_friends
#         return
#     for name, conf in config.listen_friends.items():
#         # find ambiguous dispaly name
#         if name not in new_friends.keys():
#             for n in new_friends.keys():
#                 if name in n:
#                     name = n
#         if name not in new_friends.keys() or name not in friends.keys():
#             logging.info(f"{name} not found")
#             continue
#         online_just_now = False

#         if (
#             "online" in conf.on_events
#             and friends[name].status == "offline"
#             and not new_friends[name].status == "offline"
#         ):
#             online_just_now = True
#             status_emoji = get_status_emoji(
#                 new_friends[name].status, new_friends[name].location
#             )
#             for ch_id in conf.to_channels:
#                 ch = bot.get_channel(config.channels[ch_id])
#                 if ch is None:
#                     continue
#                 await ch.send(f"{status_emoji} {name} is online now!")

#         if (
#             "status_change" in conf.on_events
#             and (
#                 friends[name].status != new_friends[name].status
#                 or (
#                     friends[name].location != new_friends[name].location
#                     and (
#                         friends[name].location == "offline"
#                         or new_friends[name].location == "offline"
#                     )
#                 )
#             )
#             and not online_just_now
#         ):
#             old_status_emoji = get_status_emoji(
#                 friends[name].status, friends[name].location
#             )
#             status_emoji = get_status_emoji(
#                 new_friends[name].status, new_friends[name].location
#             )
#             for ch_id in conf.to_channels:
#                 ch = bot.get_channel(config.channels[ch_id])
#                 if ch is None:
#                     continue
#                 await ch.send(
#                     f"{name} status changed: {old_status_emoji} -> {status_emoji}"
#                 )
#     friends = new_friends

if __name__ == "__main__":
    asyncio.run(get_online_friends(usr_id="735803792"))
