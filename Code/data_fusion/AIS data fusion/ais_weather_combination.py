# -*- coding: utf-8 -*-
"""
Created on Mon Nov 29 19:52:55 2021

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

# Loading data
path_rep  = './data_a_o_selection_clean/Ship_S3_Ais_Selection_Clean.xlxs'
path_wea  = './data_o_combination/Ship_S3_OW_OC_Combinattion.xlsx' 
path_save = './data_management/Ship_S3_AIS_Weather_Combination.xlxs' 

# read data
data_o_rep = pd.read_excel(path_rep)
data_o_wea = pd.read_excel(path_wea)

data_o_rep['Current GMT Dttm'] = pd.to_datetime(data_o_rep['Current GMT Dttm'], format='%Y-%m-%d').dt.date
data_o_wea['Current GMT Dttm'] = pd.to_datetime(data_o_wea['Current GMT Dttm'], format='%Y-%m-%d').dt.date

# data selection
data_o_rep_s = data_o_rep[['Current GMT Dttm', 'HEADING']]

# data merge
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

columns_t = ['Current GMT Dttm', 'Speed Made Good (Kts)', 'Vessel Trim (Mtrs)', 'Vsl Displacement', 'Water Temperature', 
             'Wind Speed', 'Relative Wind Direction', 
             'Current Speed', 'Relative Current Direction', 
             'Swell Height', 'Relative Swell Direction', 'Swell Period', 
             'Wind Wave Heigh', 'Relative Wind Wave Direction', 'Wind Wave Period', 
             'Wind Wave and Swell Height', 'Relative Wind Wave and Swell Direction', 'Wind Wave and Swell Period',
             'Fuel consumption rate (MT/day)']

data_o_s = data_o[columns_t]

data_o_s.to_excel(path_save, index=False)
   



