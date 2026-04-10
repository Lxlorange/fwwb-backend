import random
from app.schemas.cv import CVDetectRequest, CVDetectResponse, DetectResultItem, BoundingBox

class CVService:
    """
    海洋垃圾识别业务逻辑层 (Mock实现)
    """
    @staticmethod
    def detect_trash(request: CVDetectRequest) -> CVDetectResponse:
        """
        处理传入的图像Base64，分析其中的海洋垃圾。
        返回Mock生成的BBox与置信度。
        """
        # 假设我们能识别出的垃圾种类
        labels = ["plastic_bottle", "fishing_net", "floating_wood", "styrofoam"]

        # 随机生成 1~3 个识别结果
        mock_results = []
        for _ in range(random.randint(1, 3)):
            x_min = random.uniform(10.0, 100.0)
            y_min = random.uniform(10.0, 100.0)

            item = DetectResultItem(
                label=random.choice(labels),
                confidence=round(random.uniform(0.65, 0.99), 2),
                box=BoundingBox(
                    x_min=round(x_min, 2),
                    y_min=round(y_min, 2),
                    x_max=round(x_min + random.uniform(20, 50), 2),
                    y_max=round(y_min + random.uniform(20, 50), 2)
                )
            )
            mock_results.append(item)

        return CVDetectResponse(results=mock_results)
