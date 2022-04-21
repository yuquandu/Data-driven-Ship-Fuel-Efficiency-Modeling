# -*- coding: utf-8 -*-
"""
Created on Fri Aug 20 00:43:54 2021

@author: YY_Chen
"""

import os
import math
import itertools
import pandas as pd
import datetime as dt

from pyecharts import options as opts 
from pyecharts.charts import Geo, Map3D
from math import radians, cos, sin, asin, sqrt
from pyecharts.globals import ChartType, SymbolType

# dataset path
path_rep   = './data_o_selection/Ship_S3_Correct_Selection.xlsx'
path_wea   = './data_o_combination/Ship_S3_OW_OC_Combinattion.xlsx' 
path_save  = './data_management/Ship_S3_Voyage_Weather_Combination.xlsx'

# read xlsx     
data_rep = pd.read_excel(path_rep)
data_rep = data_rep.dropna(axis=0, how='any')
data_wea = pd.read_excel(path_wea)

data_w_new = pd.DataFrame()

# copy data
data_o = data_wea.copy()

# change data format
data_o['Current GMT Dttm']   = pd.to_datetime(data_o['Current GMT Dttm'], format='%Y-%m-%d').dt.date
data_rep['Current GMT Dttm'] = pd.to_datetime(data_rep['Current GMT Dttm'], format='%Y-%m-%d %H:%M:%S').dt.floor('1D') 

data_w = data_rep.groupby(by='Current GMT Dttm').mean()
data_w.reset_index(inplace=True)

# change data format
data_w['Current GMT Dttm'] = pd.to_datetime(data_w['Current GMT Dttm'], format='%Y-%m-%d').dt.date

# merge data
data_m = pd.merge(data_w, data_o, on='Current GMT Dttm')
data_m.drop_duplicates('Current GMT Dttm', inplace=True, ignore_index=True)


data_w_new['Current GMT Dttm']      = data_m['Current GMT Dttm']
data_w_new['Speed Made Good (Kts)'] = data_m['Speed Made Good (Kts)']
data_w_new['Vessel Trim (Mtrs)']    = data_m['Vessel Trim (Mtrs)']
data_w_new['Vsl Displacement']      = data_m['Vsl Displacement Correct']
data_w_new['Water Temperature']     = data_m['Sea surface temperature']-273.15
data_w_new['Wind Speed']            = (data_m['10 metre U wind component']**2 + data_m['10 metre V wind component']**2)**0.5

wind_d_list = []
for i in range(len(data_m)):
    if data_m['10 metre U wind component'][i] > 0 and data_m['10 metre V wind component'][i] > 0:
        wind_d = 180*math.atan(data_m['10 metre U wind component'][i]/data_m['10 metre V wind component'][i])/math.pi                         # Calculate true wind direction
    if data_m['10 metre V wind component'][i] < 0:
        wind_d = 180*math.atan(data_m['10 metre U wind component'][i]/data_m['10 metre V wind component'][i])/math.pi + 180
    if data_m['10 metre U wind component'][i] < 0 and data_m['10 metre V wind component'][i] > 0:
        wind_d = 180*math.atan(data_m['10 metre U wind component'][i]/data_m['10 metre V wind component'][i])/math.pi + 360
    if data_m['10 metre U wind component'][i] == 0 and data_m['10 metre V wind component'][i] > 0:
        wind_d = 0
    if data_m['10 metre U wind component'][i] == 0 and data_m['10 metre V wind component'][i] < 0:
        wind_d = 180
    if data_m['10 metre U wind component'][i] > 0 and data_m['10 metre V wind component'][i] == 0:
        wind_d = 90
    if data_m['10 metre U wind component'][i] < 0 and data_m['10 metre V wind component'][i] == 0:
        wind_d = 270
    if data_m['10 metre U wind component'][i] == 0 and data_m['10 metre V wind component'][i] == 0:
        wind_d = 0
    wind_d_list.append(wind_d)
data_w_new['Wind Direction'] = wind_d_list

# =============================================================================
#             wind_d_r = abs(data_w_new['wind speed'] - data_m['True Course'])
#             for i in range(len(data_m)):                            # Calculate relative wind direction
#                 if wind_d_r[i] < 180:
#                     wind_d_r[i] = 180 - wind_d_r[i]
#                 elif wind_d_r[i] >= 180:
#                     wind_d_r[i] = wind_d_r[i] - 180     
#             data_w_new['Wind Direction Relative'] = wind_d_r
# =============================================================================

