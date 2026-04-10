import random
import logging
from datetime import timedelta
from app.schemas.forecast import ForecastRequest, ForecastResponse, ForecastTimeSeriesPoint
from app.services.nc_reader_service import get_point_data

logger = logging.getLogger(__name__)

class ForecastService:
    """
    生境预测业务逻辑层
    """
    @staticmethod
    def get_habitat_forecast(request: ForecastRequest) -> ForecastResponse:
        start_time = request.timestamp
        series = []

        try:
            # 尝试从 NC 数据集获取真实的基准数据 (验证双向通路)
            real_data = get_point_data(
                module="Marine_elements",
                target_time=start_time,
                target_lat=request.latitude,
                target_lon=request.longitude
            )
            base_sst = real_data.get("sst") or 25.0
            base_sss = real_data.get("sss") or 34.0
            base_flow = real_data.get("ssu") or 0.5
            logger.info(f"通路校验成功: 关联到底层 NC 数据集 - sst:{base_sst:.1f}, sss:{base_sss:.1f}")
        except Exception as e:
            logger.warning(f"通路走不通（通常是磁盘无文件），回退Mock基准值: {e}")
            base_sst = random.uniform(15.0, 28.0)
            base_sss = random.uniform(30.0, 35.0)
            base_flow = random.uniform(0.1, 1.5)

        for hour_offset in range(72):
            point_time = start_time + timedelta(hours=hour_offset)

            # 利用小的随机数模拟波动
            # SST 在一天周期内有平滑变化，这里简单用随机数处理
            point_sst = base_sst + random.uniform(-0.5, 0.5)
            point_sss = base_sss + random.uniform(-0.1, 0.1)
            point_flow = base_flow + random.uniform(-0.2, 0.2)

            series.append(ForecastTimeSeriesPoint(
                time=point_time,
                sst=round(point_sst, 2),
                sss=round(point_sss, 2),
                flow=round(max(0.0, point_flow), 2)  # 流速不为负数
            ))

        return ForecastResponse(series=series)
