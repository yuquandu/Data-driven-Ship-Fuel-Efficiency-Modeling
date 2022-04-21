# -*- coding: utf-8 -*-
"""
Created on Thu Aug  5 19:39:21 2021

@author: YY_Chen
"""

import os
import math
import lon_lat
import itertools
import pandas as pd
import datetime as dt

from pyecharts import options as opts 
from pyecharts.charts import Geo, Map3D
from math import radians, cos, sin, asin, sqrt
from pyecharts.globals import ChartType, SymbolType


# dataset path
path_rep = './data_o_selection/Ship_S1_Correct_Selection.xlsx'  
path_save = './data_o_modification/Ship_S1_Correct_Selection_Modification.xlsx'

# read dataset
data_rep = pd.read_excel(path_rep)

# data_clean_result = pd.DataFrame()
# lon and lat correct
data_clean_new = []
data_clean_rep_index = data_rep.index.tolist()
for i in data_clean_rep_index:
    lon_deg_min = data_rep['Longitude (deg)'][i]+(data_rep['Longitude (min)'][i]/60)
    if lon_deg_min > 179.9:
        lon_deg_min = 179.9
    lat_deg_min = data_rep['Latitude (deg)'][i]+(data_rep['Latitude (min)'][i]/60)
    if lat_deg_min > 89.9:
        lat_deg_min = 89.9
      
    if data_rep['Longitude Dir'][i] == 'W':
        lon_deg_min = -lon_deg_min
    if data_rep['Latitude Dir'][i] == 'S':
        lat_deg_min = -lat_deg_min
    
    data_rep_time = pd.to_datetime(data_rep['Current GMT Dttm'][i]) 
    data_clean_new.append([data_rep_time, lon_deg_min, lat_deg_min]) 

# select dataset
data_rep_selection = pd.DataFrame(data_clean_new, columns=['Current GMT Dttm', 'LON', 'LAT'])          
data_rep_v = data_rep[['Current GMT Dttm', 'True Course', 'Speed Made Good (Kts)']]    

# merge dataset
data_rep_selection = pd.merge(data_rep_selection, data_rep_v, on='Current GMT Dttm')

# copy dataset   
data_clean = data_rep_selection.copy()         
date_strs =  data_clean['Current GMT Dttm'].dt.date

# Calculates the difference of a Dataframe element compared with another element in the Dataframe (default is element in previous row).
data_clean['diff_f'] = date_strs.diff()
data_clean['diff_b'] = date_strs.diff(-1)
   
# change data format
for i in range(len(data_clean)):
    data_clean['diff_f'][i]=data_clean['diff_f'][i].total_seconds()/3600/24
    data_clean['diff_b'][i]=data_clean['diff_b'][i].total_seconds()/3600/24
 
    
d1 = data_clean[(data_clean['diff_f'].isnull()) & (data_clean['diff_b'] == -1) | ((data_clean['diff_f'] > 1) & (data_clean['diff_b'] == -1))]
d2 = data_clean[(data_clean['diff_f'] == 1) & (data_clean['diff_b'].isnull()) | (data_clean['diff_f'] == 1) & (data_clean['diff_b'] < -1)]

d3 = data_clean[((data_clean['diff_f'].isnull()) & (data_clean['diff_b'] < -1)) | ((data_clean['diff_f'] > 1) & (data_clean['diff_b'] < -1)) | ((data_clean['diff_f'] > 1) & (data_clean['diff_b'].isnull()))]

d1.index = range(d1.shape[0])
d2.index = range(d2.shape[0])
d = pd.merge(d1[['Current GMT Dttm']], d2[['Current GMT Dttm']], left_index=True, right_index=True)        

data_rep_modification_select = []
for j in range(len(d)):
    date_s = d['Current GMT Dttm_x'][j]
    date_e = d['Current GMT Dttm_y'][j] 
    
    data_rep_modification = data_rep_selection[(data_rep['Current GMT Dttm'] >= date_s) & (data_rep_selection['Current GMT Dttm'] <= date_e)]
    data_rep_modification.sort_values(by='Current GMT Dttm', ignore_index=True , inplace=True)
        
    for m in range(len(data_rep_modification)-1):
        inter_t = (data_rep_modification['Current GMT Dttm'][m+1]-data_rep_modification['Current GMT Dttm'][m]).total_seconds()/3600
        data_t  = pd.date_range(start=data_rep_modification['Current GMT Dttm'][m], periods=inter_t, freq='1H')
        
        # Convert decimal degrees to radians
        lon1 = data_rep_modification['LON'][m]
        lat1 = data_rep_modification['LAT'][m]
        lon2 = data_rep_modification['LON'][m+1]
        lat2 = data_rep_modification['LAT'][m+1]
        
        lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
        # haversine formulation
        dlon = lon2 - lon1 
        dlat = lat2 - lat1 
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a)) 
        r = 6371 
        distance = c * r * 1000

        location = []                   
        data_dis_ave = distance/inter_t   
        for n in range(int(inter_t)):                                                      
            location.append(lon_lat.computerThatLonLat(data_rep_modification['LON'][m], data_rep_modification['LAT'][m], data_rep_modification['True Course'][m], data_dis_ave*n))
        
        location = pd.DataFrame(location, columns=['LON', 'LAT'])
        
        data_t = pd.DataFrame(data_t)
        data_t.columns = ['Current GMT Dttm']
        location.reset_index(drop=True, inplace=True)
        data_rep_modification_select.append(pd.concat([data_t, location], axis=1, ignore_index=False))
print('success')            
 
             
for k in d3.index.to_list():
    data_k = d3['Current GMT Dttm'][k]
    data_rep_modification_select.append(data_rep_selection[data_rep_selection['Current GMT Dttm'] == data_k])

data_rep_clean = pd.concat(data_rep_modification_select, ignore_index=True)
data_rep_clean_select = pd.concat([data_rep_clean, data_rep_selection], axis=0, ignore_index=True)            
data_rep_clean_select = data_rep_clean_select.drop_duplicates(['Current GMT Dttm'])
data_rep_clean_select.sort_values(by='Current GMT Dttm', inplace=True)

data_rep_clean_select.to_excel(path_save, index=False)


