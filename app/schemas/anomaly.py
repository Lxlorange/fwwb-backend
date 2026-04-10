from pydantic import BaseModel, Field

class WindWaveDataPoint(BaseModel):
    """单次风速波高数据"""
    wind_speed: float = Field(..., description="风速 (m/s)")
    wave_height: float = Field(..., description="波高 (m)")

class AnomalyRequest(BaseModel):
    """风浪预警请求模型"""
    recent_data: list[WindWaveDataPoint] = Field(..., description="近期连续的风速波高监测数组", min_length=1)
    latitude: float = Field(default=22.5, description="纬度范围", ge=-90.0, le=90.0)
    longitude: float = Field(default=114.0, description="经度范围", ge=-180.0, le=180.0)
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="查询时间")

class AnomalyResponse(BaseModel):
    """风浪预警响应模型"""
    anomaly_probability: float = Field(..., description="异常发生概率 (0.0~1.0)")
    warning_level: str = Field(..., description="告警等级 (NONE, LOW, MEDIUM, HIGH)")
    suggest_sink: bool = Field(..., description="是否建议/下达网箱下沉指令")
