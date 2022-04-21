# -*- coding: utf-8 -*-
"""
Created on Fri Jul 30 00:12:56 2021

@author: YY_Chen
"""

import os
import pandas as pd
import numpy as np
import openpyxl
import datetime
import math
import netCDF4 as nc


# Ship_S1 voyage dataset path
path = './Ship_S1.xlsx'
path_save = './Ship_S1_Correct.xlsx'

# read data
original_sheet = pd.read_excel(path, sheet_name = 'VOMS')

# columns' name
select_col = ['Current GMT Dttm', 'Vessel Code', 'Service Code', 'Event Code', 'Mode Code', 'Orig Port Code', 'Dest Port Code', 
              'Longitude (deg)', 'Longitude (min)', 'Longitude Dir', 'Latitude (deg)', 'Latitude (min)', 'Latitude Dir', 'True Course', 
              'Dist Made Good', 'Total Elapsed Hrs', 'Speed Made Good (Kts)', 'Engine Avg RPM Last Event', 'Total Propulsion Power (KW)',
              'M-Eng HFO Qty Consumed', 'M-Eng LSFO Qty Consumed', 'M-Eng LSGO Qty Consumed', 'M-Eng MGO Qty Consumed', 'M-Eng ULSGO Qty Consumed',
              'Vsl Displacement', 'Total Vsl Dwt', 'Total Cargo Weight', 'Ballast Water Qty', 'Vessel Trim (Mtrs)', 'Computed Mid Draft',
              'Swell Dir', 'Swell Ht (mtr)', 'Sea Current', 'Sea Curent Dir', 'Wind Force', 'Wind Dir', 'Sea Water Temp']

# import data table
select_data = original_sheet[select_col].sort_values(by='Current GMT Dttm')             

# Calculate data length
data_length  = len(select_data)   

# select data                                                      
state        = select_data['Mode Code']
current_time = select_data['Current GMT Dttm']
sailing_time = select_data['Total Elapsed Hrs']


# Time Index Correction
a_data = select_data[select_col]                                                                      # Read data table specified column
# a_data = a_data.drop(a_data[a_data['Total Elapsed Hrs'] == 0].index)
# a_data = a_data.reset_index(drop = True)
for i in range(1, data_length):
    time_b = datetime.datetime.strptime(str(current_time[i-1]).split(".")[0], '%Y-%m-%d %H:%M:%S')
    time_c = datetime.datetime.strptime(str(current_time[i]).split(".")[0], '%Y-%m-%d %H:%M:%S')
    inter  = (((time_c - time_b).days)*24*3600 + (time_c - time_b).seconds)/3600
    if inter < 0:
        select_data.iloc[i-1,:] = a_data.iloc[i,:]
        select_data.iloc[i,:]   = a_data.iloc[i-1,:]
        print('time correction index',i)


# Total Elapsed Hrs Correction
time_replace_index = []
# current_time = current_time.tolist()
# sailing_time = sailing_time.tolist()
time_interval       = np.zeros((1, data_length))
time_interval[0, 0] = sailing_time[0]
for i in range(1, data_length):
    time_b = datetime.datetime.strptime(str(current_time[i-1]), '%Y-%m-%d %H:%M:%S')
    time_c = datetime.datetime.strptime(str(current_time[i]), '%Y-%m-%d %H:%M:%S')
    time_interval[0, i] = (((time_c - time_b).days)*24*3600 + (time_c - time_b).seconds)/3600
    if time_interval[0, i] > 0 and time_interval[0, i] < 30 and sailing_time[i] > 30 and abs(time_interval[0, i]-sailing_time[i]) > 1:
        select_data.loc[i, 'Total Elapsed Hrs'] = time_interval[0, i]
        time_replace_index.append(i)
print("Replaced time row index:", time_replace_index)


