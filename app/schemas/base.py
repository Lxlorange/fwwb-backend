from typing import TypeVar, Generic, Any
from pydantic import BaseModel, Field

T = TypeVar("T")

class ResponseModel(BaseModel, Generic[T]):
    """
    统一的泛型 API 响应封装格式
    """
    code: int = Field(default=200, description="状态码，200代表成功")
    message: str = Field(default="success", description="状态信息")
    data: T | None = Field(default=None, description="业务数据载荷")

    @classmethod
    def success(cls, data: T | None = None, message: str = "success") -> "ResponseModel[T]":
        return cls(code=200, message=message, data=data)

    @classmethod
    def error(cls, code: int = 500, message: str = "服务器内部错误") -> "ResponseModel[Any]":
        return cls(code=code, message=message, data=None)
