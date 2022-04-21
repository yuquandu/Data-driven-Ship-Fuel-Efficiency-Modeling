# -*- coding: utf-8 -*-
"""
Created on Fri Jul 30 00:44:21 2021

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
path = './data_o_correct/Ship_S1_Correct.xlsx'
path_save = './data_o_selection/Ship_S1_Correct_Selection.xlsx'


data_o = pd.read_excel(path)
   
data_clean = data_o.copy()  

# Null and invalid value elimination  
col_subset = ['Current GMT Dttm','Swell Dir','Swell Ht (mtr)','Sea Current','Sea Curent Dir',
              'Wind Force','Wind Dir','Sea Water Temp','Speed Made Good (Kts)','Vessel Trim (Mtrs)',
              'Computed Mid Draft','M-Eng HFO Qty Consumed','Total Elapsed Hrs','Dist Made Good','Total Propulsion Power (KW)',
              'Vsl Displacement','Latitude (deg)','Latitude (min)','Latitude Dir','Longitude (deg)',
              'Longitude (min)','Longitude Dir','Mode Code','True Course']  

data_clean= data_clean.dropna(axis = 0, how = 'any', thresh = None, subset = col_subset)
data_clean= data_clean.drop(data_clean[data_clean['Swell Dir'] == 'Nil'].index)
data_clean= data_clean.drop(data_clean[data_clean['Sea Curent Dir'] == 'Nil'].index)
data_clean= data_clean.drop(data_clean[data_clean['Wind Dir'] == 'Nil'].index)

# Elimination of low and non-steady-state data
data_clean= data_clean.drop(data_clean[data_clean['Mode Code'] != 'Sea'].index)
data_clean= data_clean.drop(data_clean[data_clean['Speed Made Good (Kts)'] < 12].index)
data_clean= data_clean.drop(data_clean[data_clean['Speed Made Good (Kts)'] > 30].index)
data_clean= data_clean.drop(data_clean[data_clean['Total Elapsed Hrs'] < 10].index)
data_clean= data_clean.drop(data_clean[data_clean['M-Eng HFO Qty Consumed'] <= 0].index)
data_clean= data_clean.drop(data_clean[data_clean['M-Eng LSFO Qty Consumed'] > 0].index)
data_clean= data_clean.drop(data_clean[data_clean['M-Eng LSGO Qty Consumed'] > 0].index)
data_clean= data_clean.drop(data_clean[data_clean['M-Eng MGO Qty Consumed'] > 0].index)    
data_clean= data_clean.drop(data_clean[data_clean['M-Eng ULSGO Qty Consumed'] > 0].index)


# Current direction transformation
data_clean['Sea Curent Dir'].replace('E', 1, inplace = True)               # Head
data_clean['Sea Curent Dir'].replace(['D','F'], 2, inplace = True)         # Bow
data_clean['Sea Curent Dir'].replace(['C','G'], 3, inplace = True)         # Beam
data_clean['Sea Curent Dir'].replace(['B','H'], 4, inplace = True)         # Stern
data_clean['Sea Curent Dir'].replace('A', 5, inplace=True)                 # Following
    
# Surge direction and wind direction transformation
data_clean.replace('A', 1, inplace=True)                                   # Following
data_clean.replace(['B','H'], 2, inplace=True)                             # Stern
data_clean.replace(['C','G'], 3, inplace=True)                             # Beam
data_clean.replace(['D','F'], 4, inplace=True)                             # Bow
data_clean['Swell Dir'].replace('E', 5, inplace=True)                      # Head
data_clean['Wind Dir'].replace('E', 5, inplace=True)                       # Head

# Delete low sulfur oil column
data_clean.drop(['M-Eng LSFO Qty Consumed','M-Eng LSGO Qty Consumed',
                 'M-Eng MGO Qty Consumed','M-Eng ULSGO Qty Consumed'],axis = 1, inplace = True)

# Calculate the daily fuel consumption of the main engine
# A column "Fuel consumption rate (MT/day)" was added at the end of the data table.    
data_clean['Fuel consumption rate (MT/day)'] = 24*data_clean['M-Eng HFO Qty Consumed']/data_clean['Total Elapsed Hrs']

data_clean = data_clean.reset_index(drop=True, inplace=False)    

data_clean.to_excel(path_save, index=None)

print('Data saved')
