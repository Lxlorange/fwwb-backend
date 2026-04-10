import httpx
import time
from datetime import datetime

BASE_URL = "http://localhost:8000/api/v1"

def test_pipeline():
    """
    管道通信测试总控。
    注意：在执行此文件前，一定要开个CMD让 `python app/main.py` 跑着，看后端控制台！
    """
    print("\n" + "="*50)
    print("🚀 开始全链路 (Frontend - Router - Service - Dataset) 验证")
    print("="*50)

    client = httpx.Client(timeout=10.0)
    target_time_str = datetime.now().isoformat()

    try:
        print("\n📍 测试 [生境预测通道 - Marine_elements]")
        payload = {
            "latitude": 28.5,
            "longitude": 125.0,
            "timestamp": target_time_str
        }
        res = client.post(f"{BASE_URL}/forecast/habitat", json=payload)

        if res.status_code == 200:
            print("✓ 后端正常返回 HTTP 200!")
            print(f"✓ 预测首批数据: {res.json()['data']['series'][0]}")
            print("❗ -> 请回到执行 `python app/main.py` 的服务端控制台，观察 logger 打印信息。")
        else:
            print(f"X 服务端报错 {res.status_code}: {res.text}")

        time.sleep(1)

        print("\n📍 测试 [风浪预警通道 - Abnormal_wind_waves]")
        payload_anomaly = {
            "recent_data": [
                {"wind_speed": 10.0, "wave_height": 2.5}
            ],
            "latitude": 22.5,
            "longitude": 114.0,
            "timestamp": target_time_str
        }
        res2 = client.post(f"{BASE_URL}/anomaly/wind_wave", json=payload_anomaly)

        if res2.status_code == 200:
            print("✓ 后端正常返回 HTTP 200!")
            print(f"✓ 预警反馈: {res2.json()['data']}")
            print("❗ -> 同样请去服务端控制台观察关联 NC 的日志反馈。")
        else:
            print(f"X 服务端报错 {res2.status_code}: {res2.text}")

    except Exception as e:
        print(f"与服务器断开连接 (请确保 python app/main.py 正在运行): {e}")

if __name__ == "__main__":
    test_pipeline()
