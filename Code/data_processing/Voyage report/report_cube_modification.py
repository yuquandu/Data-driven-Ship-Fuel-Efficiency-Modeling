# -*- coding: utf-8 -*-
"""
Created on Fri Jul 30 03:50:13 2021

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
path = './data_o_cube/Ship_S1_Correct_Selection_Modification_Cube.xlsx'
path_save_cube = './data_o_cube_modification/Ship_S1_Correct_Selection_Modification_Cube_Modification.xlsx'

# read data
data_o = pd.read_excel(path)

# coay data   
data_clean = data_o.copy()  

data_lon_lat_clean_index = data_clean.index.tolist()

checklist = []
# data_clean_result = pd.DataFrame()
for i in data_lon_lat_clean_index:
#for i in range(2):
    data_lon_lat_clean = data_clean.iloc[i]
    lon_deg_min = data_lon_lat_clean['Longitude']
    lat_deg_min = data_lon_lat_clean['Latitude']
    
    if lon_deg_min == np.nan or lat_deg_min == np.nan:
        print(i)
        
    if lon_deg_min > 180:
        lon_deg_min = 179.9
        data_clean.loc[i,'Longitude'] = '179.9'
    if lon_deg_min < -180:
        lon_deg_min = -179.9
        data_clean.loc[i,'Longitude'] = '-179.9'
        
    is_on_land = globe.is_land(lat_deg_min, lon_deg_min)
    
    if is_on_land == True:
        checklist.append(i)
        
data_clean.to_excel(path_save_cube, index=None)
print('Data saved')
