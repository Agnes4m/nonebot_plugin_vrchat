from pathlib import Path
from typing import Dict
from typing_extensions import Annotated

from nonebot import logger
from nonebot.params import Depends

from ..config import plugin_config, session_config
from ..utils import GroupSessionId, UserSessionId, load_yaml
from .types import I18N as I18N
from .types import I18NFriend as I18NFriend
from .types import I18NGeneral as I18NGeneral
from .types import I18NLogin as I18NLogin
from .types import I18NMetadata as I18NMetadata
from .types import I18NUser as I18NUser
from .types import I18NWorld as I18NWorld

LOCALE_PATH = Path(__file__).parent / "locales"
FALLBACK_LOCALE = "zh-CN"

loaded_locales: Dict[str, I18N] = {}


def load_locales():
    logger.debug("Loading locales...")

    fallback_locale = I18N(**load_yaml(LOCALE_PATH / f"{FALLBACK_LOCALE}.yml"))
    loaded_locales[FALLBACK_LOCALE] = fallback_locale

    for locale_file in LOCALE_PATH.glob("*.yml"):
        try:
            locale = I18N(**load_yaml(locale_file))
        except Exception:
            logger.exception(f"Failed to load locale {locale_file.name}")
        else:
            loaded_locales[locale_file.stem] = locale
            logger.debug(
                f"Loaded locale {locale.metadata.name} ({locale_file.stem}) "
                f"by {locale.metadata.author}",
            )

    logger.debug(f"Loaded {len(loaded_locales)} locales")


async def get_locale(
    user_session: UserSessionId,
    group_session: GroupSessionId,
) -> I18N:
    config, session_id = session_config.get(user_session, group_session)
    if not config.locale:
        return loaded_locales[plugin_config.locale]

    if config.locale not in loaded_locales:
        logger.warning(
            f'Session {session_id} is using invalid locale "{config.locale}"',
        )
        return loaded_locales[plugin_config.locale]

    return loaded_locales[config.locale]


async def get_trans_by_key(key: str, session_id: str) -> str:
    tree = key.split(".")
    locale = await get_locale(session_id, session_id)

    value = locale
    try:
        for node in tree:
            value = getattr(value, node)
        assert isinstance(value, str)
    except Exception as e:
        raise AttributeError(f"Invalid i18n key: {key}") from e  # noqa: TRY004

    return value


load_locales()


UserLocale = Annotated[I18N, Depends(get_locale)]
