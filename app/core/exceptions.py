from fastapi import Request
from fastapi.responses import JSONResponse
from app.schemas.base import ResponseModel

async def global_exception_handler(request: Request, exc: Exception):
    """
    统一的全局未捕获异常处理，避免向前端暴露服务端崩溃的堆栈细节，返回标准JSON结构
    """
    content = ResponseModel.error(code=500, message=f"Internal Server Error: {str(exc)}").model_dump()
    return JSONResponse(status_code=500, content=content)
