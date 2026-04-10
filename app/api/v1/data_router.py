from fastapi import APIRouter, Query
from app.schemas.base import ResponseModel
from datetime import datetime, timedelta
import random

router = APIRouter()

@router.get("/nc_extract", response_model=ResponseModel)
async def extract_nc_data(
    start_time: str = Query(..., description="开始时间 ISO 格式"),
    end_time: str = Query(..., description="结束时间 ISO 格式"),
    lat: float = Query(22.5, description="目标解析纬度"),
    lon: float = Query(114.0, description="目标解析经度")
):
    try:
        # ============== 真实 NC 文件提取逻辑 (待真实环境下取消注释并安装 xarray/netCDF4 使用) ==============
        # import xarray as xr
        # import pandas as pd
        # ds = xr.open_dataset("app/data/real_ocean_data.nc")
        # subset = ds.sel(time=slice(start_time, end_time), lat=lat, lon=lon, method="nearest")
        # df = subset.to_dataframe().reset_index()
        # results = df.to_dict(orient="records")
        # ====================================================================

        # 以下为保证前后端顺利打通的 mock NC 文件流
        s_str = start_time if start_time.endswith("Z") else start_time + "Z"
        e_str = end_time if end_time.endswith("Z") else end_time + "Z"
        s_str = s_str.replace("Z", "+00:00")
        e_str = e_str.replace("Z", "+00:00")

        start_dt = datetime.fromisoformat(s_str)
        end_dt = datetime.fromisoformat(e_str)

        results = []
        curr_dt = start_dt
        while curr_dt <= end_dt:
            results.append({
                "time": curr_dt.isoformat().replace('+00:00', 'Z'),
                "sst": round(25.0 + random.uniform(-0.5, 0.5), 2),
                "sss": round(34.0 + random.uniform(-0.2, 0.2), 2),
                "wave_height": round(1.5 + random.uniform(-0.3, 0.3), 2)
            })
            curr_dt += timedelta(hours=6)

        return ResponseModel.success(data={
            "target_lat": lat,
            "target_lon": lon,
            "total_points": len(results),
            "series": results
        })
    except Exception as e:
        return ResponseModel(code=500, message=f"NC 文件解析或数据加载失败: {str(e)}", data=None)