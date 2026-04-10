from fastapi import APIRouter
from app.schemas.base import ResponseModel
from app.schemas.cv import CVDetectRequest, CVDetectResponse
from app.services.cv_service import CVService

router = APIRouter()

@router.post("/detect_trash", response_model=ResponseModel[CVDetectResponse])
async def detect_trash(request: CVDetectRequest):
    """
    海洋垃圾识别 API
    传入包含图片或视频帧Base64信息的请求结构，返回识别到的目标边界框与置信度。
    """
    result = CVService.detect_trash(request)
    return ResponseModel.success(data=result)