# Speed Correction
speed_b = 18.5                                                                                        # Define an initial speed
speed_a = 18.5                                                                                        # Define an initial speed
for i in range(1, data_length-1):
    if select_data['Speed Made Good (Kts)'][i] >= 26:
        print("Out-of-limit speed:", i, select_data['Speed Made Good (Kts)'][i])
        for j in range(i-1, -1, -1):
            if state[j] == 'Sea' and select_data['Speed Made Good (Kts)'][j] >= 12 and select_data['Speed Made Good (Kts)'][j] < 26 and sailing_time[j] >= 10:
                speed_b = select_data['Speed Made Good (Kts)'][j]                       # Get the previous speed.
                break
        for k in range(i+1, data_length):
            if state[k] == 'Sea' and select_data['Speed Made Good (Kts)'][k] >= 12 and select_data['Speed Made Good (Kts)'][k] < 26 and sailing_time[k] >= 10:
                speed_a = select_data['Speed Made Good (Kts)'][k]                       # Get the next speed.
                break            
        if select_data['Dist Made Good'][i] > 0:
            time_b = datetime.datetime.strptime(str(current_time[i-1]), '%Y-%m-%d %H:%M:%S')
            time_c = datetime.datetime.strptime(str(current_time[i]), '%Y-%m-%d %H:%M:%S')
            inter  = (((time_c - time_b).days)*24*3600 + (time_c - time_b).seconds)/3600
            if abs(inter - select_data['Total Elapsed Hrs'][i]) > 1 and select_data['Total Elapsed Hrs'][i] < 30:
                inter = select_data['Total Elapsed Hrs'][i]
            correct_speed = select_data['Dist Made Good'][i]/inter
            if correct_speed < 26:
                select_data.loc[i,'Speed Made Good (Kts)'] = correct_speed
            else:
                select_data.loc[i,'Speed Made Good (Kts)'] = 0.5*(speed_b+speed_a)
        else:
            select_data.loc[i,'Speed Made Good (Kts)'] = 0.5*(speed_b+speed_a)      
        print("Correct speed:", i, select_data['Speed Made Good (Kts)'][i])


if select_data['Speed Made Good (Kts)'][0] >= 26:
    if select_data['Dist Made Good'][0] > 0:
        correct_speed = select_data['Dist Made Good'][0]/select_data['Total Elapsed Hrs'][0]
        if correct_speed < 26:
            select_data.loc[0,'Speed Made Good (Kts)'] = correct_speed
        else:
            select_data.loc[0,'Speed Made Good (Kts)'] = select_data['Speed Made Good (Kts)'][1]
    else:
        select_data.loc[0,'Speed Made Good (Kts)'] = select_data['Speed Made Good (Kts)'][1]
        
if select_data['Speed Made Good (Kts)'][data_length-1] >= 26:
    if select_data['Dist Made Good'][data_length-1] > 0:
        correct_speed = select_data['Dist Made Good'][data_length-1]/select_data['Total Elapsed Hrs'][data_length-1]
        if correct_speed < 26:
            select_data.loc[data_length-1,'Speed Made Good (Kts)'] = correct_speed
        else:
            select_data.loc[data_length-1,'Speed Made Good (Kts)'] = select_data['Speed Made Good (Kts)'][data_length-2]
    else:
        select_data.loc[data_length-1,'Speed Made Good (Kts)'] = select_data['Speed Made Good (Kts)'][data_length-2]


# Empty Ship Weight Camputation
temp_counter   = 0
temp_weightSum = 0
for j in range(0, data_length):
    temp_disp = select_data['Vsl Displacement'][j]
    temp_dwt  = select_data['Total Vsl Dwt'][j]
    temp_lightweight = temp_disp - temp_dwt
    if temp_disp > 0 and temp_dwt > 0 and temp_lightweight > 0:
        temp_weightSum = temp_weightSum + temp_lightweight                 
        temp_counter = temp_counter + 1
ShipWeight = temp_weightSum / temp_counter


