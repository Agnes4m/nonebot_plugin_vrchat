from nonebot import require
from nonebot.plugin import PluginMetadata, inherit_supported_adapters

require("nonebot_plugin_session")
require("nonebot_plugin_alconna")

from .commands import load_commands
from .config import EnvConfig

load_commands()


__version__ = "0.2.0"
__plugin_meta__ = PluginMetadata(
    name="VRChat查询",
    description="使用第三方 API SDK 实现 VRChat 相关操作，例如查询好友状态",
    usage="使用【vrc帮助】指令获取帮助",
    type="application",
    homepage="https://github.com/Agnes4m/nonebot_plugin_vrchat",
    config=EnvConfig,
    supported_adapters=inherit_supported_adapters("nonebot_plugin_alconna"),
    extra={
        "version": __version__,
        "author": ["Agnes4m <Z735803792@163.com>", "student_2333 <lgc2333@126.com>"],
    },
)
