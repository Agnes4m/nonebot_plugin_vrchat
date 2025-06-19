from typing import TypedDict


class ErrorType(TypedDict):
    """错误类型"""

    status_code: str
    message: str


class ErrorResponse(TypedDict):
    """错误类型"""

    error: ErrorType
