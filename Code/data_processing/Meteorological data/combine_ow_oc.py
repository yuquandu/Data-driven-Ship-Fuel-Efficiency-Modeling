# -*- coding: utf-8 -*-
"""
Created on Wed Aug  4 06:53:39 2021

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

# load dataset
path_ow   = './data_o_ow/Ship_S3_Correct_Selection_OW.xlsx'  
path_oc   = './data_o_oc/Ship_S3_Correct_Selection_OC.xlsx'
path_save = './data_o_combination/Ship_S3_OW_OC_Combinattion.xlsx'

# import dataset
data_ow = pd.read_excel(path_ow)
data_oc = pd.read_excel(path_oc)

column_names= ['Current GMT Dttm', 'Longitude', 'Latitude', 
               'Significant height of combined wind waves and swell', 'Mean wave direction', 'Mean wave period',
               'Significant height of wind waves', 'Mean direction of wind waves', 'Mean period of wind waves', 
               'Significant height of total swell', 'Mean direction of total swell', 'Mean period of total swell',
               '10 metre U wind component', '10 metre V wind component', 'Sea surface temperature',
               'Eastward sea water velocity', 'Northward sea water velocity']

# change data format
data_ow['Current GMT Dttm'] = pd.to_datetime(data_ow['Current GMT Dttm']).dt.strftime('%Y-%m-%d %H:%M:%S') 
data_oc['Current GMT Dttm'] = pd.to_datetime(data_ow['Current GMT Dttm']).dt.strftime('%Y-%m-%d %H:%M:%S') 

data_oc_selection = data_oc[['Current GMT Dttm', 'vo', 'uo']]
data_oc_selection.columns = ['Current GMT Dttm', 'Northward sea water velocity', 'Eastward sea water velocity']

# drop dupolcate data
data_ow.drop_duplicates(subset='Current GMT Dttm', keep='first', inplace=True, ignore_index=True)
data_oc_selection.drop_duplicates(subset='Current GMT Dttm', keep='first', inplace=True, ignore_index=True)

data_oc_selection.insert(1, 'Eastward sea water velocity', data_oc_selection.pop('Eastward sea water velocity'))

# merge data
data_combine = pd.merge(data_ow, data_oc_selection, on='Current GMT Dttm', how='inner')

# save data        
data_combine.to_excel(path_save, index=False) 