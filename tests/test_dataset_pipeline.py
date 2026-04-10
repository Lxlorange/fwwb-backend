import httpx
import time
from datetime import datetime
import xarray as xr
import pandas as pd
from pathlib import Path

BASE_URL = "http://localhost:8000/api/v1"
BASE_DATA_DIR = Path(r"D:\Code\fwwb2026\data\dataset")

def get_real_data_sample(module_name: str):
    """
    智能探针：潜入本地原始数据库，不论你年份多混乱，
    只要找到任意一个合法的 .nc 文件，就从中提取一个中心点的真实时间、经度、纬度作为靶点。
    """
    module_dir = BASE_DATA_DIR / module_name
    if not module_dir.exists():
        print(f"[-] 目录不存在: {module_dir}")
        return None

    # 递归查找该模块下的任意 .nc 文件
    # 排除了 macOS 产生的隐藏切片元数据文件 (常以 ._ 开头) 避免被当成真正的 NC 库读取
    nc_files = [f for f in module_dir.rglob("*.nc") if not f.name.startswith(".")]
    if not nc_files:
         print(f"[-] 未找到任何 {module_name} 模块的 .nc 文件")
         return None

    # 随便取最新或随便一个找到的文件作为探测基准
    target_file = nc_files[-1]
    print(f"[*] 探针成功发现真实文件: {target_file.name}")

    try:
        ds = xr.open_dataset(target_file)

        # 兼容匹配其特有坐标名
        time_dim = "valid_time" if "valid_time" in ds.coords else "time"
        lat_dim = "latitude" if "latitude" in ds.coords else "lat"
        lon_dim = "longitude" if "longitude" in ds.coords else "lon"

        # 为了避免全0或NaN这种边缘数据，我们不取第0点，而是取阵列中间点
        t_idx = len(ds[time_dim]) // 2
        lat_idx = len(ds[lat_dim]) // 2
        lon_idx = len(ds[lon_dim]) // 2

        t_val = ds[time_dim].values[t_idx]
        lat_val = float(ds[lat_dim].values[lat_idx])
        lon_val = float(ds[lon_dim].values[lon_idx])

        ds.close()

        # 利用 pandas 把 numpy64 诡异的时间对象安全转为标准 iso 字符串
        timestamp_str = pd.Timestamp(t_val).isoformat()

        return timestamp_str, lat_val, lon_val
    except Exception as e:
        print(f"[-] 尝试从 {target_file.name} 提取真实物理参数靶点时报错: {e}")
        return None


def test_pipeline():
    """
    管道通信测试总控。
    注意：在执行此文件前，确保 FastAPI 后端正在运行 `python app/main.py`
    """
    print("\n" + "="*60)
    print("🚀 启动全链路 (Frontend -> Router -> Service -> NC Dataset) 验证")
    print("="*60)

    client = httpx.Client(timeout=10.0)

    # ---------------- 场景 1：生境预测测试 ---------------- #
    print("\n📍 打通测试一： [生境预测通道 - Marine_elements]")
    marine_sample = get_real_data_sample("Marine_elements")

    if marine_sample:
        target_time, target_lat, target_lon = marine_sample
        print(f"[!] 构造真实探查请求: 时间={target_time}, 纬度={target_lat:.2f}, 经度={target_lon:.2f}")

        payload = {
            "latitude": target_lat,
            "longitude": target_lon,
            "timestamp": target_time
        }
        try:
            res = client.post(f"{BASE_URL}/forecast/habitat", json=payload)
            if res.status_code == 200:
                print("✓ 后端成功返回!")
                print(f"✓ 获得预测数据体首列 (SST海表温度等): {res.json()['data']['series'][0]}")
            else:
                print(f"X 服务端报错 {res.status_code}: {res.text}")
        except Exception as e:
            print(f"通信断开: {e}")
    else:
        print("X 由于未能找到基准测试文件，跳过该接口请求。")


    time.sleep(1)

    # ---------------- 场景 2：风浪预警测试 ---------------- #
    print("\n📍 打通测试二： [风浪预警通道 - Abnormal_wind_waves]")
    waves_sample = get_real_data_sample("Abnormal_wind_waves")

    if waves_sample:
        target_time, target_lat, target_lon = waves_sample
        print(f"[!] 构造真实探查请求: 时间={target_time}, 纬度={target_lat:.2f}, 经度={target_lon:.2f}")

        payload_anomaly = {
            "recent_data": [
                {"wind_speed": 10.0, "wave_height": 2.5}
            ],
            "latitude": target_lat,
            "longitude": target_lon,
            "timestamp": target_time
        }
        try:
            res2 = client.post(f"{BASE_URL}/anomaly/wind_wave", json=payload_anomaly)
            if res2.status_code == 200:
                print("✓ 后端正常返回 HTTP 200!")
                print(f"✓ AI 判准结果与建议: {res2.json()['data']}")
            else:
                print(f"X 服务端报错 {res2.status_code}: {res2.text}")
        except Exception as e:
            print(f"通信断开: {e}")
    else:
         print("X 由于未能找到基准测试文件，跳过该接口请求。")

    print("\n" + "="*60)
    print("✅ 测试结束。请注意观察后端的 Terminal 日志是否也成功打印了“通道走通”！")


if __name__ == "__main__":
    test_pipeline()
