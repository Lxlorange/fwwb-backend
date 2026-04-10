from fastapi import APIRouter
from app.schemas.base import ResponseModel
from app.schemas.anomaly import AnomalyRequest, AnomalyResponse
from app.services.anomaly_service import AnomalyService

router = APIRouter()

@router.post("/wind_wave", response_model=ResponseModel[AnomalyResponse])
async def detect_wind_wave_anomaly(request: AnomalyRequest):
    """
    风浪预警 API
    传入近期的风与海浪数据，进行异常分析与评估，并反馈是否需要系统级应对手段（比如下沉深海网箱）。
    """
    result = AnomalyService.analyze_wind_wave(request)
    return ResponseModel.success(data=result)
