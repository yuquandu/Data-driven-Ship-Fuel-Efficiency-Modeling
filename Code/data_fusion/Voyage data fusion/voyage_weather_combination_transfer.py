# -*- coding: utf-8 -*-
"""
Created on Mon Nov 22 19:18:29 2021

@author: YY_Chen
"""

# -*- coding: utf-8 -*-
"""
Created on Sat Nov 13 10:12:43 2021

@author: YY_Chen
"""


import pandas as pd 
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.model_selection import cross_val_score
from hyperopt import fmin, tpe, hp, STATUS_OK, Trials, partial, rand
from xgboost.sklearn import XGBRegressor
import time
import openpyxl
import os


# dataset path
path_rep   = './data_o_selection/Ship_S3_Correct_Selection.xlsx'
path_wea   = './data_o_combination/Ship_S3_OW_OC_Combinattion.xlsx' 
path_save  = './data_management/Ship_S3_Voyage_Weather_Combination_Transfer.xlsx'

# read xlsx files
data_o_rep = pd.read_excel(path_rep)
data_o_wea = pd.read_excel(path_wea)

# =============================================================================
# column_s = data_m_rep.columns
# data_o_rep = data_m_rep[column_s]
# for i in data_m_rep.index:      
#     if isinstance(data_m_rep['Swell Dir'][i], int) == False:
#         print(i)
#         data_o_rep['Swell Dir'][i] = [s[0] for s in data_m_rep['Swell Dir'][i].split()][0]
#     if isinstance(data_o_rep['Sea Curent Dir'][i], int) == False:
#         data_o_rep['Sea Curent Dir'][i] = [s[0] for s in data_m_rep['Sea Curent Dir'][i].split()][0]
#     if isinstance(data_o_rep['Wind Dir'][i], int) == False:
#         data_o_rep['Wind Dir'][i] = [s[0] for s in data_m_rep['Wind Dir'][i].split()][0]
# 
# # Current direction transformation
# data_o_rep['Sea Curent Dir'].replace('E', 1, inplace = True)               # Head
# data_o_rep['Sea Curent Dir'].replace(['D','F'], 2, inplace = True)         # Bow
# data_o_rep['Sea Curent Dir'].replace(['C','G'], 3, inplace = True)         # Beam
# data_o_rep['Sea Curent Dir'].replace(['B','H'], 4, inplace = True)         # Stern
# data_o_rep['Sea Curent Dir'].replace('A', 5, inplace=True)                 # Following
# 
# # Surge direction and wind direction transformation
# data_o_rep.replace('A', 1, inplace=True)                                   # Following
# data_o_rep.replace(['B','H'], 2, inplace=True)                             # Stern
# data_o_rep.replace(['C','G'], 3, inplace=True)                             # Beam
# data_o_rep.replace(['D','F'], 4, inplace=True)                             # Bow
# data_o_rep['Swell Dir'].replace('E', 5, inplace=True)                      # Head
# data_o_rep['Wind Dir'].replace('E', 5, inplace=True)                       # Head
# 
# file_rep_name = filename_rep.split('.')[0]
# data_o_rep.to_excel(path_rep+file_rep_name+'_.xlsx', index=False)
# =============================================================================

wea_selection = ['Current GMT Dttm', 'Speed Made Good (Kts)', 'Vessel Trim (Mtrs)', 'Vsl Displacement', 'Water Temperature', 'Wind Speed', 'Wind Direction',
                 'Swell Height', 'Swell Direction',
                 'Swell Period', 'Wind Wave Heigh', 'Wind Wave Direction',
                 'Wind Wave Period', 'Wind Wave and Swell Height',
                 'Wind Wave and Swell Direction', 'Wind Wave and Swell Period',
                 'Fuel consumption rate (MT/day)']

data_o_wea = data_o_wea[wea_selection]


# change data format
data_o_rep['Current GMT Dttm'] = pd.to_datetime(data_o_rep['Current GMT Dttm'], format='%Y-%m-%d').dt.date
data_o_wea['Current GMT Dttm'] = pd.to_datetime(data_o_wea['Current GMT Dttm'], format='%Y-%m-%d').dt.date

# select data
data_o_rep_s = data_o_rep[['Current GMT Dttm', 'Sea Current', 'Sea Curent Dir', 'True Course']]

# merge data
data_o = pd.merge(data_o_wea, data_o_rep_s, how='left', on=['Current GMT Dttm'])

# data correct
data_o['Relative Wind Direction'] = abs(data_o['Wind Direction'] - data_o['True Course'])                          # Calculate relative wave direction
# data_o['Relative Current Direction'] = abs(data_o['Current Direction'] - data_o['True Course'])
data_o['Relative Swell Direction'] = abs(data_o['Swell Direction'] - data_o['True Course'])
data_o['Relative Wind Wave Direction'] = abs(data_o['Wind Wave Direction'] - data_o['True Course'])
data_o['Relative Wind Wave and Swell Direction'] = abs(data_o['Wind Wave and Swell Direction'] - data_o['True Course'])


