from typing import List, Optional

import vrchatapi
from nonebot.log import logger
from vrchatapi.rest import ApiException

from .utils import get_login_msg


async def search_users(
    usr_id: str,
    search: str,
    n: int = 5,
    # developer_type: str = "none"
    offset: int = 1,
) -> Optional[List[vrchatapi.LimitedUser]]:
    """查询用户信息
    search: str | 通过displayName查询,如果为空返回空数组
    n: int | 返回信息数量
    offset: int | 偏移值？
    """
    try:
        api_client = await get_login_msg(usr_id)
    except Exception:
        return None
    api_instance = vrchatapi.UsersApi(api_client)

    try:
        if search.startswith("usr_") and len(search) >= 20:
            api_response: List[vrchatapi.LimitedUser] = [
                api_instance.get_user(
                    search=search,
                    n=n,
                    offset=offset,
                ),  # type: ignore
            ]
            # Search All Users
        else:
            api_response: List[vrchatapi.LimitedUser] = api_instance.search_users(
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
