# import asyncio
import ujson as json
import vrchatapi
from nonebot.log import logger

# from vrchatapi import Configuration
from vrchatapi.api import authentication_api
from vrchatapi.configuration import Configuration
from vrchatapi.exceptions import UnauthorizedException
from vrchatapi.models.current_user import CurrentUser
from vrchatapi.models.two_factor_auth_code import TwoFactorAuthCode
from vrchatapi.models.two_factor_email_code import TwoFactorEmailCode

from .classes import UsrMsg
from .config import config

# from .classes import TwoFactorAuthException
# from .config import config
from .vrchat.cookies import load_cookies, remove_cookies, save_cookies

# from pathlib import Path


class TwoFactorAuthException(Exception):  # noqa: N818
    pass


def login_vrc(
    api_client: vrchatapi.ApiClient,
    usr_id: str,
    username: str,
    password: str,
    code: str,
):
    """
    使用账户密码登录vrc,如果有cookies则使用
    """
    # configuration = vrchatapi.Configuration(
    #     username=username,
    #     password=password,
    # )
    # api_client = vrchatapi.ApiClient(configuration)
    # api_client.user_agent = "VRC-Notify/0.1.0 woolensheep@qq.com"

    load_cookies(api_client, filename=usr_id)
    # Instantiate instances of API classes
    auth_api = authentication_api.AuthenticationApi(api_client)

    try:
        # Calling getCurrentUser on Authentication API logs you in if the user isn't already logged in.
        current_user = auth_api.get_current_user()  # type: ignore
    except UnauthorizedException as e:
        if e.status == 200:
            if code == "":
                raise TwoFactorAuthException  # noqa: B904
            assert isinstance(e.reason, str)
            if "Email 2 Factor Authentication" in e.reason:
                # Calling email verify2fa if the account has 2FA disabled
                auth_api.verify2_fa_email_code(
                    two_factor_email_code=TwoFactorEmailCode(code),
                )
            elif "2 Factor Authentication" in e.reason:
                # Calling verify2fa if the account has 2FA enabled
                auth_api.verify2_fa(two_factor_auth_code=TwoFactorAuthCode(code))
            current_user: CurrentUser = auth_api.get_current_user()  # type: ignore
            save_cookies(api_client, "./cookies.txt")

            # assert isinstance(current_user, vrchatapi.CurrentUser)
            # logger.info(f"Logged in as: {current_user.display_name}")
            # cookie = save_cookies(api_client, filename=usr_id)
            # if cookie is not None:
            #     with config.vrc_path.joinpath(f"{usr_id}.json").open(
            #         mode="w", encoding="utf-8"
            #     ) as f:
            #         json.dump(
            #             UsrMsg(
            #                 username=username, password=password, cookie=cookie
            #             ).to_dict(),
            #             f,
            #             ensure_ascii=False,
            #         )
            #     return cookie
        else:
            remove_cookies(filename=usr_id)
            logger.info(f"Exception when calling API: {e}")
            return None
    except vrchatapi.ApiException as e:
        remove_cookies(filename=usr_id)
        logger.info(f"Exception when calling API: {e}")
        return None
    except Exception as e:
        remove_cookies(filename=usr_id)
        logger.info(f"Exception when login: {e}")
        return None

    msg = vars(current_user)
    configuration: Configuration = current_user.local_vars_configuration
    msg["local_vars_configuration"] = configuration.__dict__
    print(str(msg))
    msg_dict = UsrMsg(username=username, password=password).to_dict()
    print(msg_dict)
    with config.vrc_path.joinpath(f"player/{usr_id}.json").open(
        mode="w",
        encoding="utf-8",
    ) as f:
        json.dump(msg_dict, f, ensure_ascii=False, indent=4)
    return current_user.display_name


async def login_in(
    usr_id: str,
    username: str,
    password: str,
    code: str = "",
):
    configuration = vrchatapi.Configuration(
        username=username,
        password=password,
    )
    api_client = vrchatapi.ApiClient(configuration)
    api_client.user_agent = "VRC-Notify/0.1.0 woolensheep@qq.com"

    load_cookies(api_client, "./cookies.txt")
    try:
        login_vrc(api_client, usr_id, username, password, code)
    except TwoFactorAuthException:
        # await matcher.send("Resend `/login` command with verify code (or 2FA code)")
        print("Resend `/login` command with verify code (or 2FA code)")
        msg: str = "verify code (or 2FA code)"
        return 401, msg
    except Exception as e:
        # await matcher.send(f"Login failed with error: {e}")
        print(f"Login failed with error: {e}")
        return 500, str(e)
    auth_api = authentication_api.AuthenticationApi(api_client)
    current_user: CurrentUser = auth_api.get_current_user()  # type: ignore
    save_cookies(api_client, "./cookies.txt")

    name: str = current_user.display_name if current_user.display_name else ""
    # await matcher.send(f"Logged in as {name}")
    print(f"Logged in as {name}")
    # with config.vrc_path.joinpath(f"{usr_id}.json").open(
    #     mode="w",
    #     encoding="utf-8",
    # ) as f:
    #     json.dump(
    #         UsrMsg(username=username, password=password, cookie=cookie).to_dict(),
    #         f,
    #         ensure_ascii=False,
    #         indent=4,
    #     )
    return 200, name


if __name__ == "__main__":
    ...
