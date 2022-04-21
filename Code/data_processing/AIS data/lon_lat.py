# -*- coding: utf-8 -*-
"""
Created on Mon Jul  5 14:40:55 2021

@author: YY_Chen
"""

import math
import pandas as pd
## North east down WGS-84 Long radius a=6378137 Short radius b=6356752.3142 Flattening f=1/298.2572236

## Long radius a=6378137 
a = 6378137
## Short radius b=6356752.3142
b = 6356752.3142
## Flattening f=1/298.2572236
f = 1 / 298.2572236

## degrees to radians, d radians
def rad(d):
    return d * math.pi / 180.0

## degrees to radians, x radians
def deg(x):
    return x * 180 / math.pi

## lon longitude, lat latitude, brng azimuth, dist distance(m)
def computerThatLonLat(lon, lat, brng, dist):
    
    alpha1 = rad(brng)
    sinAlpha1 = math.sin(alpha1)
    cosAlpha1 = math.cos(alpha1)

    tanU1 = (1 - f) * math.tan(rad(lat))
    cosU1 = 1 / math.sqrt((1 + tanU1 * tanU1))
    sinU1 = tanU1 * cosU1
    sigma1 = math.atan2(tanU1, cosAlpha1)
    sinAlpha = cosU1 * sinAlpha1
    cosSqAlpha = 1 - sinAlpha * sinAlpha
    uSq = cosSqAlpha * (a * a - b * b) / (b * b)
    A = 1 + uSq / 16384 * (4096 + uSq * (-768 + uSq * (320 - 175 * uSq)))
    B = uSq / 1024 * (256 + uSq * (-128 + uSq * (74 - 47 * uSq)))

    cos2SigmaM=0
    sinSigma=0
    cosSigma=0
    sigma = dist / (b * A)
    sigmaP = 2 * math.pi
    while math.fabs(sigma - sigmaP) > 1e-12:
        cos2SigmaM = math.cos(2 * sigma1 + sigma)
        sinSigma = math.sin(sigma)
        cosSigma = math.cos(sigma)
        deltaSigma = B * sinSigma * (cos2SigmaM + B / 4 * (cosSigma * (-1 + 2 * cos2SigmaM * cos2SigmaM)
                - B / 6 * cos2SigmaM * (-3 + 4 * sinSigma * sinSigma) * (-3 + 4 * cos2SigmaM * cos2SigmaM)))
        sigmaP = sigma
        sigma = dist / (b * A) + deltaSigma
    
    tmp  = sinU1 * sinSigma - cosU1 * cosSigma * cosAlpha1
    lat2 = math.atan2(sinU1 * cosSigma + cosU1 * sinSigma * cosAlpha1, (1 - f) * math.sqrt(sinAlpha * sinAlpha + tmp * tmp))
    lamb = math.atan2(sinSigma * sinAlpha1, cosU1 * cosSigma - sinU1 * sinSigma * cosAlpha1)
    C = f / 16 * cosSqAlpha * (4 + f * (4 - 3 * cosSqAlpha))
    L = lamb - (1 - C) * f * sinAlpha * (sigma + C * sinSigma * (cos2SigmaM + C * cosSigma * (-1 + 2 * cos2SigmaM * cos2SigmaM)))

    lon=lon+deg(L)
    lat=deg(lat2)

    #print(lon)
    #print(lat)
    #print('success')
    return lon, lat



# =============================================================================
# if __name__=='__main__':
# 
#     lon=120.353842
#     lat=30.338461
#     brng=90
#     dist=1
# 
#     computerThatLonLat(lon, lat, brng, dist)
# =============================================================================
