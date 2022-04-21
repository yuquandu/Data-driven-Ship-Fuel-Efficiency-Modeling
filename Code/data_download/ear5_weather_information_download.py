# -*- coding: utf-8 -*-
"""
Created on Tue Jun 29 10:31:37 2021

@author: Yanyu Chen
"""

import cdsapi

client = cdsapi.Client()

client.retrieve(
    'reanalysis-era5-single-levels',
    {
        'product_type': 'reanalysis',
        'variable': [
            '10m_u_component_of_wind', '10m_v_component_of_wind', 'mean_direction_of_total_swell',
            'mean_direction_of_wind_waves', 'mean_period_of_total_swell', 'mean_period_of_wind_waves',
            'mean_wave_direction', 'mean_wave_period', 'sea_surface_temperature',
            'significant_height_of_combined_wind_waves_and_swell', 'significant_height_of_total_swell', 'significant_height_of_wind_waves',
        ],
        'year': '2016',
        'month': [
            '01', '02', '03',
            '04', '05', '06',
            '07', '08', '09',
            '10', '11', '12',
        ],
        'day': [
            '01', '02', '03',
            '04', '05', '06',
            '07', '08', '09',
            '10', '11', '12',
            '13', '14', '15',
            '16', '17', '18',
            '19', '20', '21',
            '22', '23', '24',
            '25', '26', '27',
            '28', '29', '30',
            '31',
        ],
        'time': [
            '00:00', '01:00', '02:00',
            '03:00', '04:00', '05:00',
            '06:00', '07:00', '08:00',
            '09:00', '10:00', '11:00',
            '12:00', '13:00', '14:00',
            '15:00', '16:00', '17:00',
            '18:00', '19:00', '20:00',
            '21:00', '22:00', '23:00',
            ],
        'grid':[
            '0.25', '0.25'
        ],
        'area': [
            90, -180, -90,
            180,
        ],
        'format': 'grib',
    },
    'E:/project_iamu/ocean_wave_2016.grib')