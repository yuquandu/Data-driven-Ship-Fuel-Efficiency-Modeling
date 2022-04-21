#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jul 17 12:19:40 2021

@author: ychen72
"""

import pandas as pd
import numpy as np
import datetime
import math
import netCDF4 as nc
import openpyxl

# read csv table
data = pd.read_csv('./ship_s1.csv')      

# select columns
column_names = ['u10', 'v10', 'mdts', 'mdww', 'mpts', 'mpww', 'mwd', 'mwp', 'sst', 'swh', 'shts', 'shww']

# import nan as NaN
data[column_names].fillna(value='NaN', axis=1, inplace=True)

# save data
data.to_excel('./ship_s1_new.xlsx')
print('data save')