# Reference Displacement Calculation
Refe = np.zeros((1, 4))
for k in range(15, data_length):
    if select_data['Mode Code'][k] == 'Sea':
        temp_disp  = select_data['Vsl Displacement'][k]
        temp_bllst = select_data['Ballast Water Qty'][k]
        for xx in range(k, -1, -1):
            if select_data['Total Cargo Weight'][xx] > 0:
                temp_cargo = select_data['Total Cargo Weight'][xx]
                break
        for yy in range(k, -1, -1):
            if select_data['Total Vsl Dwt'][yy] > 0:
                temp_dwt = select_data['Total Vsl Dwt'][yy]
                break
        if temp_disp > 0 and temp_bllst > 0 and temp_cargo > 0 and temp_dwt > 0 and (temp_disp - (temp_cargo + temp_bllst + ShipWeight) < 5000):
            Refe[0,0] = temp_bllst
            Refe[0,1] = temp_cargo
            Refe[0,2] = temp_dwt
            Refe[0,3] = temp_disp
            break

# Displacement Correction
disp_replace_index = []
for nn in range(0, data_length-1):
    bllstWater1 = select_data['Ballast Water Qty'][nn]
    bllstWater2 = bllstWater1 / 10
    cargoWeight = 0
    deadWeight  = 0
    bllstWater0 = 0        

    for mm in range(nn, -1, -1):
        if select_data['Total Cargo Weight'][mm] > 0:
            cargoWeight = select_data['Total Cargo Weight'][mm]
            break
    for ff in range(nn, -1, -1):
        if select_data['Total Vsl Dwt'][ff] > 0:
            deadWeight  = select_data['Total Vsl Dwt'][ff]
            bllstWater0 = select_data['Ballast Water Qty'][ff]
            break
   
    disp = select_data['Vsl Displacement'][nn]
    disp1 = disp * 10
    
    if nn == 0:
        exp1 = 0
    else:
        exp1 = select_data['Vsl Displacement'][nn-1]
        for gg in range(nn, 0, -1):
            if select_data['Vsl Displacement'][gg-1] > 0:
                exp1 = select_data['Vsl Displacement'][gg-1]
                break
    
    exp2 = select_data['Vsl Displacement'][nn+1]
    for hh in range(nn, data_length-1):
        if select_data['Vsl Displacement'][hh+1] > 0:
            exp2 = select_data['Vsl Displacement'][hh+1]
            break
        if hh+1 == data_length-1:
            if select_data['Vsl Displacement'][hh+1] < 0 or select_data['Vsl Displacement'][hh+1] == None:
                exp2 = select_data['Vsl Displacement'][nn-1]
                
    if exp1 > 0 and exp2 > 0:                                                                         # If the displacement of the previous and next row is greater than 0
        disp2 = (exp1 + exp2) / 2                                                                     # Use the front and rear displacement to calculate the average
    elif exp1 == 0 and exp2 == 0:                                                                     # If the displacement of the previous and next row is equal to 0
        disp2 = 0
    elif exp1 > 0 and exp2 == 0:                                                                      # If the previous line is greater than 0 and the next line is equal to 0
        disp2 = exp1
    else:
        disp2 = exp2
    
    refer_bllst = Refe[0,0]
    refer_cargo = Refe[0,1]
    refer_dwt   = Refe[0,2]
    refer_disp  = Refe[0,3]
    
    delta_bllst = bllstWater1 - refer_bllst                                                           # Calculating Ballast Water Quality Deviation
    delta_cargo = cargoWeight - refer_cargo                                                           # Calculate cargo weight deviation
    delta_dwt   = deadWeight - refer_dwt                                                              # Calculate total payload deviation
    delta_disp  = disp - refer_disp                                                                   # Calculate displacement deviation
    #disp3 = refer_disp + delta_bllst + delta_cargo                                                   # Reference displacement plus ballast water quality deviation and cargo weight deviation
    
    disp_value = disp
    if disp <= ShipWeight + cargoWeight:
        temp_value1 = (disp1 - refer_disp) - (delta_bllst + delta_cargo)
        temp_value2 = (disp2 - refer_disp) - (delta_bllst + delta_cargo)
        if abs(temp_value1) <= abs(temp_value2) or disp2 == 0:
            disp_value = disp1
        else:
            disp_value = disp2      
    else:
        if abs(delta_dwt + (bllstWater1 - bllstWater0) - delta_disp) > 5000 and cargoWeight > 0:
            if disp2 > 0:
                disp_value = disp2
            else:
                disp_value = refer_disp + delta_dwt + (bllstWater1 - bllstWater0)
                
        if (delta_bllst + delta_cargo - delta_disp) > 5000 and abs(delta_dwt + (bllstWater2 - bllstWater0) - delta_disp) <= 5000:
            disp_value = disp
            
    if disp_value != disp:
        disp_replace_index.append(nn)
    
    select_data.loc[nn,'Vsl Displacement Correct'] = disp_value                                       # A column "Vsl Displacement Correct" was added at the end of the data table.
