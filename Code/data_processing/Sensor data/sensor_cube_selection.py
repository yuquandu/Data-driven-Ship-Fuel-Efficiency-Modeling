# -*- coding: utf-8 -*-
"""
Created on Sun Aug 22 22:46:18 2021

@author: YY_Chen
"""

import pandas as pd
import numpy as np
import openpyxl
import datetime
import math
import netCDF4 as nc
from bisect import bisect

# load sensor data
original_sheet = pd.read_excel('./Ship_S5_Sensor_Data.xlsx')    # Read Excel table

select_col = ['TIME', 'POSITION', 'COURSE (deg)', 'HEADING (deg)', 'GROUND SPEED (kn)', 'WATER SPEED (kn)',
              'ME FO CONSUMPTION (t/d)', 'ME FO MASS FLOW (kg/h)', 'ME SHAFT POWER', 'ME SHAFT RPM',
              'SFOC ISO (g/kWh)', 'SFOC MEASURED (g/kWh)', 'TRIM ACTUAL (m)', 
              'DRAFT AFT', 'DRAFT FWD', 'DRAFT MID (P)', 'DRAFT MID (S)',
              'WIND DIRECTION (ABS) (deg)', 'WIND DIRECTION (REL) (deg)', 'WIND SPEED (ABS) (kn)', 'WIND SPEED (REL) (kn)']

# Import data table
original_data = pd.DataFrame(original_sheet)                                   
select_data = original_data[select_col]

# Remove empty values
select_data = select_data.dropna(axis = 0, how = 'any', thresh = None, subset = select_col)  

# Reset index   
select_data = select_data.reset_index(drop = True)                             
print("data length-1:", len(select_data))

# Delete non-data rows
for i in range(0, len(select_data)):
    if isinstance(select_data['GROUND SPEED (kn)'][i],str) or isinstance(select_data['ME FO CONSUMPTION (t/d)'][i],str):
        print("Index of invalid data:", i, select_data['GROUND SPEED (kn)'][i])
        select_data = select_data.drop([i])
select_data = select_data.reset_index(drop = True)                             # Reset index
print("data length-2:", len(select_data))

select_data[['DRAFT AFT', 'DRAFT FWD']] = select_data[['DRAFT AFT', 'DRAFT FWD']].astype(float)

select_data['DRAFT MEAN (m)'] = None
for i in range(len(select_data)):
    select_data['DRAFT MEAN (m)'][i] = (select_data['DRAFT AFT'][i] + select_data['DRAFT FWD'][i])/2

c_col = ['COURSE (deg)','HEADING (deg)','GROUND SPEED (kn)','WATER SPEED (kn)',
         'ME FO CONSUMPTION (t/d)','ME FO MASS FLOW (kg/h)','ME SHAFT POWER','ME SHAFT RPM',
         'SFOC ISO (g/kWh)','SFOC MEASURED (g/kWh)','TRIM ACTUAL (m)','DRAFT AFT','DRAFT FWD',
         'DRAFT MEAN (m)','DRAFT MID (P)','DRAFT MID (S)','WIND DIRECTION (ABS) (deg)',
         'WIND DIRECTION (REL) (deg)','WIND SPEED (ABS) (kn)','WIND SPEED (REL) (kn)']

# Data type converted to float
select_data[c_col] = select_data[c_col].astype(float)                          

