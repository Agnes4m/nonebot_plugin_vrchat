from pydantic import BaseModel


class ErrorMsg(BaseModel):
    Log: str = "尚未登录，或登录信息失效，请私聊并发送【vrc登录】来重新登录"
