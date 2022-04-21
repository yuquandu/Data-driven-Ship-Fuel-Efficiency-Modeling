# -*- coding: utf-8 -*-
"""
Created on Fri Jul 30 03:39:49 2021

@author: YY_Chen
"""

import os
import math
#import lon_lat
import itertools
import pandas as pd
import datetime as dt


from pyecharts import options as opts 
from pyecharts.charts import Geo, Map3D
from pyecharts.globals import ChartType, SymbolType


# data path
path = './data_o_modification/Ship_S1_Correct_Selection_Modification.xlsx'
path_save = './data_o_cube/Ship_S1_Correct_Selection_Modification_Cube.xlsx'


# read xlsx file
data_o = pd.read_excel(path) 

# Null and invalid value elimination  
col_subset = ['Current GMT Dttm','LON', 'LAT'] 

column_names= ['Current GMT Dttm', 'Longitude', 'Latitude', 
               'Significant height of combined wind waves and swell', 'Mean wave direction', 'Mean wave period',
               'Significant height of wind waves', 'Mean direction of wind waves', 'Mean period of wind waves', 
               'Significant height of total swell', 'Mean direction of total swell', 'Mean period of total swell',
               '10 metre U wind component', '10 metre V wind component', 'Sea surface temperature',
               'Eastward sea water velocity', 'Northward sea water velocity']


data = pd.DataFrame(columns=column_names)
data[['Current GMT Dttm', 'Longitude', 'Latitude']] = data_o[col_subset]

data.to_excel(path_save, index=None)
print('Data saved')

