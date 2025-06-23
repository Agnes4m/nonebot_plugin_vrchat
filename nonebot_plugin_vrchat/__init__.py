from nonebot import require
from nonebot.plugin import PluginMetadata, inherit_supported_adapters

from .commands import load_commands

require("nonebot_plugin_session")
# require("nonebot_plugin_waiter")
require("nonebot_plugin_htmlrender")
require("nonebot_plugin_alconna")
from nonebot_plugin_alconna import load_builtin_plugin  # noqa: E402

from .config import EnvConfig  # noqa: E402

load_builtin_plugin("lang")
load_commands()

__version__ = "0.3.2"
__plugin_meta__ = PluginMetadata(
    name="VRChat查询",
    description="使用第三方 API SDK 实现 VRChat 相关操作，例如查询好友状态",
    usage="使用【vrc帮助】指令获取帮助",
    type="application",
    homepage="https://github.com/Agnes4m/nonebot_plugin_vrchat",
    config=EnvConfig,
    supported_adapters=inherit_supported_adapters(
        "nonebot_plugin_alconna",
        "nonebot_plugin_session",
    ),
    extra={
        "version": __version__,
        "author": ["Agnes4m <Z735803792@163.com>", "student_2333 <lgc2333@126.com>"],
    },
)
