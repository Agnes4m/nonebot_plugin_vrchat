from typing import Awaitable, List, cast

from nonebot.utils import run_sync
from vrchatapi import ApiClient, EconomyApi

from .types import BalanceModel


async def get_balance(client: ApiClient, user_id: str) -> BalanceModel:
    """获取用户余额信息

    Args:
        client: ApiClient 实例

    Returns:
        余额信息
    """
    api = EconomyApi(client)
    result = await cast(
        "Awaitable[dict]",
        run_sync(api.get_balance)(user_id=user_id),
    )
    return BalanceModel(**result.to_dict())


async def get_balance_earnings(client: ApiClient, user_id: str) -> dict:
    """获取用户收益信息

    Args:
        client: ApiClient 实例

    Returns:
        收益信息
    """
    api = EconomyApi(client)
    result = await cast(
        "Awaitable[dict]",
        run_sync(api.get_balance_earnings)(user_id=user_id),
    )
    return result.to_dict() if result else {}


async def get_economy_account(client: ApiClient, user_id: str) -> dict:
    """获取经济账户信息

    Args:
        client: ApiClient 实例

    Returns:
        经济账户信息
    """
    api = EconomyApi(client)
    result = await cast(
        "Awaitable[dict]",
        run_sync(api.get_economy_account)(user_id=user_id),
    )
    return result if result else {}


async def get_active_licenses(
    client: ApiClient,
    n: int = 50,
    offset: int = 0,
) -> List[dict]:
    """获取活跃许可证列表

    Args:
        client: ApiClient 实例
        n: 返回数量
        offset: 偏移量

    Returns:
        许可证列表
    """
    api = EconomyApi(client)
    result = await cast(
        "Awaitable[list]",
        run_sync(api.get_active_licenses)(n=n, offset=offset),
    )
    return result if isinstance(result, list) else []


async def get_license_group(client: ApiClient, license_group_id: str) -> dict:
    """获取许可证组信息

    Args:
        client: ApiClient 实例
        license_group_id: 许可证组 ID

    Returns:
        许可证组信息
    """
    api = EconomyApi(client)
    result = await cast(
        "Awaitable[dict]",
        run_sync(api.get_license_group)(license_group_id=license_group_id),
    )
    return result if isinstance(result, dict) else {}


async def get_product_listing(
    client: ApiClient,
    product_listing_id: str,
) -> dict:
    """获取商品列表信息

    Args:
        client: ApiClient 实例
        product_listing_id: 商品列表 ID

    Returns:
        商品列表信息
    """
    api = EconomyApi(client)
    result = await cast(
        "Awaitable[dict]",
        run_sync(api.get_product_listing)(product_id=product_listing_id),
    )
    return result if isinstance(result, dict) else {}


async def get_product_listings(
    client: ApiClient,
    user_id: str,
    product_listing_type: str = "direct",
    n: int = 20,
    offset: int = 0,
) -> List[dict]:
    """获取商品列表

    Args:
        user_id: 用户 ID
        client: ApiClient 实例
        product_listing_type: 商品类型
        n: 返回数量
        offset: 偏移量

    Returns:
        商品列表
    """
    api = EconomyApi(client)
    result = await cast(
        "Awaitable[list]",
        run_sync(api.get_product_listings)(user_id=user_id,type=product_listing_type, n=n, offset=offset),
    )
    return result if isinstance(result, list) else []


async def get_store(client: ApiClient, store_id: str) -> dict:
    """获取商店信息

    Args:
        client: ApiClient 实例
        store_id: 商店 ID

    Returns:
        商店信息
    """
    api = EconomyApi(client)
    result = await cast(
        "Awaitable[dict]",
        run_sync(api.get_store)(store_id=store_id),
    )
    return result if isinstance(result, dict) else {}


async def get_store_shelves(client: ApiClient, store_id: str) -> List[dict]:
    """获取商店货架列表

    Args:
        client: ApiClient 实例
        store_id: 商店 ID

    Returns:
        货架列表
    """
    api = EconomyApi(client)
    result = await cast(
        "Awaitable[list]",
        run_sync(api.get_store_shelves)(store_id=store_id),
    )
    return result if isinstance(result, list) else []


async def get_current_subscriptions(client: ApiClient) -> dict:
    """获取当前订阅信息

    Args:
        client: ApiClient 实例

    Returns:
        订阅信息
    """
    api = EconomyApi(client)
    result = await cast(
        "Awaitable[dict]",
        run_sync(api.get_current_subscriptions)(),
    )
    return result if isinstance(result, dict) else {}


async def get_subscriptions(
    client: ApiClient,
    n: int = 20,
    offset: int = 0,
) -> List[dict]:
    """获取订阅列表

    Args:
        client: ApiClient 实例
        n: 返回数量
        offset: 偏移量

    Returns:
        订阅列表
    """
    api = EconomyApi(client)
    result = await cast(
        "Awaitable[list]",
        run_sync(api.get_subscriptions)(n=n, offset=offset),
    )
    return result if isinstance(result, list) else []


async def get_tilia_status(client: ApiClient) -> dict:
    """获取 Tilia 状态信息

    Args:
        client: ApiClient 实例

    Returns:
        Tilia 状态信息
    """
    api = EconomyApi(client)
    result = await cast(
        "Awaitable[dict]",
        run_sync(api.get_tilia_status)(),
    )
    return result if isinstance(result, dict) else {}


async def get_tilia_tos(client: ApiClient, user_id: str) -> dict:
    """获取 Tilia 服务条款

    Args:
        user_id: 用户 ID
        client: ApiClient 实例

    Returns:
        服务条款信息
    """
    api = EconomyApi(client)
    result = await cast(
        "Awaitable[dict]",
        run_sync(api.get_tilia_tos)(user_id=user_id),
    )
    return result if isinstance(result, dict) else {}


async def get_token_bundles(client: ApiClient) -> List[dict]:
    """获取代币包信息

    Args:
        client: ApiClient 实例

    Returns:
        代币包信息
    """
    api = EconomyApi(client)
    result = await cast(
        "Awaitable[list]",
        run_sync(api.get_token_bundles)(),
    )
    return result if isinstance(result, list) else []


async def get_user_credits_eligible(client: ApiClient, user_id: str, subscription_id:str) -> dict:
    """获取用户信用额度资格信息

    Args:
        user_id: 用户 ID
        client: ApiClient 实例

    Returns:
        资格信息
    """
    api = EconomyApi(client)
    result = await cast(
        "Awaitable[dict]",
        run_sync(api.get_user_credits_eligible)(user_id=user_id, subscription_id=subscription_id),
    )
    return result if isinstance(result, dict) else {}


async def get_user_subscription_eligible(client: ApiClient, user_id: str) -> dict:
    """获取用户订阅资格信息

    Args:
        user_id: 用户 ID
        client: ApiClient 实例

    Returns:
        资格信息
    """
    api = EconomyApi(client)
    result = await cast(
        "Awaitable[dict]",
        run_sync(api.get_user_subscription_eligible)(user_id=user_id),
    )
    return result if isinstance(result, dict) else {}
