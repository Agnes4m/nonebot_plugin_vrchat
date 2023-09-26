from typing import Dict, Optional

from pydantic import BaseModel


class UsrMsg(BaseModel):
    """用户储存信息"""

    username: str
    """用户名"""
    password: str
    """密码"""
    cookie: Optional[str] = None
    """饼干"""

    def to_dict(self) -> Dict[str, str]:
        return {
            "username": self.username,
            "password": self.password,
            "cookie": self.cookie,
        }
