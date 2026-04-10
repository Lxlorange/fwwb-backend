from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.exceptions import global_exception_handler
from app.api.v1 import cv_router, forecast_router, anomaly_router, workorder_router, data_router

def create_app() -> FastAPI:
    """系统入口工厂函数"""
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        description="面向海洋环境的智能分析与预警系统 Backend API"
    )

    # 注册全局异常处理
    app.add_exception_handler(Exception, global_exception_handler)

    # 配置 CORS 控制
    if settings.BACKEND_CORS_ORIGINS:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    # 注册路由模块 (API层的 Router)
    app.include_router(cv_router.router, prefix=f"{settings.API_V1_STR}/cv", tags=["海洋垃圾识别CV"])
    app.include_router(forecast_router.router, prefix=f"{settings.API_V1_STR}/forecast", tags=["生境预测"])
    app.include_router(anomaly_router.router, prefix=f"{settings.API_V1_STR}/anomaly", tags=["风浪预警"])
    app.include_router(workorder_router.router, prefix=f"{settings.API_V1_STR}/workorder", tags=["工单流转"])
    app.include_router(data_router.router, prefix=f"{settings.API_V1_STR}/data", tags=["历史NC数据提取"])

    return app

app = create_app()

if __name__ == "__main__":
    import uvicorn
    # 本地主函数启动项配置
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
