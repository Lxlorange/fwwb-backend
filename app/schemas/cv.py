from pydantic import BaseModel, Field

class CVDetectRequest(BaseModel):
    """海洋垃圾识别请求模型"""
    image_base64: str = Field(..., description="图片或视频帧的 Base64 编码数据")

class BoundingBox(BaseModel):
    """边界框数据模型"""
    x_min: float = Field(..., description="框左上角X坐标")
    y_min: float = Field(..., description="框左上角Y坐标")
    x_max: float = Field(..., description="框右下角X坐标")
    y_max: float = Field(..., description="框右下角Y坐标")

class DetectResultItem(BaseModel):
    """单条识别结果"""
    label: str = Field(..., description="识别目标的标签，如 plastic, net")
    confidence: float = Field(..., description="置信度评分 (0.0~1.0)")
    box: BoundingBox = Field(..., description="边界框坐标")

class CVDetectResponse(BaseModel):
    """海洋垃圾识别响应模型"""
    results: list[DetectResultItem] = Field(..., description="识别出的垃圾目标列表")
