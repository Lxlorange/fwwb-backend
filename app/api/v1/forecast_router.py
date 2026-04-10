from fastapi import APIRouter
from app.schemas.base import ResponseModel
from app.schemas.forecast import ForecastRequest, ForecastResponse
from app.services.forecast_service import ForecastService

router = APIRouter()

@router.post("/habitat", response_model=ResponseModel[ForecastResponse])
async def habitat_forecast(request: ForecastRequest):
    """
    海洋生境预测 API
    传入当前经纬度和时间，返回未来 72 小时的温度(SST)、盐度(SSS)、流速特征。
    """
    result = ForecastService.get_habitat_forecast(request)
    return ResponseModel.success(data=result)