data_w_new['Current Speed'] = (data_m['Eastward sea water velocity']**2 + data_m['Northward sea water velocity']**2)**0.5 # Synthetic true current speed

current_d_list = []
for i in range(len(data_m)):
    if data_m['Eastward sea water velocity'][i] > 0 and data_m['Northward sea water velocity'][i] > 0:
        current_d = 180*math.atan(data_m['Eastward sea water velocity'][i]/data_m['Northward sea water velocity'][i])/math.pi                             # Calculate true current direction
    if data_m['Northward sea water velocity'][i] < 0:
        current_d = 180*math.atan(data_m['Eastward sea water velocity'][i]/data_m['Northward sea water velocity'][i])/math.pi + 180
    if data_m['Eastward sea water velocity'][i] < 0 and data_m['Northward sea water velocity'][i] > 0:
        current_d = 180*math.atan(data_m['Eastward sea water velocity'][i]/data_m['Northward sea water velocity'][i])/math.pi + 360
    if data_m['Eastward sea water velocity'][i] == 0 and data_m['Northward sea water velocity'][i] > 0:
        current_d = 0
    if data_m['Eastward sea water velocity'][i] == 0 and data_m['Northward sea water velocity'][i] < 0:
        current_d = 180
    if data_m['Eastward sea water velocity'][i] > 0 and data_m['Northward sea water velocity'][i] == 0:
        current_d = 90
    if data_m['Eastward sea water velocity'][i] < 0 and data_m['Northward sea water velocity'][i] == 0:
        current_d = 270
    if data_m['Eastward sea water velocity'][i] == 0 and data_m['Northward sea water velocity'][i] == 0:
        current_d = 0
    current_d_list.append(current_d)
    
data_w_new['Current Direction'] = current_d_list   # m/s

# =============================================================================
# current_d_r = abs(data_w_new['Current Direction'] - data_m['HEADING (deg)'])           # Calculate relative current direction
# for i in range(len(data_m)): 
#     if current_d_r[i]< 180:
#         current_d_r[i] = 180 - current_d_r[i]
#     elif current_d_r[i]>= 180:
#         current_d_r[i] = current_d_r[i]- 180
# data_w_new['Current Direction Relative'] = current_d_r
# data_w_new['Current Direction (kn)'] = data_w_new['Current Speed']/0.51444444
# =============================================================================

data_w_new['Swell Height']    = data_m['Significant height of total swell']
data_w_new['Swell Direction'] = data_m['Mean direction of total swell']
data_w_new['Swell Period']    = data_m['Mean period of total swell']

data_w_new['Wind Wave Heigh']     = data_m['Significant height of wind waves']
data_w_new['Wind Wave Direction'] = data_m['Mean direction of wind waves']
data_w_new['Wind Wave Period']    = data_m['Mean period of wind waves']

# =============================================================================
# for i in range(len(data_m)):
#     if data_w_new['Wind Wave Direction'][i] <= 180:
#         data_w_new['Wind Wave Direction'][i] = data_w_new['Wind Wave Direction'][i]+180
#     elif data_w_new['Wind Wave Direction'][i] > 180:
#         data_w_new['Wind Wave Direction'][i] = data_w_new['Wind Wave Direction'][i]-180
# data['Wind Wave Direction Relative'] = 
# 
# wave_p = 3.86*(Hs**0.5)
# relative_d_s = abs(data_w_new['Wave Direction'][i] - data_m['True Course'][i])                          # Calculate relative wave direction
#             if relative_d_s > 180:
#                 relative_d_s = 360 - relative_d_s
# =============================================================================

data_w_new['Wind Wave and Swell Height']     = data_m['Significant height of combined wind waves and swell']
data_w_new['Wind Wave and Swell Direction']  = data_m['Mean wave direction']
data_w_new['Wind Wave and Swell Period']     = data_m['Mean wave period']
   
data_w_new['Fuel consumption rate (MT/day)'] = data_m['Fuel consumption rate (MT/day)']

data_w_new.to_excel(path_save, index=None)
