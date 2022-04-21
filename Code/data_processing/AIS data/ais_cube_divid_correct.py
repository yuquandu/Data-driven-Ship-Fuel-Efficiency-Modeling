# -*- coding: utf-8 -*-
"""
Created on Fri Jul 30 13:54:29 2021

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
path_rep  = './data_o_selection/Ship_S1_Correct_Selection.xlsx'   
path_ais  = './data_a_o_selection/Ship_S1_AIS_Selection.xlsx'
path_save = './data_a_o_modification/Ship_S1_AIS_Selection_Modification.xlsx'

# read xlxs files
data_rep = pd.read_excel(path_rep)
data_ais = pd.read_excel(path_ais)  

# change data format
data_ais['Current GMT Dttm'] = pd.to_datetime(data_ais['Current GMT Dttm'], format='%Y-%m-%d %H') 
data_rep['Current GMT Dttm'] = pd.to_datetime(data_rep['Current GMT Dttm'], format='%Y-%m-%d %H') 

# change lon and lat format                            
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
    #data_rep_time = pd.to_datetime(data_rep['Current GMT Dttm'][i])
    data_rep_time = pd.to_datetime(data_rep['Current GMT Dttm'][i], format='%Y-%m-%d %H:00:00')       
    data_clean_new.append([data_rep_time, lon_deg_min, lat_deg_min]) 
    
data_rep_selection = pd.DataFrame(data_clean_new, columns=['Current GMT Dttm', 'LON', 'LAT'])
data_rep_v = data_rep[['Current GMT Dttm', 'True Course', 'Speed Made Good (Kts)']]    
data_rep_selection = pd.merge(data_rep_selection, data_rep_v, on='Current GMT Dttm')


data_clean = data_rep_selection.copy()         
date_strs =  data_clean['Current GMT Dttm'].dt.date

# Calculates the difference of a Dataframe element compared with another element in the Dataframe (default is element in previous row).
data_clean['diff_f'] = date_strs.diff()
data_clean['diff_b'] = date_strs.diff(-1)

# change data format 
for i in range(len(data_clean)):
    data_clean['diff_f'][i]=data_clean['diff_f'][i].total_seconds()/3600/24
    data_clean['diff_b'][i]=data_clean['diff_b'][i].total_seconds()/3600/24
    
d1 = data_clean[((data_clean['diff_f'].isnull()) & (data_clean['diff_b'] == -1)) | ((data_clean['diff_f'] > 1) & (data_clean['diff_b'] == -1))]
d2 = data_clean[((data_clean['diff_f'] == 1) & (data_clean['diff_b'].isnull())) | ((data_clean['diff_f'] == 1) & (data_clean['diff_b'] < -1))]

d3 = data_clean[(data_clean['diff_f'] > 1) & (data_clean['diff_b'] < -1)]

d1.index = range(d1.shape[0])
d2.index = range(d2.shape[0])
d = pd.merge(d1[['Current GMT Dttm']], d2[['Current GMT Dttm']], left_index=True, right_index=True)
        

data_ais_modification_select = []
data_ais_modification_select_o = []
for j in range(len(d)):
    date_s = d['Current GMT Dttm_x'][j]
    date_e = d['Current GMT Dttm_y'][j] 
    
    data_ais_modification = data_ais[(data_ais['Current GMT Dttm'] >= date_s) & (data_ais['Current GMT Dttm'] <= date_e)]            
    data_ais_modification.sort_values(by='Current GMT Dttm', ignore_index=True , inplace=True)
    data_ais_modification_index_notna = data_ais_modification[data_ais_modification['LON'].notna()].index.to_list()
    # data_ais_modification_index_isna  = data_ais_modification[data_ais_modification['LON'].isna()].index.to_list()
    
    for m in range(len(data_ais_modification_index_notna)-1):
        # test = data_ais_modification_index_notna[m]
        # print(test)
        inter_t = (data_ais_modification['Current GMT Dttm'][data_ais_modification_index_notna[m+1]]-data_ais_modification['Current GMT Dttm'][data_ais_modification_index_notna[m]]).total_seconds()/3600      
    
        # Convert decimal degrees to radians
        lon1 = data_ais_modification.iloc[data_ais_modification_index_notna[m]]['LON']
        lat1 = data_ais_modification.iloc[data_ais_modification_index_notna[m]]['LAT']
        lon2 = data_ais_modification.iloc[data_ais_modification_index_notna[m+1]]['LON']
        lat2 = data_ais_modification.iloc[data_ais_modification_index_notna[m+1]]['LAT']
        
        lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
        # haversine formulation
        dlon = lon2 - lon1 
        dlat = lat2 - lat1 
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a)) 
        r = 6371
        distance = c * r * 1000


        location = [] 
        # data_time= []
        if int(inter_t) != 1: 
            # print(inter_t)
            data_dis_ave = distance/inter_t  
            data_t  = pd.date_range(start=data_ais_modification['Current GMT Dttm'][data_ais_modification_index_notna[m]], periods=inter_t, freq='1H')                               
            for n in range(int(inter_t)):    
                location.append(lon_lat.computerThatLonLat(data_ais_modification.iloc[data_ais_modification_index_notna[m]]['LON'], data_ais_modification.iloc[data_ais_modification_index_notna[m]]['LAT'], data_ais_modification.iloc[data_ais_modification_index_notna[m]]['True Course'], data_dis_ave*n))            
            # data_time.append(data_t)
            data_t = pd.DataFrame(data_t)
            data_t.columns = ['Current GMT Dttm']
            location = pd.DataFrame(location, columns=['LON', 'LAT'])
            #location = pd.concat([data_t, location], ignore_index=True)
            #location.reset_index(drop=True, inplace=True)
            data_ais_modification_select.append(pd.concat([data_t, location], axis=1, ignore_index=False))               
print('success')
               
for k in d3.index.to_list():
    data_k = d3['Current GMT Dttm'][k]
    data_ais_modification_select.append(data_ais[data_ais['Current GMT Dttm'] == data_k])


data_ais_clean = pd.concat(data_ais_modification_select, ignore_index=True)

for m in range(len(data_ais)):
    for n in range(len(data_ais_clean)):   
        if data_ais['Current GMT Dttm'][m] == data_ais_clean['Current GMT Dttm'][n] and (pd.isnull(data_ais['LON'][m]) == True or pd.isnull(data_ais['LAT'][m]) == True):
            data_ais['LON'][m] = data_ais_clean['LON'][n]
            data_ais['LAT'][m] = data_ais_clean['LAT'][n]
            # data_ais_selection['True Course'][m] = data_rep_selection['True Course'][n]
 
for m in range(len(data_ais)):
    for n in range(len(data_rep_selection)):        
        if data_ais['Current GMT Dttm'][m] == data_rep_selection['Current GMT Dttm'][n] and (pd.isnull(data_ais['LON'][m]) == True or pd.isnull(data_ais['LAT'][m]) == True):
            data_ais['LON'][m] = data_rep_selection['LON'][n]
            data_ais['LAT'][m] = data_rep_selection['LAT'][n]
            
for m in range(len(data_ais)):
    for n in range(len(data_rep)):        
        if data_ais['Current GMT Dttm'][m] == data_rep['Current GMT Dttm'][n] and (pd.isnull(data_ais['LON'][m]) == True or pd.isnull(data_ais['LAT'][m]) == True):
            data_ais['LON'][m] = data_rep['Longitude'][n]
            data_ais['LAT'][m] = data_rep['Latitude'][n]


data_ais.to_excel(path_save, index=False)

