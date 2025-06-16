from typing_extensions import Annotated

from nonebot_plugin_session import SessionId, SessionIdType

UserSessionId = Annotated[str, SessionId(SessionIdType.USER, include_bot_id=False)]
GroupSessionId = Annotated[str, SessionId(SessionIdType.GROUP, include_bot_id=False)]
