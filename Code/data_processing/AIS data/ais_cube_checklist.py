# -*- coding: utf-8 -*-
"""
Created on Fri Jul 30 10:13:45 2021

@author: YY_Chen
"""

import os
import pandas as pd
import numpy as np
import openpyxl
import datetime
import math
import netCDF4 as nc

from global_land_mask import globe

# dataset path
path = './data_a_o/Ship_S1_Ais.csv'
path_save_cube = './data_a_o_selection/Ship_S1_Ais_Selection.xlxs'  

# read csv file
data_o     = pd.read_csv(path)   
data_clean = data_o.copy()  
data_lon_lat_clean_index = data_clean.index.tolist()

# lon and lat correct
checklist = []
# data_clean_result = pd.DataFrame()
for i in data_lon_lat_clean_index:
#for i in range(2):
    data_lon_lat_clean = data_clean.iloc[i]
    lon_deg_min = data_lon_lat_clean['LON']
    lat_deg_min = data_lon_lat_clean['LAT']
    
# =============================================================================
#     if lon_deg_min > 180:
#         lon_deg_min = 180
#         data_clean.loc[i,'Longitude'] = '180'
#     if lon_deg_min < -180:
#         lon_deg_min = -180
#         data_clean.loc[i,'Longitude'] = '-180'
# =============================================================================
        
    is_on_land = globe.is_land(lat_deg_min, lon_deg_min)
    #is_on_land = is_land(lon_deg_min, lat_deg_min)
    if is_on_land == True:
        checklist.append(i)
        

time_index = pd.date_range(start='1/1/2014', end='1/1/2017', freq='H')
data_time = pd.DataFrame(time_index, columns=['Current GMT Dttm'])
data_time['Current GMT Dttm'] = pd.to_datetime(data_time['Current GMT Dttm']).dt.strftime('%Y-%m-%d %H:00:00')   

data_clean['Current GMT Dttm'] = pd.to_datetime(data_clean['TIMESTAMP UTC']).dt.strftime('%Y-%m-%d %H:00:00')
data_clean = data_clean.drop_duplicates(subset=['Current GMT Dttm'], keep='first')
data_clean.sort_values(by='Current GMT Dttm', inplace=True)

# data_m = time_index.join(data_clean, how='outer')
data_m = pd.merge(data_time, data_clean, on='Current GMT Dttm', how='outer')
data_m = data_m.drop_duplicates(subset=['Current GMT Dttm'], keep='first')
data_m.to_excel(path_save_cube, index=None)

print('Data saved')
