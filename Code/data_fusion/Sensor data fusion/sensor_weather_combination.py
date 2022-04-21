# -*- coding: utf-8 -*-
"""
Created on Fri Aug 27 03:19:56 2021

@author: YY_Chen
"""


import os
import math
# import lon_lat
import itertools
import pandas as pd
import datetime as dt


from pyecharts import options as opts 
from pyecharts.charts import Geo, Map3D
from math import radians, cos, sin, asin, sqrt
from pyecharts.globals import ChartType, SymbolType

# data path
path_rep  = './data_s_selection/Ship_S5_Sensor_Data_Selection.xlsx'
path_wea  = './data_o_combination/Ship_S5_OW_OC_Combinattion.xlsx' 
path_save = './data_management/Ship_S5_Sensor_Weather_Combinattion.xlsx' 

# read data
data_rep  = pd.read_excel(path_rep)
data_wea  = pd.read_excel(path_wea)

# drop nan
data_rep  = data_rep.dropna(axis=0, how='any')


data_w_new = pd.DataFrame()

# copy data
data_o = data_wea.copy()

# change data format
data_rep['Current GMT Dttm'] = pd.to_datetime(data_rep['TIME'], format='%Y-%m-%d')
data_wea['Current GMT Dttm'] = pd.to_datetime(data_wea['Current GMT Dttm'], format='%Y-%m-%d')

# merge data
data_m = pd.merge(data_rep, data_wea, on='Current GMT Dttm', how='inner')


data_w_new['Current GMT Dttm']           = data_m['Current GMT Dttm']
data_w_new['GROUND SPEED (kn)']          = data_m['GROUND SPEED (kn)']
data_w_new['TRIM ACTURAL']               = data_m['TRIM ACTUAL (m)']
data_w_new['DRAFT MEAN (m)']             = data_m['DRAFT MEAN (m)']
# data_w_new['WIND DIRECTION (ABS) (deg)'] = data_m['WIND DIRECTION (ABS) (deg)']
data_w_new['WIND DIRECTION (REL) (deg)'] = data_m['WIND DIRECTION (REL) (deg)']
# data_w_new['WIND SPEED (ABS) (kn)']      = data_m['WIND SPEED (ABS) (kn)']
data_w_new['WIND SPEED (REL) (kn)']      = data_m['WIND SPEED (REL) (kn)']
data_w_new['Water Temperature']          = data_m['Sea surface temperature']-273.15

           
data_w_new['Wind Speed (Abs)'] = (data_m['10 metre U wind component']**2 + data_m['10 metre V wind component']**2)**0.5

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
data_w_new['Wind Direction (Abs)'] = wind_d_list

wind_speed_rel_list = []
wind_direction_deg_rel_list = []
Head = data_m['HEADING (deg)'] 
Wind_direction_deg = data_w_new['Wind Direction (Abs)']
for i in range(len(data_m)):
    Wind_direction_deg_rel = abs(Wind_direction_deg[i] - Head[i])
    if Wind_direction_deg_rel < 180:
       Wind_direction_deg_rel = 180 - Wind_direction_deg_rel
       wind_speed = sqrt(data_w_new['Wind Speed (Abs)'][i]**2+data_m['GROUND SPEED (kn)'][i]**2-2*data_w_new['Wind Speed (Abs)'][i]*data_m['GROUND SPEED (kn)'][i]*cos(Wind_direction_deg_rel/2)) 
    elif Wind_direction_deg_rel > 180:
       Wind_direction_deg_rel = Wind_direction_deg_rel - 180
       wind_speed = sqrt(data_w_new['Wind Speed (Abs)'][i]**2+data_m['GROUND SPEED (kn)'][i]**2-2*data_w_new['Wind Speed (Abs)'][i]*data_m['GROUND SPEED (kn)'][i]*cos(Wind_direction_deg_rel/2)) 
    wind_speed_rel_list.append(wind_speed)
    wind_direction_deg_rel_list.append(Wind_direction_deg_rel) 
data_w_new['Wind Speed (Rel)'] = wind_speed_rel_list
data_w_new['Wind Direction (Rel)'] = wind_direction_deg_rel_list


data_w_new['Current Speed (Abs)'] = (data_m['Eastward sea water velocity']**2 + data_m['Northward sea water velocity']**2)**0.5 # Synthetic true current speed

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
data_w_new['Current Direction (Abs)'] = current_d_list   # m/s


