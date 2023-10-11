from typing import List, Optional

import vrchatapi
from nonebot.log import logger
from vrchatapi.rest import ApiException

from .utils import get_login_msg


async def wolrd_base(usr_id):
    try:
        api_client = await get_login_msg(usr_id)
    except Exception:
        return None
    return vrchatapi.WorldsApi(api_client)


async def worlds_search(
    usr_id: str,
    search: str,
    n: int = 10,
    offset: int = 1,
) -> Optional[List[vrchatapi.LimitedWorld]]:
    """查询用户信息
    文档参考:https://github.com/vrchatapi/vrchatapi-python/blob/main/docs/WorldsApi.md#search_worlds
    search: str | 通过displayName查询,如果为空返回空数组
    n: int | 返回信息数量
    offset: int | 偏移值？
    """
    api_instance: Optional[vrchatapi.WorldsApi] = await wolrd_base(usr_id)
    if api_instance is None:
        return None
    try:
        if search.startswith("usr_") and len(search) >= 20:
            api_response: List[vrchatapi.LimitedWorld] = [
                api_instance.get_world(
                    world_id=search,
                ),  # type: ignore
            ]
            # Search All Users
        else:
            api_response: List[vrchatapi.LimitedWorld] = api_instance.search_worlds(
                search=search,
                n=n,
                offset=offset,
            )  # type: ignore
        logger.info(api_response)
        if api_response:
            return api_response
    except ApiException as e:
        logger.warning("Exception when calling UsersApi->search_users: %s\n" % e)
    return None
