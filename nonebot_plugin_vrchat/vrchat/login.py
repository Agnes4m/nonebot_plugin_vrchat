from typing import Awaitable, Callable, cast

from nonebot.utils import run_sync
from vrchatapi import AuthenticationApi
from vrchatapi.exceptions import ApiException, UnauthorizedException
from vrchatapi.models.current_user import CurrentUser
from vrchatapi.models.two_factor_auth_code import TwoFactorAuthCode
from vrchatapi.models.two_factor_email_code import TwoFactorEmailCode

from .client import PLAYER_PATH, LoginInfo, get_client, save_client_cookies


class TwoFactorAuthError(Exception):
    def __init__(self, verify_func: Callable[[str], Awaitable[CurrentUser]]) -> None:
        super().__init__()
        self.verify_func = verify_func


async def login_via_password(
    session_id: str,
    username: str,
    password: str,
) -> CurrentUser:
    client = get_client(
        session_id=session_id,
        login_info=LoginInfo(username=username, password=password),
    )
    api = AuthenticationApi(client)

    def save_user_info():
        info_path = PLAYER_PATH / f"{session_id}.json"
        info_path.write_text(
            LoginInfo(username=username, password=password).json(),
            encoding="utf-8",
        )
        save_client_cookies(client, session_id)

    try:
        # Calling getCurrentUser on Authentication API logs you in if the user isn't already logged in.
        current_user = await cast(
            Awaitable[CurrentUser],
            run_sync(api.get_current_user)(),
        )

    except UnauthorizedException as e:
        if e.status != 200:
            exc = ApiException(e.status, e.reason)
            exc.body = e.body
            exc.headers = e.headers
            raise exc from e

        if not isinstance(e.reason, str):
            raise TypeError(f"Unknown Reason: {e.reason}") from e

        if "Email 2 Factor Authentication" in e.reason:
            two_fa_email = True
        elif "2 Factor Authentication" in e.reason:
            two_fa_email = False
        else:
            raise TypeError(f"Unknown Reason: {e.reason}") from e

        async def verify_two_fa(auth_code: str) -> CurrentUser:
            if two_fa_email:
                # Calling email verify2fa if the account has 2FA disabled
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