# print("Modified displacement index:", disp_replace_index)

     
# Longitude Direction Correction
for s in range(0, 20):
    if isinstance(select_data['Longitude Dir'][s], str) == True:
        sta = s+1
        break
    
# Longitude Direction Correction    
lon_deg_min = select_data['Longitude (deg)']+(select_data['Longitude (min)']/60)                      # Calculate Longitude Accuracy
for i in range(sta, data_length-1):
    if isinstance(select_data['Longitude Dir'][i], str) == True:
        if select_data['Longitude Dir'][i] != select_data['Longitude Dir'][i-1]:                      # If the previous and next longitude directions are different.
            for j in range(i-1, -1, -1):
                lon_before = select_data['Longitude Dir'][0]
                if isinstance(select_data['Longitude Dir'][j], str) == True:
                    lon_before = select_data['Longitude Dir'][j]                                      # Get the previous longitude direction.
                    break
            for k in range(i+1, data_length):
                lon_after = select_data['Longitude Dir'][data_length-1]
                if isinstance(select_data['Longitude Dir'][k], str) == True:
                    lon_after = select_data['Longitude Dir'][k]                                       # Get the next longitude direction.
                    break
            for h in range(i+2, data_length):
                lon_after_2 = select_data['Longitude Dir'][data_length-1]
                if isinstance(select_data['Longitude Dir'][h], str) == True:
                    lon_after_2 = select_data['Longitude Dir'][h]
                    break
                
            for m in range(i-1, -1, -1):
                lon_deg_min_before = lon_deg_min[0]
                time_b = datetime.datetime.strptime(str(current_time[0]), '%Y-%m-%d %H:%M:%S')
                if lon_deg_min[m] >= 0:
                    lon_deg_min_before = lon_deg_min[m]                                              # Get the previous longitude
                    time_b = datetime.datetime.strptime(str(current_time[m]), '%Y-%m-%d %H:%M:%S')   # Get the previous time
                    break
            for n in range(i+1, data_length):
                lon_deg_min_after = lon_deg_min[data_length-1]
                if lon_deg_min[n] >= 0:
                    lon_deg_min_after = lon_deg_min[n]                                               # Get the next longitude
                    break
                
            if lon_deg_min[i] <= 150 and lon_deg_min[i] >= 30 and (lon_deg_min_before <= 150 or lon_deg_min_after <= 150) and (lon_deg_min_before >= 30 or lon_deg_min_after >= 30):
                if select_data['Longitude Dir'][i] != lon_before:                                    # If the previous and next longitude directions are different
                    select_data.loc[i, 'Longitude Dir'] = lon_before                                 # Equal to the previous longitude direction
                    print("Longitude direction correction (30-150):",i,lon_before)
            else:
                if select_data['Longitude Dir'][i] != lon_before:
                    if lon_deg_min[i] > 150 and (lon_deg_min_before > 150 or lon_deg_min_after > 150):
                        deta_lon = (180-lon_deg_min[i])+(180-lon_deg_min_before)                     # Calculate the longitude difference.
                    
                    if lon_deg_min[i] < 30 and (lon_deg_min_before < 30 or lon_deg_min_after < 30):
                        deta_lon = abs(lon_deg_min[i]+lon_deg_min_before)                            # Calculate the longitude difference.

                    time_c = datetime.datetime.strptime(str(current_time[i]), '%Y-%m-%d %H:%M:%S')
                    inter = (((time_c - time_b).days)*24*3600 + (time_c - time_b).seconds)/3600      # Calculate the time interval.
                    deta_dis_max = max(select_data['Speed Made Good (Kts)'])*inter                   # Calculate the maximum possible distance.
                    
                    if deta_lon > (deta_dis_max/30):                                                 # 30 nautical miles is the minimum distance between 2 longitudes.
                        select_data.loc[i,'Longitude Dir'] = lon_before
                        print("Longitude direction correction (>150<30):", i, lon_before) 