for i in data_o.index:
    if data_o['Relative Wind Direction'][i] > 180:
        data_o['Relative Wind Direction'][i] = 360 - data_o['Relative Wind Direction'][i]
# =============================================================================
#     if data_o['Relative Current Direction'][i] > 180:
#         data_o['Relative Current Direction'][i] = 360 - data_o['Relative Current Direction'][i]
# =============================================================================
    if data_o['Relative Swell Direction'][i] > 180:
        data_o['Relative Swell Direction'][i] = 360 - data_o['Relative Swell Direction'][i]
    if data_o['Relative Wind Wave Direction'][i] > 180:
        data_o['Relative Wind Wave Direction'][i] = 360 - data_o['Relative Wind Wave Direction'][i]
    if data_o['Relative Wind Wave and Swell Direction'][i] > 180:
        data_o['Relative Wind Wave and Swell Direction'][i] = 360 - data_o['Relative Wind Wave and Swell Direction'][i]


    # Relative direction conversion
    for i in data_o.index:
        if data_o['Relative Wind Direction'][i] >= 0:
            if data_o['Relative Wind Direction'][i] >= 0 and data_o['Relative Wind Direction'][i] <= 30:
                data_o.loc[i,'Wind Direction'] = 5
            elif data_o['Relative Wind Direction'][i] > 30 and data_o['Relative Wind Direction'][i] <= 60:
                data_o.loc[i,'Wind Direction'] = 4
            elif data_o['Relative Wind Direction'][i] > 60 and data_o['Relative Wind Direction'][i] <= 120:
                data_o.loc[i,'Wind Direction'] = 3
            elif data_o['Relative Wind Direction'][i] > 120 and data_o['Relative Wind Direction'][i] <= 150:
                data_o.loc[i,'Wind Direction'] = 2
            elif data_o['Relative Wind Direction'][i] > 150 and data_o['Relative Wind Direction'][i] <= 180:
                data_o.loc[i,'Wind Direction'] = 1
                
            if data_o['Relative Current Direction'][i] >= 0 and data_o['Relative Current Direction'][i] <= 30:
                data_o.loc[i,'Current Direction'] = 5
            elif data_o['Relative Current Direction'][i] > 30 and data_o['Relative Current Direction'][i] <= 60:
                data_o.loc[i,'Current Direction'] = 4
            elif data_o['Relative Current Direction'][i] > 60 and data_o['Relative Current Direction'][i] <= 120:
                data_o.loc[i,'Current Direction'] = 3
            elif data_o['Relative Current Direction'][i] > 120 and data_o['Relative Current Direction'][i] <= 150:
                data_o.loc[i,'Current Direction'] = 2
            elif data_o['Relative Current Direction'][i] > 150 and data_o['Relative Current Direction'][i] <= 180:
                data_o.loc[i,'Current Direction'] = 1
    
            if data_o['Relative Swell Direction'][i] >= 0 and data_o['Relative Swell Direction'][i] <= 30:
                data_o.loc[i,'Swell Direction'] = 5
            elif data_o['Relative Swell Direction'][i] > 30 and data_o['Relative Swell Direction'][i] <= 60:
                data_o.loc[i,'Swell Direction'] = 4
            elif data_o['Relative Swell Direction'][i] > 60 and data_o['Relative Swell Direction'][i] <= 120:
                data_o.loc[i,'Swell Direction'] = 3
            elif data_o['Relative Swell Direction'][i] > 120 and data_o['Relative Swell Direction'][i] <= 150:
                data_o.loc[i,'Swell Direction'] = 2
            elif data_o['Relative Swell Direction'][i] > 150 and data_o['Relative Swell Direction'][i] <= 180:
                data_o.loc[i,'Swell Direction'] = 1
                
            if data_o['Relative Wind Wave Direction'][i] >= 0 and data_o['Relative Wind Wave Direction'][i] <= 30:
                data_o.loc[i,'Wind Wave Direction'] = 5
            elif data_o['Relative Wind Wave Direction'][i] > 30 and data_o['Relative Wind Wave Direction'][i] <= 60:
                data_o.loc[i,'Wind Wave Direction'] = 4
            elif data_o['Relative Wind Wave Direction'][i] > 60 and data_o['Relative Wind Wave Direction'][i] <= 120:
                data_o.loc[i,'Wind Wave Direction'] = 3
            elif data_o['Relative Wind Wave Direction'][i] > 120 and data_o['Relative Wind Wave Direction'][i] <= 150:
                data_o.loc[i,'Wind Wave Direction'] = 2
            elif data_o['Relative Wind Wave Direction'][i] > 150 and data_o['Relative Wind Wave Direction'][i] <= 180:
                data_o.loc[i,'Wind Wave Direction'] = 1
                
            if data_o['Relative Wind Wave and Swell Direction'][i] >= 0 and data_o['Relative Wind Wave and Swell Direction'][i] <= 30:
                data_o.loc[i,'Wind Wave and Swell Direction'] = 5
            elif data_o['Relative Wind Wave and Swell Direction'][i] > 30 and data_o['Relative Wind Wave and Swell Direction'][i] <= 60:
                data_o.loc[i,'Wind Wave and Swell Direction'] = 4
            elif data_o['Relative Wind Wave and Swell Direction'][i] > 60 and data_o['Relative Wind Wave and Swell Direction'][i] <= 120:
                data_o.loc[i,'Wind Wave and Swell Direction'] = 3
            elif data_o['Relative Wind Wave and Swell Direction'][i] > 120 and data_o['Relative Wind Wave and Swell Direction'][i] <= 150:
                data_o.loc[i,'Wind Wave and Swell Direction'] = 2
            elif data_o['Relative Wind Wave and Swell Direction'][i] > 150 and data_o['Relative Wind Wave and Swell Direction'][i] <= 180:
                data_o.loc[i,'Wind Wave and Swell Direction'] = 1
                                                
    # Wind level conversion
    for i in data_o.index:
        if data_o['Wind Speed'][i] >= 0:
            if data_o['Wind Speed'][i] >= 0 and data_o['Wind Speed'][i] <= 0.2:
                data_o.loc[i,'Wind Speed'] = 0
            if data_o['Wind Speed'][i] > 0.2 and data_o['Wind Speed'][i] <= 1.5:
                data_o.loc[i,'Wind Speed'] = 1
            if data_o['Wind Speed'][i] > 1.5 and data_o['Wind Speed'][i] <= 3.3:
                data_o.loc[i,'Wind Speed'] = 2
            if data_o['Wind Speed'][i] > 3.3 and data_o['Wind Speed'][i] <= 5.4:
                data_o.loc[i,'Wind Speed'] = 3
            if data_o['Wind Speed'][i] > 5.4 and data_o['Wind Speed'][i] <= 7.9:
                data_o.loc[i,'Wind Speed'] = 4
            if data_o['Wind Speed'][i] > 7.9 and data_o['Wind Speed'][i] <= 10.7:
                data_o.loc[i,'Wind Speed'] = 5
            if data_o['Wind Speed'][i] > 10.7 and data_o['Wind Speed'][i] <= 13.8:
                data_o.loc[i,'Wind Speed'] = 6
            if data_o['Wind Speed'][i] > 13.8 and data_o['Wind Speed'][i] <= 17.1:
                data_o.loc[i,'Wind Speed'] = 7
            if data_o['Wind Speed'][i] > 17.1 and data_o['Wind Speed'][i] <= 20.7:
                data_o.loc[i,'Wind Speed'] = 8
            if data_o['Wind Speed'][i] > 20.7 and data_o['Wind Speed'][i] <= 24.4:
                data_o.loc[i,'Wind Speed'] = 9
            if data_o['Wind Speed'][i] > 24.4 and data_o['Wind Speed'][i] <= 28.4:
                data_o.loc[i,'Wind Speed'] = 10
            if data_o['Wind Speed'][i] > 28.4 and data_o['Wind Speed'][i] <= 32.6:
                data_o.loc[i,'Wind Speed'] = 11
            if data_o['Wind Speed'][i] > 32.6:
                data_o.loc[i,'Wind Speed'] = 12   
 
