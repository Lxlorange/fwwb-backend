import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timezone

from app.main import app

client = TestClient(app)

def test_detect_trash():
    """测试海洋垃圾识别接口"""
    payload = {
        "image_base64": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEAAAAAA..."
    }
    response = client.post("/api/v1/cv/detect_trash", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert data["code"] == 200
    assert data["message"] == "success"

    # 验证业务数据载荷
    results = data["data"]["results"]
    assert isinstance(results, list)
    if len(results) > 0:
        assert "label" in results[0]
        assert "confidence" in results[0]
        assert "box" in results[0]

def test_habitat_forecast():
    """测试生境预测接口"""
    payload = {
        "latitude": 22.5,
        "longitude": 114.0,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    response = client.post("/api/v1/forecast/habitat", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert data["code"] == 200
    assert data["message"] == "success"

    series = data["data"]["series"]
    assert isinstance(series, list)
    assert len(series) == 72  # 应该返回72小时的数据

    first_point = series[0]
    assert "time" in first_point
    assert "sst" in first_point
    assert "sss" in first_point
    assert "flow" in first_point

def test_detect_wind_wave_anomaly():
    """测试风浪预警接口"""
    payload = {
        "recent_data": [
            {"wind_speed": 12.5, "wave_height": 2.1},
            {"wind_speed": 16.2, "wave_height": 3.4},
            {"wind_speed": 14.0, "wave_height": 2.8}
        ]
    }
    response = client.post("/api/v1/anomaly/wind_wave", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert data["code"] == 200
    assert data["message"] == "success"

    anomaly_data = data["data"]
    assert "anomaly_probability" in anomaly_data
    assert "warning_level" in anomaly_data
    assert "suggest_sink" in anomaly_data

def test_create_workorder():
    """测试工单流转接口"""
    payload = {
        "alarm_id": "ALARM-20260410-001",
        "description": "网箱区域发现疑似塑料垃圾，请求清理"
    }
    response = client.post("/api/v1/workorder/create", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert data["code"] == 200
    assert data["message"] == "success"

    order_data = data["data"]
    assert "order_id" in order_data
    assert order_data["order_id"].startswith("WO-")
    assert order_data["status"] == "PENDING"
    assert "created_at" in order_data