# Latitude Direction Correction
lat_deg_min = select_data['Latitude (deg)']+(select_data['Latitude (min)']/60)                       # Calculate the exact latitude.
for i in range(sta, data_length-1):
    if isinstance(select_data['Latitude Dir'][i], str) == True:
        if select_data['Latitude Dir'][i] != select_data['Latitude Dir'][i-1]:                       # If the previous and next latitude directions are different.
            for j in range(i-1, -1, -1):
                lat_before = select_data['Latitude Dir'][0]
                if isinstance(select_data['Latitude Dir'][j], str) == True:
                    lat_before = select_data['Latitude Dir'][j]                                      # Get the previous latitude direction
                    break
            for k in range(i+1, data_length):
                lat_after = select_data['Latitude Dir'][data_length-1]
                if isinstance(select_data['Latitude Dir'][k], str) == True:
                    lat_after = select_data['Latitude Dir'][k]                                       # Get the next latitude direction
                    break
            for h in range(i+2, data_length):
                lat_after_2 = select_data['Latitude Dir'][data_length-1]
                if isinstance(select_data['Latitude Dir'][h], str) == True:
                    lat_after_2 = select_data['Latitude Dir'][h]
                    break
                
            for m in range(i-1, -1, -1):
                lat_deg_min_before = lat_deg_min[0]
                time_b = datetime.datetime.strptime(str(current_time[0]), '%Y-%m-%d %H:%M:%S')
                if lat_deg_min[m] >= 0:
                    lat_deg_min_before = lat_deg_min[m]                                             # Get the previous latitude
                    time_b = datetime.datetime.strptime(str(current_time[m]), '%Y-%m-%d %H:%M:%S')
                    break
            for n in range(i+1, data_length):
                lat_deg_min_after = lat_deg_min[data_length-1]
                if lat_deg_min[n] >= 0:
                    lat_deg_min_after = lat_deg_min[n]                                              # Get the next latitude
                    break
            
            if lat_deg_min[i] >= 30 and (lat_deg_min_before >= 30 or lat_deg_min_after >= 30):
                if select_data['Latitude Dir'][i] != lat_before:
                    select_data.loc[i,'Latitude Dir'] = lat_before                                  # Equal to the previous latitude direction
                    print("Latitude direction correction (>=30):",i,lat_before)
            elif lat_deg_min[i] < 30 and (lat_deg_min_before < 30 or lat_deg_min_after < 30):
                if select_data['Latitude Dir'][i] != lat_before:
                    deta_lat = abs(lat_deg_min[i]+lat_deg_min_before)                               # Calculate the latitude difference
                    time_c = datetime.datetime.strptime(str(current_time[i]), '%Y-%m-%d %H:%M:%S')
                    inter = (((time_c - time_b).days)*24*3600 + (time_c - time_b).seconds)/3600
                    deta_dis_max = max(select_data['Speed Made Good (Kts)'])*inter                  # Calculate the maximum possible distance
                    if deta_lat > (deta_dis_max/60):                                                # 60 nautical miles is the distance between 2 latitudes
                        select_data.loc[i,'Latitude Dir'] = lat_before
                        print("Latitude direction correction (<30):",i,lat_before)