# Delete low quality data
select_data = select_data.drop(select_data[select_data['GROUND SPEED (kn)'] < 12].index)
select_data = select_data.drop(select_data[select_data['GROUND SPEED (kn)'] > 26].index)
select_data = select_data.drop(select_data[select_data['WATER SPEED (kn)'] < 12].index)
select_data = select_data.drop(select_data[select_data['WATER SPEED (kn)'] > 26].index)
select_data = select_data.drop(select_data[select_data['ME FO CONSUMPTION (t/d)'] < 30].index)
select_data = select_data.drop(select_data[select_data['ME FO CONSUMPTION (t/d)'] > 160].index)
select_data = select_data.drop(select_data[select_data['ME FO MASS FLOW (kg/h)'] < 1250].index)
select_data = select_data.drop(select_data[select_data['ME FO MASS FLOW (kg/h)'] > 6666.67].index)
select_data = select_data.drop(select_data[select_data['ME SHAFT RPM'] <= 40].index)
select_data = select_data.drop(select_data[select_data['ME SHAFT RPM'] >= 100].index)
select_data = select_data.drop(select_data[select_data['SFOC MEASURED (g/kWh)'] >= 250].index)
select_data = select_data.drop(select_data[select_data['SFOC MEASURED (g/kWh)'] <= 160].index)
select_data = select_data.drop(select_data[select_data['DRAFT MEAN (m)'] <= 5].index)
select_data = select_data.drop(select_data[select_data['DRAFT MEAN (m)'] >= 20].index)
select_data = select_data.drop(select_data[select_data['TRIM ACTUAL (m)'] <= -5].index)
select_data = select_data.drop(select_data[select_data['TRIM ACTUAL (m)'] >= 5].index)
select_data = select_data.drop(select_data[select_data['WIND DIRECTION (ABS) (deg)'] < 0].index)
select_data = select_data.drop(select_data[select_data['WIND DIRECTION (REL) (deg)'] < 0].index)
select_data = select_data.drop(select_data[select_data['WIND DIRECTION (ABS) (deg)'] > 360].index)
select_data = select_data.drop(select_data[select_data['WIND DIRECTION (REL) (deg)'] > 360].index)
select_data = select_data.drop(select_data[select_data['WIND SPEED (ABS) (kn)'] < 0].index)
select_data = select_data.drop(select_data[select_data['WIND SPEED (REL) (kn)'] < 0].index)
select_data = select_data.reset_index(drop = True)                             # Reset index
print("data length-3:", len(select_data))

# Deduplicate data
select_data.drop_duplicates(subset = ["GROUND SPEED (kn)", "WATER SPEED (kn)", "DRAFT MEAN (m)",
                                      "TRIM ACTUAL (m)", "WIND DIRECTION (ABS) (deg)", "WIND DIRECTION (REL) (deg)",
                                      "WIND SPEED (ABS) (kn)", "WIND SPEED (REL) (kn)", "ME FO CONSUMPTION (t/d)"], keep = 'first', inplace = True)                    

# Reset index
select_data = select_data.reset_index(drop = True)                             
print("data length-4:", len(select_data))

select_data['DRAFT MEAN (m)'] = np.round(select_data['DRAFT MEAN (m)'], 2)                       # Accurate to 2 decimal places  
select_data['Latitude']  = select_data['POSITION'].map(lambda x:x.split(';')[0])
select_data['Latitude (deg)'] = select_data['Latitude'].map(lambda x:x.split('°')[0])
select_data['Latitude (min)'] = select_data['Latitude'].map(lambda x:x.split('°')[1].split('\'')[0])
select_data['Latitude Dir'] = select_data['Latitude'].map(lambda x:x.split('°')[1].split('\'')[1])
select_data['Longitude'] = select_data['POSITION'].map(lambda x:x.split(';')[1])
select_data['Longitude (deg)'] = select_data['Longitude'].map(lambda x:x.split('°')[0])
select_data['Longitude (min)'] = select_data['Longitude'].map(lambda x:x.split('°')[1].split('\'')[0])
select_data['Longitude Dir'] = select_data['Longitude'].map(lambda x:x.split('°')[1].split('\'')[1])


location = ['Latitude (deg)', 'Latitude (min)', 'Longitude (deg)', 'Longitude (min)']
select_data[location] = select_data[location].astype(float)
select_data.to_excel('./Ship_S5_Sensor_Data_Selection.xlsx', index=False)


