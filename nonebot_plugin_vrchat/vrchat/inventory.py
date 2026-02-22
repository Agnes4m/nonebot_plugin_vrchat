from typing import Awaitable, List, Optional, cast

from nonebot.utils import run_sync
from vrchatapi import ApiClient, InventoryApi

from .types import InventoryItemModel, InventoryModel, InventoryTemplateModel
from .utils import user_agent


async def get_inventory(client: ApiClient) -> InventoryModel:
    """获取用户库存信息

    Args:
        client: ApiClient 实例

    Returns:
        库存信息
    """
    api = InventoryApi(client)
    result = await cast(
        "Awaitable[dict]",
        run_sync(api.get_inventory)(),
    )
    return InventoryModel(**result) if isinstance(result, dict) else InventoryModel.model_validate({})


async def get_own_inventory_item(
    client: ApiClient,
    item_id: str,
) -> InventoryItemModel:
    """获取用户库存物品信息

    Args:
        client: ApiClient 实例
        item_id: 物品 ID

    Returns:
        物品信息
    """
    api = InventoryApi(client)
    result = await cast(
        "Awaitable[dict]",
        run_sync(api.get_own_inventory_item)(inventory_item_id=item_id),
    )
    return InventoryItemModel(**result) if isinstance(result, dict) else InventoryItemModel.model_validate({})


async def get_user_inventory_item(
    client: ApiClient,
    user_id: str,
    item_id: str,
) -> InventoryItemModel:
    """获取其他用户库存物品信息

    Args:
        client: ApiClient 实例
        user_id: 用户 ID
        item_id: 物品 ID

    Returns:
        物品信息
    """
    api = InventoryApi(client)
    result = await cast(
        "Awaitable[dict]",
        run_sync(api.get_user_inventory_item)(
            user_id=user_id,
            inventory_item_id=item_id,
        ),
    )
    return InventoryItemModel(**result) if isinstance(result, dict) else InventoryItemModel.model_validate({})


async def update_own_inventory_item(
    client: ApiClient,
    item_id: str,
    update_inventory_item_request: dict,
) -> InventoryItemModel:
    """更新用户库存物品信息

    Args:
        client: ApiClient 实例
        item_id: 物品 ID
        update_inventory_item_request: 更新请求对象

    Returns:
        更新后的物品信息
    """
    from vrchatapi.models import UpdateInventoryItemRequest

    api = InventoryApi(client)
    result = await cast(
        "Awaitable[dict]",
        run_sync(api.update_own_inventory_item)(
            inventory_item_id=item_id,
            update_inventory_item_request=UpdateInventoryItemRequest(
                **update_inventory_item_request
            ),
        ),
    )
    return InventoryItemModel(**result) if isinstance(result, dict) else InventoryItemModel.model_validate({})


async def delete_own_inventory_item(client: ApiClient, item_id: str) -> bool:
    """删除用户库存物品

    Args:
        client: ApiClient 实例
        item_id: 物品 ID

    Returns:
        是否删除成功
    """
    api = InventoryApi(client)
    await run_sync(api.delete_own_inventory_item)(inventory_item_id=item_id)
    return True


async def equip_own_inventory_item(
    client: ApiClient,
    item_id: str,
    equip_inventory_item_request: dict,
) -> bool:
    """装备用户库存物品

    Args:
        client: ApiClient 实例
        item_id: 物品 ID
        equip_inventory_item_request: 装备请求对象

    Returns:
        是否装备成功
    """
    from vrchatapi.models import EquipInventoryItemRequest

    api = InventoryApi(client)
    await run_sync(api.equip_own_inventory_item)(
        inventory_item_id=item_id,
        equip_inventory_item_request=EquipInventoryItemRequest(
            **equip_inventory_item_request
        ),
    )
    return True


async def unequip_own_inventory_slot(client: ApiClient, inventory_item_id: str) -> bool:
    """取消装备用户库存物品

    Args:
        client: ApiClient 实例
        inventory_item_id: 物品 ID

    Returns:
        是否取消成功
    """
    api = InventoryApi(client)
    await run_sync(api.unequip_own_inventory_slot)(inventory_item_id=inventory_item_id)
    return True


async def consume_own_inventory_item(
    client: ApiClient,
    item_id: str,
) -> dict:
    """消耗用户库存物品

    Args:
        client: ApiClient 实例
        item_id: 物品 ID

    Returns:
        消耗结果
    """
    api = InventoryApi(client)
    result = await cast(
        "Awaitable[dict]",
        run_sync(api.consume_own_inventory_item)(inventory_item_id=item_id),
    )
    return result if isinstance(result, dict) else {}


async def get_inventory_template(
    client: ApiClient,
    template_id: str,
) -> InventoryTemplateModel:
    """获取库存模板信息

    Args:
        client: ApiClient 实例
        template_id: 模板 ID

    Returns:
        模板信息
    """
    api = InventoryApi(client)
    result = await cast(
        "Awaitable[dict]",
        run_sync(api.get_inventory_template)(inventory_template_id=template_id),
    )
    return InventoryTemplateModel(**result) if isinstance(result, dict) else InventoryTemplateModel.model_validate({})


async def get_inventory_collections(
    client: ApiClient,
    n: int = 20,
    offset: int = 0,
) -> List[dict]:
    """获取库存集合列表

    Args:
        client: ApiClient 实例
        n: 返回数量
        offset: 偏移量

    Returns:
        集合列表
    """
    api = InventoryApi(client)
    result = await cast(
        "Awaitable[list]",
        run_sync(api.get_inventory_collections)(n=n, offset=offset),
    )
    return result if isinstance(result, list) else []


async def get_inventory_drops(
    client: ApiClient,
    n: int = 20,
    offset: int = 0,
) -> List[dict]:
    """获取库存掉落列表

    Args:
        client: ApiClient 实例
        n: 返回数量
        offset: 偏移量

    Returns:
        掉落列表
    """
    api = InventoryApi(client)
    result = await cast(
        "Awaitable[list]",
        run_sync(api.get_inventory_drops)(n=n, offset=offset),
    )
    return result if isinstance(result, list) else []
