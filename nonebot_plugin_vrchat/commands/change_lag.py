from nonebot import on_command
from nonebot.adapters import Message
from nonebot.matcher import Matcher
from nonebot.params import EventMessage

from ..config import session_config
from ..i18n import UserLocale, loaded_locales
from .utils import UserSessionId, rule_enable

change_locale = on_command(
    "vrccl",
    aliases={"vrc切换语言"},
    rule=rule_enable,
    priority=20,
)


@change_locale.handle()
async def _(matcher: Matcher, i18n: UserLocale):
    locales = "\n".join(
        f"{i}. {v.metadata.name} ({k})"
        for i, (k, v) in enumerate(loaded_locales.items(), 1)
    )
    await matcher.pause(
        f"{i18n.locale.available_locales_tip}\n"
        f"{locales}\n"
        f"{i18n.locale.select_locale_tip}",
    )


@change_locale.handle()
async def _(
    matcher: Matcher,
    session_id: UserSessionId,
    i18n: UserLocale,
    message: Message = EventMessage(),
):
    arg = message.extract_plain_text().strip()
    if not arg:
        await matcher.reject(i18n.general.empty_message)

    if arg == "0":
        await matcher.finish(i18n.general.discard_select)

    if not arg.isdigit():
        await matcher.reject(i18n.general.invalid_ordinal_format)

    index = int(arg) - 1
    if not (0 <= index < len(loaded_locales)):
        await matcher.reject(i18n.general.invalid_ordinal_range)

    name, i18n = list(loaded_locales.items())[index]
    config = session_config.get(session_id)[0].copy(update={"locale": name})
    session_config[session_id] = config

    await matcher.finish(
        i18n.locale.locale_changed.format(
            i18n.metadata.name,
            name,
            i18n.metadata.author,
        ),
    )
    name, i18n = list(loaded_locales.items())[index]
    config = session_config.get(session_id)[0].model_copy(update={"locale": name})
    session_config[session_id] = config

    await matcher.finish(
        i18n.locale.locale_changed.format(
            i18n.metadata.name,
            name,
            i18n.metadata.author,
        ),
    )