# Latitude Correction
earth_r = 6378.140                                                                                  # Radius of the Earth
for i in range(sta, data_length):
    lat_d_m = select_data['Latitude (deg)']+(select_data['Latitude (min)']/60)
    if state[i] == 'Sea':
        if select_data['Latitude (deg)'][i] >= 0 and select_data['Latitude (deg)'][i-1] >= 0:
            if select_data['Latitude Dir'][i] == select_data['Latitude Dir'][i-1]:
                deta_lat = abs(lat_d_m[i]-lat_d_m[i-1])                                             # Calculate the latitude difference
            elif select_data['Latitude Dir'][i] != select_data['Latitude Dir'][i-1]:
                deta_lat = abs(lat_d_m[i]+lat_d_m[i-1])                                             # Calculate the latitude difference
            deta_dis = deta_lat*60                                                                  # Calculate the separation distance. 
            time_c = datetime.datetime.strptime(str(current_time[i]), '%Y-%m-%d %H:%M:%S')          # Get current time
            time_b = datetime.datetime.strptime(str(current_time[i-1]), '%Y-%m-%d %H:%M:%S')        # Get previous time
            inter  = (((time_c - time_b).days)*24*3600 + (time_c - time_b).seconds)/3600
            deta_dis_max = max(select_data['Speed Made Good (Kts)'])*inter                          # Calculate the maximum possible distance
            if deta_dis > deta_dis_max or deta_lat > (deta_dis_max/60):
                for j in range(i,-1,-1):
                    if select_data['True Course'][j] >= 0:
                        t_course = select_data['True Course'][j]                                    # Get true course
                        break
                for k in range(i,-1,-1):
                    if select_data['Speed Made Good (Kts)'][k] >= 0:
                        s_speed = select_data['Speed Made Good (Kts)'][k]                           # Get ship speed
                        break
                c_dis = s_speed*inter                                                               # Calculate sailing distance

                if t_course >= 0 and t_course <= 90:
                    true_c = t_course                                                               # The true course is converted to 0-90.
                if t_course > 90 and t_course <= 180:
                    true_c = 180-t_course
                if t_course > 180 and t_course <= 270:
                    true_c = t_course-180
                if t_course > 270 and t_course <= 360:
                    true_c = 360-t_course
                true_c = math.radians(true_c)                                                       # Convert to radians
                
                if (t_course >= 0 and t_course <= 90) or (t_course > 270 and t_course <= 360):
                    d_lat = (c_dis*math.cos(true_c))/60                                             # Calculate the latitude interval.
                if t_course > 90 and t_course <= 270:
                    d_lat = (-1*c_dis*math.cos(true_c))/60                                          # Calculate the latitude interval.

                lat_b = lat_d_m[i-1]
                if select_data['Latitude Dir'][i-1] == 'S':
                    lat_b = -lat_b                                                                  # South latitude transformation.
                
                lat_c = lat_b + d_lat
                print("Latitude correction:", i, lat_c)
                if lat_c < 0:
                    lat_c = abs(lat_c)                                                              # South latitude transformation.
                    select_data.loc[i,'Latitude Dir'] = 'S'
                select_data.loc[i,'Latitude (deg)'] = int(lat_c)
                select_data.loc[i,'Latitude (min)'] = (lat_c-int(lat_c))*60