current_speed_rel_list = []
current_direction_deg_rel_list = []
Head = data_m['HEADING (deg)'] 
Current_direction_deg = data_w_new['Current Direction (Abs)']
for i in range(len(data_m)):
    Current_direction_deg_rel = abs(Current_direction_deg[i] - Head[i])
    if Current_direction_deg_rel < 180:
      Current_direction_deg_rel = 180 -Current_direction_deg_rel
      current_speed = sqrt(data_w_new['Current Speed (Abs)'][i]**2+data_m['GROUND SPEED (kn)'][i]**2-2*data_w_new['Current Speed (Abs)'][i]*data_m['GROUND SPEED (kn)'][i]*cos(Current_direction_deg_rel/2)) 
    elif Current_direction_deg_rel > 180:
      Current_direction_deg_rel = Current_direction_deg_rel - 180
      current_speed = sqrt(data_w_new['Current Speed (Abs)'][i]**2+data_m['GROUND SPEED (kn)'][i]**2-2*data_w_new['Current Speed (Abs)'][i]*data_m['GROUND SPEED (kn)'][i]*cos(Current_direction_deg_rel/2)) 
    current_speed_rel_list.append(current_speed)
    current_direction_deg_rel_list.append(Current_direction_deg_rel) 
data_w_new['Current Speed (Rel)'] = current_speed_rel_list
data_w_new['Current Direction (Rel)'] =current_direction_deg_rel_list

# data_w_new['Current Direction Relative'] = current_d_r
# cata_w_new['Current Direction (kn)'] = data_w_new['Current Speed']/0.51444444


data_w_new['Swell Height']    = data_m['Significant height of total swell']
data_w_new['Swell Direction (Abs)'] = data_m['Mean direction of total swell']
data_w_new['Swell Period']    = data_m['Mean period of total swell']

swell_direction_deg_rel_list = []
Head = data_m['HEADING (deg)'] 
Swell_direction_deg = data_w_new['Swell Direction (Abs)']
for i in range(len(data_m)):
    Swell_direction_deg_rel = abs(Swell_direction_deg[i] - Head[i])
    if Swell_direction_deg_rel < 180:
      Swell_direction_deg_rel = 180 -Swell_direction_deg_rel
    elif Swell_direction_deg_rel > 180:
      Swell_direction_deg_rel = Swell_direction_deg_rel - 180
    swell_direction_deg_rel_list.append(Swell_direction_deg_rel) 
data_w_new['Swell Direction (Rel)'] = swell_direction_deg_rel_list


data_w_new['Wind Wave Heigh']     = data_m['Significant height of wind waves']
data_w_new['Wind Wave Direction (Abs)'] = data_m['Mean direction of wind waves']
data_w_new['Wind Wave Period']    = data_m['Mean period of wind waves']

wind_wave_direction_deg_rel_list = []
Head = data_m['HEADING (deg)'] 
Wind_wave_direction_deg = data_w_new['Wind Wave Direction (Abs)']
for i in range(len(data_m)):
    Wind_wave_direction_deg_rel = abs(Wind_wave_direction_deg[i] - Head[i])
    if Wind_wave_direction_deg_rel < 180:
      Wind_wave_direction_deg_rel = 180 - Wind_wave_direction_deg_rel
    elif Wind_wave_direction_deg_rel > 180:
      Wind_wave_direction_deg_rel = Wind_wave_direction_deg_rel - 180
    wind_wave_direction_deg_rel_list.append(Wind_wave_direction_deg_rel) 
data_w_new['Wind Wave Direction (Rel)'] = wind_wave_direction_deg_rel_list


data_w_new['Wind Wave and Swell Height']    = data_m['Significant height of combined wind waves and swell']
data_w_new['Wind Wave and Swell Direction (Abs)'] = data_m['Mean wave direction']
data_w_new['Wind Wave and Swell Period']    = data_m['Mean wave period']

wind_wave_swell_direction_deg_rel_list = []
Head = data_m['HEADING (deg)'] 
Wind_wave_swell_direction_deg = data_w_new['Wind Wave and Swell Direction (Abs)']
for i in range(len(data_m)):
    Wind_wave_swell_direction_deg_rel = abs(Wind_wave_swell_direction_deg[i] - Head[i])
    if Wind_wave_swell_direction_deg_rel < 180:
      Wind_wave_swell_direction_deg_rel = 180 - Wind_wave_swell_direction_deg_rel
    elif Wind_wave_swell_direction_deg_rel > 180:
      Wind_wave_swell_direction_deg_rel = Wind_wave_swell_direction_deg_rel - 180
    wind_wave_swell_direction_deg_rel_list.append(Wind_wave_swell_direction_deg_rel) 
data_w_new['Wind Wave and Swell Direction (Rel)'] = wind_wave_swell_direction_deg_rel_list
   
data_w_new['ME FO CONSUMPTION (t/d)'] =data_m['ME FO CONSUMPTION (t/d)']

data_w_new.to_excel(path_save, index=None)