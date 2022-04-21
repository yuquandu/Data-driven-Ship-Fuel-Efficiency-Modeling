#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jul 31 20:11:57 2021

@author: ychen72
"""


import xarray as xr
import pandas as pd
import datetime as dt

import os
import cfgrib
import eccodes
import openpyxl
import matplotlib
import pandas as pd

import utils
from utils import *

T0=time.time()

# ERA5 dataset path
file_ocean_wave_1 = './ocean_wave_2014.grib'
file_ocean_wave_2 = './ocean_wave_2015.grib'
file_ocean_wave_3 = './ocean_wave_2016.grib'
# backend_kwargs={'filter_by_keys': {"time": pd.date_range("start"="2014-02-01 00:00:00", "end"="2016-03-15 00:00:00", "freq"="6T"), "reference_time": pd.Timestamp("2014-02-01 00:00:00")}

# read dataset
data_ow_1 = xr.open_dataset(file_ocean_wave_1, engine=('cfgrib'))
data_ow_2 = xr.open_dataset(file_ocean_wave_2, engine=('cfgrib'))
data_ow_3 = xr.open_dataset(file_ocean_wave_3, engine=('cfgrib'))
print(data_ow_1)
print(data_ow_2)
print(data_ow_3)
# print(data_ow.info)

# ship dataset path
path_ship = './data_o_selection/Ship_S3_Correct_Selection.xlsx'
path_save = './data_o_ow/Ship_S3_Correct_Selection_OW.xlsx'

# import data
data_s = pd.read_excel(path_ship)    # Read Excel table
# print(data_s.describe)
# print(data_s.columns)

# =============================================================================
# data_s_len   = len(data_s)
# data_s_index = data_s.index.tolist()
# print(data_s.describe)
# 
#    
# lon_a = data_s['Longitude']
# for i in data_s_index:
#     if lon_a[i] < 0:
#         data_s['Longitude'][i] = lon_a[i] + 360
# =============================================================================

# select dataset
data_s['Current GMT Dttm'] = pd.to_datetime(data_s['TIMESTAMP UTC']).dt.strftime("%Y-%m-%d %H:%M:%S")
name_s = ['Current GMT Dttm', 'LON', 'LAT']
data_c = data_s[name_s]   
data_c = data_c.set_index(data_s['Current GMT Dttm'])
data_c.index = pd.to_datetime(data_c.index, unit='ns')
data_c = data_c.iloc[:, [1,2]]

# resample dataset
data_h = data_c.resample('H').mean()
# data_re['Current GMT Dttm'] = data_re.index
data_h.reset_index(inplace=True)
data_h.dropna(axis=0, how='any', inplace=True)  
data_h.reset_index(drop=True, inplace=True)
data_h_len = len(data_h)
data_h_index = data_h.index.tolist()
    
lon_a = data_h['LON']
for i in data_h_index:
    if lon_a[i] < 0:
        data_h['LON'][i] = lon_a[i] + 360

# set time, lon and lat range
select_time = pd.to_datetime(data_h['Current GMT Dttm']).dt.strftime("%Y-%m-%dT%H:00:00")
#select_time = pd.to_datetime(data_s['Current GMT Dttm']).dt.strftime("%Y-%m-%dT%H:%M:00")
select_lon  = data_h['LON']
select_lat  = data_h['LAT']

# point_list = zip(select_lat, select_lon)

new_data_clean_1 = pd.DataFrame([])
new_data_clean_2 = pd.DataFrame([])
new_data_clean_3 = pd.DataFrame([])

# =============================================================================
# data_clean_t1 = data_ow_1.sel(time=slice("2014-02-01", "2016-04-01"))
# data_clean_t2 = data_ow_2.sel(time=slice("2014-02-01", "2016-04-01"))
# data_clean_t3 = data_ow_3.sel(time=slice("2014-02-01", "2016-04-01"))
# 
# # data_clean_t1_daily = data_clean_t1.resample(time='1D').mean('time')
# # da.stack(pos=("lon", "lat")).sel(pos=points).mean("time")
# =============================================================================


for i in data_h_index:
    if select_time[i].split('-')[0] == '2014':
        data_clean_1 = data_ow_1.sel(time=select_time[i], longitude=select_lon[i], latitude=select_lat[i], method='nearest')
        DT_1 = data_clean_1.to_pandas()
        new_data_clean_1 = new_data_clean_1.append([DT_1])

    if select_time[i].split('-')[0] == '2015':
        data_clean_2 = data_ow_2.sel(time=select_time[i], longitude=select_lon[i], latitude=select_lat[i], method='nearest')
        DT_2 = data_clean_2.to_pandas()
        new_data_clean_2 = new_data_clean_2.append([DT_2])
        
    if select_time[i].split('-')[0] == '2016':
       data_clean_3 = data_ow_3.sel(time=select_time[i], longitude=select_lon[i], latitude=select_lat[i], method='nearest')
       DT_3 = data_clean_3.to_pandas()
       new_data_clean_3 = new_data_clean_3.append([DT_3])
print('success')    

data_w = pd.concat([new_data_clean_1, new_data_clean_2, new_data_clean_3], axis=0, ignore_index=True) 
data_w.columns 


# column_names = ['u10', 'v10', 'mdts', 'mdww', 'mpts', 'mpww', 'mwd', 'mwp', 'sst', 'swh', 'shts', 'shww']
column_names = ['Current GMT Dttm', 'Longitude', 'Latitude',
                '10 metre U wind component', '10 metre V wind component', 'Mean direction of total swell', 'Mean direction of wind waves', 'Mean period of total swell', 'Mean period of wind waves',
                'Mean wave direction', 'Mean wave period', 'Sea surface temperature', 
                'Significant height of combined wind waves and swell', 'Significant height of total swell', 'Significant height of wind waves']

# column_names = ['time', 'lon', 'lat', 'u10', 'v10', 'mdts', 'mdww', 'mpts', 'mpww', 'mwd', 'mwp', 'sst', 'swh', 'shts', 'shww']
data_clean = pd.concat([select_time, select_lon, select_lat, data_w], names=column_names, axis=1, ignore_index=True)  
data_clean.columns = column_names

data_clean.to_excel(path_save, index=False)

T1=time.time()
T_S = T1- T0
print(T_S)
# T_S.to_txt(path_save+'oc_time.txt')