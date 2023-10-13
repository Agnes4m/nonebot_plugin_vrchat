from typing import Awaitable, Callable, cast

from nonebot.utils import run_sync
from vrchatapi import AuthenticationApi
from vrchatapi.exceptions import ApiException, UnauthorizedException
from vrchatapi.models.current_user import CurrentUser
from vrchatapi.models.two_factor_auth_code import TwoFactorAuthCode
from vrchatapi.models.two_factor_email_code import TwoFactorEmailCode

from .client import PLAYER_PATH, LoginInfo, get_client, save_client_cookies


# 定义一个自定义异常类TwoFactorAuthError，继承自Exception
class TwoFactorAuthError(Exception):
    # 定义异常类的初始化方法
    def __init__(self, verify_func: Callable[[str], Awaitable[CurrentUser]]) -> None:
        # 调用父类的初始化方法
        super().__init__()
        # 保存传入的verify_func参数，它是一个函数，接受一个字符串参数，返回一个Awaitable[CurrentUser]类型的对象
        self.verify_func = verify_func


# 定义一个异步函数login_via_password，用于通过用户名和密码登录
async def login_via_password(
    # 登录的会话ID
    session_id: str,
    # 用户名
    username: str,
    # 密码
    password: str,
) -> CurrentUser:
    client = await get_client(
        session_id=session_id,
        login_info=LoginInfo(username=username, password=password),
    )
    # 创建一个AuthenticationApi对象，使用上面的client
    api = AuthenticationApi(client)

    # 定义一个函数，用于保存用户信息到文件和保存客户端的cookies
    def save_user_info():
        # 根据session_id创建一个保存用户信息的文件路径
        info_path = PLAYER_PATH / f"{session_id}.json"
        # 将用户信息（用户名和密码）以json格式写入到文件中，编码方式为utf-8
        info_path.write_text(
            LoginInfo(username=username, password=password).json(),
            encoding="utf-8",
        )
        # 保存客户端的cookies到相应的位置
        save_client_cookies(client, session_id)

    # 尝试调用Authentication API的getCurrentUser方法，如果用户未登录则会登录，并返回当前用户的信息
    try:
        # 使用cast函数将同步的api.get_current_user()方法转换为异步的，并调用它
        current_user = await cast(
            Awaitable[CurrentUser],
            run_sync(api.get_current_user)(),
        )

    # 如果出现UnauthorizedException异常（即未授权异常），进行相应的处理
    except UnauthorizedException as e:
        # 如果异常的状态码不是200，则抛出一个ApiException异常，该异常包含原始异常的信息
        if e.status != 200:
            exc = ApiException(e.status, e.reason)
            exc.body = e.body
            exc.headers = e.headers
            raise exc from e

        # 如果异常的原因不是字符串类型，则抛出一个TypeError异常
        if not isinstance(e.reason, str):
            raise TypeError(f"Unknown Reason: {e.reason}") from e

        # 如果异常原因为"Email 2 Factor Authentication"，则设置two_fa_email为True
        # 这意味着用户需要通过两步验证才能完成登录
        if "Email 2 Factor Authentication" in e.reason:
            two_fa_email = True
        # 如果异常原因为"2 Factor Authentication"，则设置two_fa_email为False
        # 这意味着用户已经通过了两个步骤的验证，不需要再进行验证了
        elif "2 Factor Authentication" in e.reason:
            two_fa_email = False
        # 如果异常原因为其他情况，则抛出一个TypeError异常
        else:
            raise TypeError(f"Unknown Reason: {e.reason}") from e

        # 定义一个异步函数verify_two_fa，该函数接受一个认证码作为参数，并返回当前用户的信息
        async def verify_two_fa(auth_code: str) -> CurrentUser:
            # 如果two_fa_email为True，则调用api的verify2_fa_email_code方法进行邮箱验证操作
            if two_fa_email:
                # email verify2fa method call if the account has 2FA disabled. The EmailCode object is created from the given auth code. 上面这行代码似乎有些问题，应该是“if the account has 2FA disabled”才对。本地的auth code应该是传入的。不然如果用户已经开启了2步验证。这个会出错。await run_sync(api.verify2fa email code)(two factor email code=)
                await run_sync(api.verify2_fa_email_code)(
                    two_factor_email_code=TwoFactorEmailCode(auth_code),
                )
            else:
                # Calling verify2fa if the account has 2FA enabled
                await run_sync(api.verify2_fa)(
                    two_factor_auth_code=TwoFactorAuthCode(auth_code),
                )

            current_user = await cast(
                Awaitable[CurrentUser],
                run_sync(api.get_current_user)(),
            )
            save_user_info()
            return current_user

        raise TwoFactorAuthError(verify_two_fa) from e

    save_user_info()
    return current_user


def remove_login_info(session_id: str):
    """这个函数没有定义，补全以防报错"""
    if session_id:
        ...
