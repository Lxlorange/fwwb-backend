from pydantic import BaseModel, Field
from datetime import datetime

class ForecastRequest(BaseModel):
    """生境预测请求模型"""
    latitude: float = Field(..., description="经度范围 -90 到 90", ge=-90.0, le=90.0)
    longitude: float = Field(..., description="纬度范围 -180 到 180", ge=-180.0, le=180.0)
    timestamp: datetime = Field(..., description="查询起点时间")

class ForecastTimeSeriesPoint(BaseModel):
    """时序数据点"""
    time: datetime = Field(..., description="预测时间点")
    sst: float = Field(..., description="海表温度 Sea Surface Temperature (摄氏度)")
    sss: float = Field(..., description="海表盐度 Sea Surface Salinity (PSU)")
    flow: float = Field(..., description="流速 (m/s)")

class ForecastResponse(BaseModel):
    """生境预测响应模型"""
    series: list[ForecastTimeSeriesPoint] = Field(..., description="未来 72 小时的时序数据")
