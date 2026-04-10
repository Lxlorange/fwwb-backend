import random
import logging
from app.schemas.anomaly import AnomalyRequest, AnomalyResponse
from app.services.nc_reader_service import get_point_data

logger = logging.getLogger(__name__)

class AnomalyService:
    """
    风浪异常与预警业务逻辑层
    """
    @staticmethod
    def analyze_wind_wave(request: AnomalyRequest) -> AnomalyResponse:
        """
        接收近期的风速与波高数据，推断异常概率并决策是否采取系统行动（如下沉网箱）。
        """
        # 计算近期风速波高的平均值
        avg_wind = sum([p.wind_speed for p in request.recent_data]) / len(request.recent_data)
        avg_wave = sum([p.wave_height for p in request.recent_data]) / len(request.recent_data)

        # 尝试从 NC 数据集验证是否具有波浪历史基底上下文
        try:
            real_nc_wave = get_point_data(
                module="Abnormal_wind_waves",
                target_time=request.timestamp,
                target_lat=request.latitude,
                target_lon=request.longitude
            )
            nc_swh = real_nc_wave.get("swh")
            logger.info(f"通路校验成功: 关联到底层异常风浪NC背景模型，有效波高: {nc_swh} m")
        except Exception as e:
            logger.warning(f"数据通道异常/无可加载文件，仅走前端Mock逻辑: {e}")

        # 基于简单的Mock算法：如果平均风速大于 15m/s 或者 浪高大于 3m，则高概率异常
        if avg_wind > 15.0 or avg_wave > 3.0:
            prob = random.uniform(0.8, 0.99)
            level = "HIGH"
            suggest_sink = True
        elif avg_wind > 10.0 or avg_wave > 2.0:
            prob = random.uniform(0.4, 0.79)
            level = "MEDIUM"
            suggest_sink = False
        else:
            prob = random.uniform(0.01, 0.39)
            level = "LOW"
            suggest_sink = False

        return AnomalyResponse(
            anomaly_probability=round(prob, 3),
            warning_level=level,
            suggest_sink=suggest_sink
        )
