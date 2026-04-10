from pydantic import BaseModel, Field
from datetime import datetime

class WorkOrderRequest(BaseModel):
    """创建工单请求模型"""
    alarm_id: str = Field(..., description="触发工单的原始告警ID")
    description: str = Field(default="", description="工单描述信息")

class WorkOrderResponse(BaseModel):
    """工单响应模型"""
    order_id: str = Field(..., description="生成的工单编号")
    status: str = Field(..., description="工单状态，如 PENDING, PROCESSING, DONE")
    created_at: datetime = Field(..., description="工单创建时间")
