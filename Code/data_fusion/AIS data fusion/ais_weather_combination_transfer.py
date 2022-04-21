# -*- coding: utf-8 -*-
"""
Created on Mon Nov 29 20:18:29 2021

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

# loading data
path_rep  = './data_a_o_selection_clean/Ship_S3_Ais_Selection_Clean.xlxs'
path_wea  = './data_o_combination/Ship_S3_OW_OC_Combinattion.xlsx' 
path_save = './data_management/Ship_S3_AIS_Weather_Combination_Transfer.xlsx'

# import data
data_o_rep = pd.read_excel(path_rep)
data_o_wea = pd.read_excel(path_wea)

# change data format
data_o_rep['Current GMT Dttm'] = pd.to_datetime(data_o_rep['Current GMT Dttm'], format='%Y-%m-%d').dt.date
data_o_wea['Current GMT Dttm'] = pd.to_datetime(data_o_wea['Current GMT Dttm'], format='%Y-%m-%d').dt.date

# select data
data_o_rep_s = data_o_rep[['Current GMT Dttm', 'HEADING']]

# merge data
data_o = pd.merge(data_o_wea, data_o_rep_s, how='left', on=['Current GMT Dttm'])


data_o['Relative Wind Direction'] = abs(data_o['Wind Direction'] - data_o['HEADING'])                          # Calculate relative wave direction
data_o['Relative Current Direction'] = abs(data_o['Current Direction'] - data_o['HEADING'])
data_o['Relative Swell Direction'] = abs(data_o['Swell Direction'] - data_o['HEADING'])
data_o['Relative Wind Wave Direction'] = abs(data_o['Wind Wave Direction'] - data_o['HEADING'])
data_o['Relative Wind Wave and Swell Direction'] = abs(data_o['Wind Wave and Swell Direction'] - data_o['HEADING'])


for i in data_o.index:
    if data_o['Relative Wind Direction'][i] > 180:
        data_o['Relative Wind Direction'][i] = 360 - data_o['Relative Wind Direction'][i]
    if data_o['Relative Current Direction'][i] > 180:
        data_o['Relative Current Direction'][i] = 360 - data_o['Relative Current Direction'][i]
    if data_o['Relative Swell Direction'][i] > 180:
        data_o['Relative Swell Direction'][i] = 360 - data_o['Relative Swell Direction'][i]
    if data_o['Relative Wind Wave Direction'][i] > 180:
        data_o['Relative Wind Wave Direction'][i] = 360 - data_o['Relative Wind Wave Direction'][i]
    if data_o['Relative Wind Wave and Swell Direction'][i] > 180:
        data_o['Relative Wind Wave and Swell Direction'][i] = 360 - data_o['Relative Wind Wave and Swell Direction'][i]


# Relative wind direction and relative wave direction conversion
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
           'Current Speed', 'Current Direction', 
           'Swell Height', 'Swell Direction', 'Swell Period', 
           'Wind Wave Heigh', 'Wind Wave Direction', 'Wind Wave Period', 
           'Wind Wave and Swell Height', 'Wind Wave and Swell Direction', 'Wind Wave and Swell Period',
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




