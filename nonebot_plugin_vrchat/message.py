from pydantic import BaseModel


class Error(BaseModel):
    Log: str = "尚未登录，或登录信息失效，请私聊并发送【vrc登录】来重新登录"
    Unauth: str = "登录已过期，请重新登录"
    Unkown: str = "遇到未知错误，请检查后台输出"
    login: str = "用户名或密码错误，请重新发送"
    Format2FA: str = "验证码格式不正确"
    Error2FA: str = "验证码错误，请重新发送"


class Info(BaseModel):
    Relogin: str = "检测到缓存的登录信息，尝试重新登录"
    Dislogin: str = "已取消登录"
    NoFriend: str = "当前没有好友捏"
    NoUser: str = "没搜到任何玩家捏"
    Deselect: str = "已取消选择"


class Send(BaseModel):
    Sendlgoin: str = "请发送登录账号密码，用空格分隔，发送 0 取消登录\n提示：机器人会保存你的登录状态,请在信任机器人的情况下登录"
    User: str = "请发送要查询的玩家名称"
    SearchNone: str = "搜索关键词不能为空，请重新发送"
    OrdinalFormat: str = "序号格式不正确，请重新发送"
    OrdinalRange: str = "序号不在范围内，请重新发送"
    Map: str = "请发送要查询的地图名称"
    NoMap: str = "没搜到任何地图捏"


class Warnin(BaseModel):
    Resendlgoin: str = "消息格式不符合规范，请重新发送账号密码，用空格分隔"
    Overwrite: str = "检测到已缓存的登录信息，本次登录成功后旧登录信息将被覆盖"


ErrorMsg = Error()
InfoMsg = Info()
SendMsg = Send()
WarningMsg = Warnin()
