from typing import Awaitable, List, cast

from nonebot.utils import run_sync
from vrchatapi import ApiClient, AuthenticationApi, EconomyApi

from .types import BalanceModel


async def get_current_user_id(client: ApiClient) -> str:
    """获取当前登录用户的 ID"""
    api = AuthenticationApi(client)
    current_user = await cast(
        "Awaitable[object]",
        run_sync(api.get_current_user)(),
    )
    if hasattr(current_user, "to_dict"):
        return current_user.to_dict().get("id", "")
    if hasattr(current_user, "id"):
        return current_user.id
    return ""


async def get_balance(client: ApiClient, user_id: str) -> BalanceModel:
    """获取用户余额信息"""
    api = EconomyApi(client)
    result = await cast(
        "Awaitable[object]",
        run_sync(api.get_balance)(user_id=user_id),
    )
    if hasattr(result, "to_dict"):
        data = result.to_dict()
        return BalanceModel(
            balance=data.get("balance", 0),
            pending=data.get("noTransactions", 0),
            last_payout=data.get("lastPayout"),
        )
    return BalanceModel()


async def get_balance_earnings(client: ApiClient, user_id: str) -> dict:
    """获取用户收益信息"""
    api = EconomyApi(client)
    result = await cast(
        "Awaitable[object]",
        run_sync(api.get_balance_earnings)(user_id=user_id),
    )
    return result.to_dict() if hasattr(result, "to_dict") else {}


async def get_economy_account(client: ApiClient, user_id: str) -> dict:
    """获取经济账户信息"""
    api = EconomyApi(client)
    result = await cast(
        "Awaitable[object]",
        run_sync(api.get_economy_account)(user_id=user_id),
    )
    return result.to_dict() if hasattr(result, "to_dict") else {}


async def get_active_licenses(
    client: ApiClient,
    n: int = 50,
    offset: int = 0,
) -> List[dict]:
    """获取活跃许可证列表"""
    api = EconomyApi(client)
    result = await cast(
        "Awaitable[list]",
        run_sync(api.get_active_licenses)(n=n, offset=offset),
    )
    return (
        [item.to_dict() if hasattr(item, "to_dict") else item for item in result]
        if isinstance(result, list)
        else []
    )


async def get_license_group(client: ApiClient, license_group_id: str) -> dict:
    """获取许可证组信息"""
    api = EconomyApi(client)
    result = await cast(
        "Awaitable[object]",
        run_sync(api.get_license_group)(license_group_id=license_group_id),
    )
    return result.to_dict() if hasattr(result, "to_dict") else {}


async def get_product_listing(
    client: ApiClient,
    product_listing_id: str,
) -> dict:
    """获取商品列表信息"""
    api = EconomyApi(client)
    result = await cast(
        "Awaitable[object]",
        run_sync(api.get_product_listing)(product_id=product_listing_id),
    )
    return result.to_dict() if hasattr(result, "to_dict") else {}


async def get_product_listings(
    client: ApiClient,
    user_id: str,
    product_listing_type: str = "direct",
    n: int = 20,
    offset: int = 0,
) -> List[dict]:
    """获取商品列表"""
    api = EconomyApi(client)
    result = await cast(
        "Awaitable[list]",
        run_sync(api.get_product_listings)(
            user_id=user_id,
            type=product_listing_type,
            n=n,
            offset=offset,
        ),
    )
    return (
        [item.to_dict() if hasattr(item, "to_dict") else item for item in result]
        if isinstance(result, list)
        else []
    )


async def get_store(client: ApiClient, store_id: str) -> dict:
    """获取商店信息"""
    api = EconomyApi(client)
    result = await cast(
        "Awaitable[object]",
        run_sync(api.get_store)(store_id=store_id),
    )
    return result.to_dict() if hasattr(result, "to_dict") else {}


async def get_store_shelves(client: ApiClient, store_id: str) -> List[dict]:
    """获取商店货架列表"""
    api = EconomyApi(client)
    result = await cast(
        "Awaitable[list]",
        run_sync(api.get_store_shelves)(store_id=store_id),
    )
    return (
        [item.to_dict() if hasattr(item, "to_dict") else item for item in result]
        if isinstance(result, list)
        else []
    )


async def get_current_subscriptions(client: ApiClient) -> dict:
    """获取当前订阅信息"""
    api = EconomyApi(client)
    result = await cast(
        "Awaitable[object]",
        run_sync(api.get_current_subscriptions)(),
    )
    return result.to_dict() if hasattr(result, "to_dict") else {}


async def get_subscriptions(client: ApiClient, user_id: str) -> List[dict]:
    """获取用户全部订阅历史"""
    api = EconomyApi(client)
    result = await cast(
        "Awaitable[list]",
        run_sync(api.get_subscriptions)(user_id=user_id),
    )
    return (
        [item.to_dict() if hasattr(item, "to_dict") else item for item in result]
        if isinstance(result, list)
        else []
    )


async def get_tilia_status(client: ApiClient) -> dict:
    """获取 Tilia 状态信息"""
    api = EconomyApi(client)
    result = await cast(
        "Awaitable[object]",
        run_sync(api.get_tilia_status)(),
    )
    return result.to_dict() if hasattr(result, "to_dict") else {}


async def get_tilia_tos(client: ApiClient, user_id: str) -> dict:
    """获取 Tilia 服务条款"""
    api = EconomyApi(client)
    result = await cast(
        "Awaitable[object]",
        run_sync(api.get_tilia_tos)(user_id=user_id),
    )
    return result.to_dict() if hasattr(result, "to_dict") else {}


async def get_token_bundles(client: ApiClient) -> List[dict]:
    """获取代币包信息"""
    api = EconomyApi(client)
    result = await cast(
        "Awaitable[list]",
        run_sync(api.get_token_bundles)(),
    )
    return (
        [item.to_dict() if hasattr(item, "to_dict") else item for item in result]
        if isinstance(result, list)
        else []
    )


async def get_user_credits_eligible(
    client: ApiClient,
    user_id: str,
    subscription_id: str,
) -> dict:
    """获取用户信用额度资格信息"""
    api = EconomyApi(client)
    result = await cast(
        "Awaitable[object]",
        run_sync(api.get_user_credits_eligible)(
            user_id=user_id,
            subscription_id=subscription_id,
        ),
    )
    return result.to_dict() if hasattr(result, "to_dict") else {}


async def get_user_subscription_eligible(client: ApiClient, user_id: str) -> dict:
    """获取用户订阅资格信息"""
    api = EconomyApi(client)
    result = await cast(
        "Awaitable[object]",
        run_sync(api.get_user_subscription_eligible)(user_id=user_id),
    )
    return result.to_dict() if hasattr(result, "to_dict") else {}
