import time

from loguru import logger
from nonebot import on_command
from nonebot.matcher import Matcher

from ..i18n import Lang
from ..vrchat import (
    get_balance,
    get_balance_earnings,
    get_client,
    get_current_subscriptions,
    get_current_user_id,
    get_economy_account,
    get_subscriptions,
    get_tilia_status,
)
from .utils import (
    UserSessionId,
    handle_error,
    rule_enable,
)

# region 余额查询
balance_cmd = on_command(
    "vrcbalance",
    aliases={"vrc余额", "vrc我的余额"},
    rule=rule_enable,
    priority=20,
)


@balance_cmd.handle()
async def _(matcher: Matcher, session_id: UserSessionId):
    start_time = time.perf_counter()
    logger.info("正在查询当前用户余额信息")
    try:
        client = await get_client(session_id)
        user_id = await get_current_user_id(client)
        balance = await get_balance(client, user_id)
        earnings = await get_balance_earnings(client, user_id)
    except Exception as e:
        await handle_error(matcher, e)

    end_time = time.perf_counter()
    logger.debug(f"余额查询执行用时：{end_time - start_time:.3f} 秒")

    msg = Lang.nbp_vrc.economy.balance_info(
        balance=balance.balance,
        pending=balance.pending,
        last_payout=balance.last_payout,
        earnings=earnings,
    )
    await matcher.finish(msg)


# region 经济账户查询
economy_account_cmd = on_command(
    "vrceconomy",
    aliases={"vrc账户"},
    rule=rule_enable,
    priority=20,
)


@economy_account_cmd.handle()
async def _(matcher: Matcher, session_id: UserSessionId):
    logger.info("正在查询当前用户账户信息")
    try:
        client = await get_client(session_id)
        user_id = await get_current_user_id(client)
        account = await get_economy_account(client, user_id)
    except Exception as e:
        await handle_error(matcher, e)

    msg = Lang.nbp_vrc.economy.account_info(
        account_id=account.get("id", ""),
        status=account.get("status", ""),
        created_at=account.get("created_at"),
        updated_at=account.get("updated_at"),
    )
    await matcher.finish(msg)


# region 订阅查询
subscriptions_cmd = on_command(
    "vrcsubs",
    aliases={"vrc订阅", "vrc我的订阅"},
    rule=rule_enable,
    priority=20,
)


@subscriptions_cmd.handle()
async def _(matcher: Matcher, session_id: UserSessionId):
    logger.info("正在查询当前订阅信息")
    try:
        client = await get_client(session_id)
        current_subs = await get_current_subscriptions(client)
        all_subs = await get_subscriptions(client)
    except Exception as e:
        await handle_error(matcher, e)

    msg = Lang.nbp_vrc.economy.subscriptions_info(
        current_count=len(current_subs.get("subscriptions", []))
        if isinstance(current_subs, dict)
        else 0,
        total_count=len(all_subs) if isinstance(all_subs, list) else 0,
        subscriptions=all_subs if isinstance(all_subs, list) else [],
    )
    await matcher.finish(msg)


# region Tilia 状态查询
tilia_status_cmd = on_command(
    "vrctilia",
    aliases={"vrctilia", "vrctilia状态"},
    rule=rule_enable,
    priority=20,
)


@tilia_status_cmd.handle()
async def _(matcher: Matcher, session_id: UserSessionId):
    logger.info("正在查询 Tilia 状态")
    try:
        client = await get_client(session_id)
        status = await get_tilia_status(client)
    except Exception as e:
        await handle_error(matcher, e)

    msg = Lang.nbp_vrc.economy.tilia_status_info(
        user_id=status.get("user_id", ""),
        status=status.get("status", ""),
        created_at=status.get("created_at"),
        updated_at=status.get("updated_at"),
    )
    await matcher.finish(msg)


# region 收益查询
earnings_cmd = on_command(
    "vrcearnings",
    aliases={"vrcsy", "vrc收益", "vrc我的收益"},
    rule=rule_enable,
    priority=20,
)


@earnings_cmd.handle()
async def _(matcher: Matcher, session_id: UserSessionId):
    logger.info("正在查询当前用户收益信息")
    try:
        client = await get_client(session_id)
        user_id = await get_current_user_id(client)
        earnings = await get_balance_earnings(client, user_id)
    except Exception as e:
        await handle_error(matcher, e)
    balance = earnings.get("balance", "0")
    no_transactions = earnings.get("no_transactions")
    tilia_response = earnings.get("tilia_response")
    if no_transactions is None:
        msg = Lang.nbp_vrc.economy.no_earnings_info()
    else:
        msg = Lang.nbp_vrc.economy.earnings_info(
            balance=balance,
            no_transactions=no_transactions,
            tilia_response=tilia_response,
        )
    await matcher.finish(msg)


# region 帮助信息
economy_help = on_command(
    "vrceconomyhelp",
    aliases={"vrc经济帮助"},
    rule=rule_enable,
    priority=20,
)


@economy_help.handle()
async def _(matcher: Matcher):
    msg = Lang.nbp_vrc.economy.help()
    await matcher.finish(msg)
