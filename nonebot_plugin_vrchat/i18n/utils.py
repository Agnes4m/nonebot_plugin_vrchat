from nonebot_plugin_session import SessionId, SessionIdType
from typing_extensions import Annotated

UserSessionId = Annotated[str, SessionId(SessionIdType.USER, include_bot_id=False)]
GroupSessionId = Annotated[str, SessionId(SessionIdType.GROUP, include_bot_id=False)]
