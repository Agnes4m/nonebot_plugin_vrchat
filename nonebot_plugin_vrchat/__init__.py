from nonebot import require
from nonebot.plugin import PluginMetadata, inherit_supported_adapters

require("nonebot_plugin_session")
require("nonebot_plugin_saa")

from . import __main__ as __main__  # noqa: E402
from .config import ConfigModel  # noqa: E402

__version__ = "0.1.0"
__plugin_meta__ = PluginMetadata(
    name="VRChat查询",
    description="使用第三方 API SDK 实现 VRChat 相关操作，例如查询好友状态",
    usage="使用【vrc帮助】指令获取帮助",
    type="application",
    homepage="https://github.com/Agnes4m/nonebot_plugin_vrchat",
    config=ConfigModel,
    supported_adapters=inherit_supported_adapters("nonebot_plugin_saa"),
    extra={
        "version": __version__,
        "author": ["Agnes4m <Z735803792@163.com>", "student_2333 <lgc2333@126.com>"],
    },
)
