from typing import List

import vrchatapi
from nonebot_plugin_saa import Image, Text

from .vrchat.friend import get_status_emoji


async def friend_status_msg(msg: List[vrchatapi.LimitedUser]):
    send_msg = []
    for one_dict in msg:
        if send_msg:
            send_msg.append(Text("\n---------------\n"))
        if (
            not one_dict.status
            or not one_dict.location
            or not one_dict.current_avatar_thumbnail_image_url
        ):
            continue
        emo = await get_status_emoji(one_dict.status, one_dict.location)
        send_msg.append(Image(one_dict.current_avatar_thumbnail_image_url))
        send_msg.append(
            Text(
                f"{one_dict.display_name} | {emo}{one_dict.status_description if one_dict.status_description else one_dict.status}",
            ),
        )
    if not send_msg:
        return None
    return send_msg


async def search_usrs_msg(msg: List[vrchatapi.LimitedUser]):
    send_msg = []
    for one_dict in msg:
        if send_msg:
            send_msg.append(Text("\n---------------\n"))
        if (
            one_dict.status is None
            or one_dict.current_avatar_thumbnail_image_url is None
        ):
            continue
        emo = await get_status_emoji(one_dict.status, one_dict.location)
        send_msg.append(Image(one_dict.current_avatar_thumbnail_image_url))
        send_msg.append(
            Text(
                f"{one_dict.display_name} | {emo}{one_dict.status_description if one_dict.status_description else one_dict.status}",
            ),
        )
    if not send_msg:
        return None
    return send_msg
