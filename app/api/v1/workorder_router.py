from fastapi import APIRouter
from app.schemas.base import ResponseModel
from app.schemas.workorder import WorkOrderRequest, WorkOrderResponse
from app.services.workorder_service import WorkOrderService

router = APIRouter()

@router.post("/create", response_model=ResponseModel[WorkOrderResponse])
async def create_workorder(request: WorkOrderRequest):
    """
    工单流转 API
    用于在系统检测到海洋垃圾等异常情况触发预警后，向相关人员或自动化清理工作站下达任务。
    """
    result = WorkOrderService.create_work_order(request)
    return ResponseModel.success(data=result)
