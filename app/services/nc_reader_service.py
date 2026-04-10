import math
import logging
from pathlib import Path
from datetime import datetime
from functools import lru_cache
from typing import Dict, Optional, Any

import xarray as xr

logger = logging.getLogger(__name__)

# 数据存储的根目录
BASE_DATA_DIR = Path(r"D:\Code\fwwb2026\data\dataset")

# 模块对应的坐标系映射表
COORD_MAP = {
    "Abnormal_wind_waves": {
        "time": "valid_time",
        "lat": "latitude",
        "lon": "longitude"
    },
    "Marine_elements": {
        "time": "time",
        "lat": "lat",
        "lon": "lon"
    },
    "Mesoscale_vortex": {
        "time": "time",
        "lat": "latitude",
        "lon": "longitude"
    }
}

def _get_file_path(module: str, target_time: datetime) -> Path:
    """
    路径路由工厂：根据模块名和目标时间推断相应的 .nc 文件路径
    """
    if module == "Abnormal_wind_waves":
        # 路径：Abnormal_wind_waves/{YYYY}/{YYYYMM}/data_stream-wave_stepType-instant.nc
        year_str = target_time.strftime("%Y")
        ym_str = target_time.strftime("%Y%m")
        return BASE_DATA_DIR / module / year_str / ym_str / "data_stream-wave_stepType-instant.nc"

    elif module == "Marine_elements":
        # 路径：Marine_elements/{YYYY}/{YYYYMMDD}.nc
        year_str = target_time.strftime("%Y")
        ymd_str = target_time.strftime("%Y%m%d")
        return BASE_DATA_DIR / module / year_str / f"{ymd_str}.nc"

    elif module == "Mesoscale_vortex":
        # 涡旋识别：遍历目录下的时间段文件，需如 19930101_20021231.nc
        vortex_dir = BASE_DATA_DIR / module
        if not vortex_dir.exists():
            raise FileNotFoundError(f"目录不存在: {vortex_dir}")

        for nc_file in vortex_dir.glob("*.nc"):
            stem = nc_file.stem
            try:
                # 解析如 19930101_20021231 的时间范围
                parts = stem.split("_")
                if len(parts) >= 2:
                    start_str, end_str = parts[-2], parts[-1]
                    start_date = datetime.strptime(start_str, "%Y%m%d")
                    end_date = datetime.strptime(end_str, "%Y%m%d")
                    # 截止日期加上那一天的最后一秒
                    end_date = end_date.replace(hour=23, minute=59, second=59)

                    # 如果在时间区间内，匹配成功
                    # 为了比较直接，建议 target_time 使用 naive 时间，或者确保双方 tzinfo 一致
                    if start_date.replace(tzinfo=None) <= target_time.replace(tzinfo=None) <= end_date:
                        return nc_file
            except ValueError:
                # 忽略不符合命名规范的文件
                continue

        raise FileNotFoundError(f"未找到涵盖时间 {target_time} 的涡旋数据文件。")

    else:
        raise ValueError(f"未知的模块名称: {module}")

@lru_cache(maxsize=5)
def _get_dataset(file_path: str) -> xr.Dataset:
    """
    单例加载器。通过 lru_cache 保证单例复用，防止内存浪费。
    受益于 xarray 和底层的 dask，哪怕面对 4GB 的单文件也不会立即吃进内存（懒加载机制）。
    """
    logger.info(f"==> 缓存未命中，开始映射底层的 NC 文件: {file_path}")
    # 启用 engine=netcdf4/h5netcdf 是最佳实践
    return xr.open_dataset(file_path)

def get_point_data(
    module: str,
    target_time: datetime,
    target_lat: float,
    target_lon: float
) -> Dict[str, Optional[float]]:
    """
    统一对外查询接口：获取文件、根据坐标切片，并提取单点的物理变量。

    Args:
        module: 模块名枚举
        target_time: 目标时间
        target_lat: 目标纬度
        target_lon: 目标经度

    Returns:
        Dict[str, float | None]: 当前单点下的所有变量值字典
    """
    # 1. 路由并校验文件路径
    try:
        file_path = _get_file_path(module, target_time)
    except FileNotFoundError as e:
        raise FileNotFoundError(f"[{module}] 缺少对应时间的数据集: {e}")

    if not file_path.exists():
        raise FileNotFoundError(f"[{module}] 文件丢失，预期路径为: {file_path}")

    # 2. 映射与懒加载 Dataset
    ds = _get_dataset(str(file_path))

    # 3. 动态坐标匹配
    c_map = COORD_MAP.get(module)
    if not c_map:
        raise ValueError(f"缺少模块 [{module}] 的坐标映射规范。")

    time_dim = c_map["time"]
    lat_dim = c_map["lat"]
    lon_dim = c_map["lon"]

    if time_dim not in ds.dims and time_dim not in ds.coords:
        raise KeyError(f"数据集中不存在预设的时间维度: {time_dim}")

    sel_kwargs = {
        time_dim: target_time,
        lat_dim: target_lat,
        lon_dim: target_lon
    }

    # 4. 执行多维特征的切片
    try:
        # 使用最邻近切片方法
        point_data = ds.sel(method='nearest', **sel_kwargs)
    except KeyError as e:
        # xarray 如果给的时间或坐标极度超出维度上下限，或是索引不匹配会引发 KeyError
        logger.error(f"坐标超出边界或无法切片引发异常: {e}")
        raise ValueError(f"请求的目标时间或位置超出了当前数据集的存储范围: {e}") from e

    # 5. 解析组装物理变量字典
    result_dict: Dict[str, Optional[float]] = {}

    # 遍历 dataset 中的业务变量（data_vars，排除了 coords 也就是坐标系）
    for var_name in ds.data_vars:
        try:
            val = point_data[var_name].item()

            # 使用 math.isnan 判断无效数据（Python 原生空值判断，对 numpy float64 同样生效）
            if isinstance(val, (float, int)) and math.isnan(val):
                result_dict[var_name] = None
            else:
                result_dict[var_name] = float(val)
        except Exception:
            # 兼容个别由于数据类型不匹配引发 item() 无法转原生的字段
            result_dict[var_name] = None

    return result_dict