columns = ['Current GMT Dttm', 'Speed Made Good (Kts)', 'Vessel Trim (Mtrs)', 'Vsl Displacement', 'Water Temperature', 
           'Wind Speed', 'Wind Direction', 
           'Sea Current', 'Sea Curent Dir', 
           'Swell Height', 'Relative Swell Direction', 'Swell Period', 
           'Wind Wave Heigh', 'Relative Wind Wave Direction', 'Wind Wave Period', 
           'Wind Wave and Swell Height', 'Relative Wind Wave and Swell Direction', 'Wind Wave and Swell Period',
           'Fuel consumption rate (MT/day)']
   
data_o_s = data_o[columns]

columns_t = ['Current GMT Dttm', 'Speed Made Good (Kts)', 'Vessel Trim (Mtrs)', 'Vsl Displacement', 'Water Temperature', 
             'Wind Speed', 'Relative Wind Direction', 
             'Current Speed', 'Relative Current Direction', 
             'Swell Height', 'Relative Swell Direction', 'Swell Period', 
             'Wind Wave Heigh', 'Relative Wind Wave Direction', 'Wind Wave Period', 
             'Wind Wave and Swell Height', 'Relative Wind Wave and Swell Direction', 'Wind Wave and Swell Period',
             'Fuel consumption rate (MT/day)']

# data_o_s = data_o[columns_t]

data_o_s.columns = columns_t

data_o_s.to_excel(path_save, index=False)




