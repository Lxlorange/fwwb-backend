import uuid
from datetime import datetime, timezone
from app.schemas.workorder import WorkOrderRequest, WorkOrderResponse

class WorkOrderService:
    """
    工单流转业务逻辑层 (Mock实现)
    """
    @staticmethod
    def create_work_order(request: WorkOrderRequest) -> WorkOrderResponse:
        """
        根据告警ID，创建一条新的清理工单。
        进入待处理(PENDING)状态。
        """
        # 生成一个模拟的唯一工单流水号
        order_sn = f"WO-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}-{str(uuid.uuid4())[:4].upper()}"

        # 逻辑处理：将告警ID与工单ID在数据库里绑定。此处省略，直接返回结果。

        return WorkOrderResponse(
            order_id=order_sn,
            status="PENDING",
            created_at=datetime.now(timezone.utc)
        )
