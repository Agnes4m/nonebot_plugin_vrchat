from nonebot import on_command
from nonebot.matcher import Matcher

from ..i18n import UserLocale
from .utils import rule_enable

vrc_help = on_command(
    "vrchelp",
    aliases={"vrc帮助"},
    rule=rule_enable,
    priority=20,
)


@vrc_help.handle()
async def _(matcher: Matcher, i18n: UserLocale):
    await matcher.finish(i18n.general.help)