# Longitude correction
for i in range(sta,data_length):
    lat_d_m = select_data['Latitude (deg)']+(select_data['Latitude (min)']/60)
    lon_d_m = select_data['Longitude (deg)']+(select_data['Longitude (min)']/60)
    if state[i] == 'Sea':
        if select_data['Longitude (deg)'][i] >= 0 and select_data['Longitude (deg)'][i-1] >= 0:
            if select_data['Longitude Dir'][i] == select_data['Longitude Dir'][i-1]:
                deta_lon = abs(lon_d_m[i]-lon_d_m[i-1])                                             # Calculate the longitude difference
            elif select_data['Longitude Dir'][i] != select_data['Longitude Dir'][i-1]:
                if lon_d_m[i] > 150 and lon_d_m[i-1] > 150:
                    deta_lon = (180-lon_d_m[i])+(180-lon_d_m[i-1])                                  # Calculate the longitude difference
                elif lon_d_m[i] < 30 and lon_d_m[i-1] < 30:
                    deta_lon = abs(lon_d_m[i]+lon_d_m[i-1])                                         # Calculate the longitude difference
            deta_dis_lon = deta_lon*60*math.cos(math.radians(0.5*(lat_d_m[i]+lat_d_m[i-1])))        # Calculate the separation distance
            time_c = datetime.datetime.strptime(str(current_time[i]), '%Y-%m-%d %H:%M:%S')
            time_b = datetime.datetime.strptime(str(current_time[i-1]), '%Y-%m-%d %H:%M:%S')
            inter = (((time_c - time_b).days)*24*3600 + (time_c - time_b).seconds)/3600             # Time interval
            deta_dis_max = max(select_data['Speed Made Good (Kts)'])*inter                          # Calculate the maximum possible distance
            if deta_dis_lon > deta_dis_max or deta_lon > (deta_dis_max/30):
                for j in range(i,-1,-1):
                    if select_data['True Course'][j] >= 0:
                        t_course = select_data['True Course'][j]                                    # Get true course
                        break
                for k in range(i,-1,-1):
                    if select_data['Speed Made Good (Kts)'][k] >= 0:
                        s_speed = select_data['Speed Made Good (Kts)'][k]                           # Get ship speed
                        break
                c_dis = s_speed*inter                                                               # Calculate sailing distance
                
                if t_course >= 0 and t_course <= 90:
                    true_c = t_course                                                               # The true course is converted to 0-90 
                if t_course > 90 and t_course <= 180:
                    true_c = 180-t_course
                if t_course > 180 and t_course <= 270:
                    true_c = t_course-180
                if t_course > 270 and t_course <= 360:
                    true_c = 360-t_course
                true_c = math.radians(true_c)                                                       # Convert to radians
                
                lat_b = lat_d_m[i-1]
                if select_data['Latitude Dir'][i-1] == 'S':
                    lat_b = -lat_b                                                                  # South latitude transformation
                
                lat_c = lat_d_m[i]
                if select_data['Latitude Dir'][i] == 'S':
                    lat_c = -lat_c                                                                  # South latitude transformation
                
                mean_lat = 0.5*(abs(lat_b)+abs(lat_c))                                              # Calculate average latitude
                mean_lat = math.radians(mean_lat)
                lon_b = lon_d_m[i-1]
                if select_data['Longitude Dir'][i-1] == 'W':
                    lon_b = 360-lon_b                                                               # West longitude conversion
                    
                if t_course >= 0 and t_course <= 180:
                    d_lon = (c_dis*math.sin(true_c)*(1/math.cos(mean_lat)))/60                      # Calculate longitude interval
                if t_course > 180 and t_course <= 360:
                    d_lon = (-1*c_dis*math.sin(true_c)*(1/math.cos(mean_lat)))/60                   # Calculate longitude interval
                
                lon_c = lon_b + d_lon
                if lon_c > 180 and lon_c < 360:
                    lon_c = 360-lon_c                                                               # West longitude conversion
                    select_data.loc[i,'Longitude Dir'] = 'W'
                if lon_c >= 360:
                    lon_c = lon_c-360                                                               # East longitude transformation
                if lon_c < 0:
                    lon_c = abs(lon_c)                                                              # West longitude conversion
                    select_data.loc[i,'Longitude Dir'] = 'W'
                print("longitude correction:",i,lon_c)
                select_data.loc[i,'Longitude (deg)'] = int(lon_c)
                select_data.loc[i,'Longitude (min)'] = (lon_c-int(lon_c))*60

# Current direction transformation
select_data['Sea Curent Dir'].replace('E', 1, inplace = True)               # Head
select_data['Sea Curent Dir'].replace(['D','F'], 2, inplace = True)         # Bow
select_data['Sea Curent Dir'].replace(['C','G'], 3, inplace = True)         # Beam
select_data['Sea Curent Dir'].replace(['B','H'], 4, inplace = True)         # Stern
select_data['Sea Curent Dir'].replace('A', 5, inplace=True)                 # Following

# Surge direction and wind direction transformation
select_data.replace('A', 1, inplace=True)                                   # Following
select_data.replace(['B','H'], 2, inplace=True)                             # Stern
select_data.replace(['C','G'], 3, inplace=True)                             # Beam
select_data.replace(['D','F'], 4, inplace=True)                             # Bow
select_data['Swell Dir'].replace('E', 5, inplace=True)                      # Head
select_data['Wind Dir'].replace('E', 5, inplace=True)                       # Head


select_data.to_excel(path_save, index=None)
print('Data saved')