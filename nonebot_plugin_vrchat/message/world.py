from pathlib import Path
from typing import List

from loguru import logger
from nonebot_plugin_htmlrender import template_to_pic as t2p

from ..vrchat import LimitedUserModel


async def draw_world_card_overview(
    users: List[LimitedUserModel],
    # client: Optional[ApiClient] = None,
) -> bytes:

    templates = users
    logger.info(templates)
    return await t2p(
        template_path=str(Path(__file__).parent / "templates"),
        template_name="world_list.html",
        templates={"worlds": templates},
    )


async def draw_world_card(
    user: LimitedUserModel,
    # client: Optional[ApiClient] = None,
) -> bytes:

    templates = user
    logger.info(templates)
    return await t2p(
        template_path=str(Path(__file__).parent / "templates"),
        template_name="world_list.html",
        templates={"worlds": templates},
    )
