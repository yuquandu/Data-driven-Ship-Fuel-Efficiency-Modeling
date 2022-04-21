#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 30 01:57:53 2021

@author: ychen72
"""

import numpy as np
import xarray as xr
import pandas as pd
import datetime as dt

import os
import cfgrib
import eccodes
import matplotlib


import utils
from utils import *


# ocean current data path
path = './Copernicus_Ocean_Current_20140201_20160315/'
filenames= os.listdir(path)
filenames.sort()

path_1 = []
path_2 = []
path_3 = []

for filename in filenames[:33]:
    path_1.append(os.path.join(path, filename))
    #data_list_1.append(xr.open_mfdataset(os.path.join(path, filename), engine=('netcdf4')))
for filename in filenames[32:69]:
    path_2.append(os.path.join(path, filename))
    #data_list_2.append(xr.open_mfdataset(os.path.join(path, filename), engine=('netcdf4'))) 
for filename in filenames[68:]:
    path_3.append(os.path.join(path, filename))
    #data_list_3.append(xr.open_mfdataset(os.path.join(path, filename), engine=('netcdf4')))

# load file
data_ow_1  = xr.open_mfdataset(path_1, engine=("netcdf4"), concat_dim=['time'], combine='nested', parallel=True)
data_ow_2  = xr.open_mfdataset(path_2, engine=("netcdf4"), concat_dim=['time'], combine='nested', parallel=True)
data_ow_3  = xr.open_mfdataset(path_3, engine=("netcdf4"), concat_dim=['time'], combine='nested', parallel=True)

_, index_1 = np.unique(data_ow_1['time'], return_index=True)
_, index_2 = np.unique(data_ow_2['time'], return_index=True)
_, index_3 = np.unique(data_ow_3['time'], return_index=True)
# print(index_1)
# print(index_2)
# print(index_3)
data_o_1 = data_ow_1.isel(time=index_1)
data_o_2 = data_ow_2.isel(time=index_2)
data_o_3 = data_ow_3.isel(time=index_3)


# select data range
data_clean_t1 = data_o_1.sel(time=slice("2014-02-01", "2015-01-01"))
data_clean_t2 = data_o_2.sel(time=slice("2015-01-01", "2016-01-01"))
data_clean_t3 = data_o_3.sel(time=slice("2016-01-01", "2016-04-01"))

# resample data
data_clean_t1 = data_clean_t1.resample(time='1H').mean('time').ffill(dim='time')
data_clean_t2 = data_clean_t2.resample(time='1H').mean('time').ffill(dim='time')
data_clean_t3 = data_clean_t2.resample(time='1H').mean('time').ffill(dim='time')

# ship data path
path_ship = './data_o_selection/Ship_S3_Correct_Selection.xlsx'
path_save = './data_o_oc/Ship_S3_Correct_Selection_OC.xlsx'

# import data
data_s = pd.read_csv(path_ship)   

# data length 
data_s_len = len(data_s)
data_s_index = data_s.index.tolist()
# print(data_s.describe)

# =============================================================================
# lon_a = data_s['lon new']
#     
# for i in data_s_index:
#     if lon_a[i] < 0:
#         data_s['lon new'][i] = lon_a[i] + 360
# =============================================================================
        
# set time, lon and lat range
select_time = pd.to_datetime(data_s['Current GMT Dttm']).dt.strftime("%Y-%m-%dT%H:%M:%S")
#select_time = pd.to_datetime(data_s['Current GMT Dttm']).dt.strftime("%Y-%m-%dT%H:%M:00")
select_lon  = data_s['Longitude']
select_lat  = data_s['Latitude']

# point_list = zip(select_lat, select_lon)

new_data_clean_1 = pd.DataFrame([])
new_data_clean_2 = pd.DataFrame([])
new_data_clean_3 = pd.DataFrame([])
 
# da.stack(pos=("lon", "lat")).sel(pos=points).mean("time")

# select data according time, lon and lat
for i in range(data_s_len):
    if select_time[i].split('-')[0] == '2014':
        data_clean_l1 = data_clean_t1.sel(time=select_time[i], longitude=select_lon[i], latitude=select_lat[i], depth=[0], method='nearest').compute()
        # DT_1 = data_clean_l1.to_pandas()
        DT_1 = data_clean_l1.to_dataframe()
        new_data_clean_1 = new_data_clean_1.append([DT_1])
        #print("success")
        #print(i)

    if select_time[i].split('-')[0] == '2015':
        data_clean_l2 = data_clean_t2.sel(time=select_time[i], longitude=select_lon[i], latitude=select_lat[i], method='nearest').compute()
        DT_2 = data_clean_l2.to_dataframe()
        new_data_clean_2 = new_data_clean_2.append([DT_2])
        #print("success")
        
    if select_time[i].split('-')[0] == '2016':

        data_clean_l3 = data_clean_t3.sel(time=select_time[i], longitude=select_lon[i], latitude=select_lat[i], method='nearest').compute()
        # DT_3 = data_clean_l3.to_pandas()
        DT_3 = data_clean_l3.to_dataframe()
        new_data_clean_3 = new_data_clean_3.append([DT_3])
        #print("success")
print('success')       

# concat dataset
data_w = pd.concat([new_data_clean_1, new_data_clean_2, new_data_clean_3], axis=0, ignore_index=True) 
data_w.columns 

# save data
data_w.to_csv(path_save, index=None)
print('data save')

