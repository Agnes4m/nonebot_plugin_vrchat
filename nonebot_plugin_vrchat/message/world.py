from typing import List, Optional

from ..vrchat import ApiClient, LimitedUserModel


async def draw_world_card_overview(
    users: List[LimitedUserModel],
    group: bool = True,
    client: Optional[ApiClient] = None,
    title: str = "好友列表",
) -> bytes: ...
