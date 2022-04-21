# -*- coding: utf-8 -*-
"""
Created on Sun Aug  1 01:59:47 2021

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
from pyecharts.globals import ChartType, SymbolType

# dataset path
path_rep  = './data_o_selection/Ship_S1_Selection.xlxs'  
path_ais  = './data_a_o_selection/Ship_S1_Ais_Selection.xlxs'  
path_save = './data_a_o_selection_clean/Ship_S1_Ais_Selection_Clean.xlxs'

# read xlxs files
data_rep = pd.read_excel(path_rep)
data_ais = pd.read_excel(path_ais)

# change data format
data_ais['Current GMT Dttm'] = pd.to_datetime(data_ais['Current GMT Dttm'])

# modify lon and lat
# data_clean_result = pd.DataFrame()
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
    
    #lon_deg_min = pd.DataFrame(lon_deg_min, columns=['Longitude'])        
    #lat_deg_min = pd.DataFrame(lat_deg_min, columns=['Latitude']) 
    data_rep_time = pd.to_datetime(data_rep['Current GMT Dttm'][i])       
    data_clean_new.append([data_rep_time, lon_deg_min, lat_deg_min]) 
    
data_rep_selection = pd.DataFrame(data_clean_new, columns=['Current GMT Dttm', 'LON', 'LAT'])
data_rep_v = data_rep[['Current GMT Dttm', 'True Course', 'Speed Made Good (Kts)']]    

# merge dataset 
data_rep_selection = pd.merge(data_rep_selection, data_rep_v, on='Current GMT Dttm')
data_rep_selection['Heading'] = "Null"

data_ais_time = pd.to_datetime(data_ais['Current GMT Dttm'])
data_ais_lv = data_ais[['LON', 'LAT', 'HEADING', 'COURSE']]
data_ais_selection  = pd.concat([data_ais_time, data_ais_lv], axis=1, ignore_index=True)
data_ais_selection.columns=['Current GMT Dttm', 'LON', 'LAT', 'HEADING', 'True Course']

for m in range(len(data_ais)):
    for n in range(len(data_rep_selection)):   
        # data_ais.set_index('Current GMT Dttm', inplace=True)
        if data_ais_selection['Current GMT Dttm'][m] == data_rep_selection['Current GMT Dttm'][n] and (pd.isnull(data_ais_selection['LON'][m]) == True or pd.isnull(data_ais_selection['LAT'][m]) == True):
            data_ais_selection['LON'][m] = data_rep_selection['LON'][n]
            data_ais_selection['LAT'][m] = data_rep_selection['LAT'][n]
            data_ais_selection['HEADING'][m] = data_rep_selection['Heading'][n]
            data_ais_selection['True Course'][m] = data_rep_selection['True Course'][n]
           
data_clean = data_rep_selection.copy()         
date_strs =  data_clean['Current GMT Dttm'].dt.date

# Calculates the difference of a Dataframe element compared with another element in the Dataframe (default is element in previous row).
data_clean['diff_f'] = date_strs.diff()
data_clean['diff_b'] = date_strs.diff(-1)
   
#i_index = []
for i in range(len(data_clean)):
    data_clean['diff_f'][i]=data_clean['diff_f'][i].total_seconds()/3600/24
    data_clean['diff_b'][i]=data_clean['diff_b'][i].total_seconds()/3600/24
    
d1 = data_clean[(data_clean['diff_f'].isnull()) & (data_clean['diff_b'] == -1) | ((data_clean['diff_f'] > 1) & (data_clean['diff_b'] == -1))]
d2 = data_clean[(data_clean['diff_f'] == 1) & (data_clean['diff_b'].isnull()) | ((data_clean['diff_f'] == 1) & (data_clean['diff_b'] < -1))]

d3 = data_clean[((data_clean['diff_f'].isnull()) & (data_clean['diff_b'] < -1)) | ((data_clean['diff_f'] > 1) & (data_clean['diff_b'] < -1)) | ((data_clean['diff_f'] > 1) & (data_clean['diff_b'].isnull()))]

d1.index = range(d1.shape[0])
d2.index = range(d2.shape[0])
d = pd.merge(d1[['Current GMT Dttm']], d2[['Current GMT Dttm']], left_index=True, right_index=True)
#d['tong'] = d['time_y'] - d['time_x']         
     
data_ais_selection_clean = []
for j in range(len(d)):
    date_s = d['Current GMT Dttm_x'][j]
    date_e = d['Current GMT Dttm_y'][j]                                                    
    data_ais_selection_clean.append(data_ais_selection[(data_ais_selection['Current GMT Dttm'] >= date_s) & (data_ais_selection['Current GMT Dttm'] <= date_e)])             

for k in d3.index.to_list():
    #print(k)
    data_k = d3['Current GMT Dttm'][k]
    data_ais_selection_clean.append(data_ais_selection[data_ais_selection['Current GMT Dttm'] == data_k])
 
data_ais_selection_clean = pd.concat(data_ais_selection_clean, ignore_index=True) 
data_ais_selection_clean = data_ais_selection_clean.drop_duplicates(['Current GMT Dttm'])
data_ais_selection_clean.sort_values(by='Current GMT Dttm', inplace=True)
data_ais_selection_clean.to_excel(path_save, index=False)



