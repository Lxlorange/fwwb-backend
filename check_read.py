# _*_ coding : utf-8 _*_
# @Time :  18:23
# @Author : Lxl
# @File ： test_read
# @ProjectName : fwwb-backend
import xarray as xr



file_path = r"D:\Code\fwwb2026\data\dataset\Mesoscale_vortex\19930101_20021231.nc"
dataset = xr.open_dataset(file_path)
print(dataset)