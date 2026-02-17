# -*- coding: utf-8 -*-
"""
Created on Mon Feb  3 13:17:16 2025

@author: m337l400
"""

import xarray as xr
import xvec
import geopandas as gpd
import pandas as pd
from multiprocessing import cpu_count
import matplotlib.pyplot as plt
import cftime
from datetime import datetime as dt
import os
from os import listdir
from os.path import isfile, join
import numpy as np

f_path = 'F:/HMA_glacio_hydro_index/'
file_list = [f for f in os.listdir(f_path) if f.endswith('.nc')]
o_path ='F:\HMA_glacio_hydro_index\HMA_glacio_hydro_index/'


for file in file_list:
    n_path = f'{f_path}{file}'
    ds = xr.open_dataset(n_path).xvec.decode_cf()
    # ds= ds.drop_vars(["gindex"])
    # ds= ds.drop_vars(["g_s"])
    # ds= ds.drop_vars(["g_y"])
    # ds= ds.drop_vars(["seasonal_mean"])
    # ds= ds.assign(precipitation=lambda x: (x.precipitation / 1000))
    # precipitation_v = ds.precipitation.values * (5000*5000)
    # ds= ds.assign(precipitation_v = (('geometry','time'), precipitation_v))
    # ds= ds.assign(gs=lambda x: (x.volume/ (x.volume + x.precipitation_v)))
    # ds= ds.assign(gy=lambda x: (x.runoff/ (x.runoff + x.precipitation_v)))
    # ds= ds.assign(g_index=lambda x: ((x.gs + x.gy)/ 2))
    

    # ds.g_index.values = np.where(ds.g_index.values<0, 0, ds.g_index.values)
    # ds.gy.values = np.where(ds.gy.values<0, 0, ds.gy.values)
    # ds.gs.values = np.where(ds.gs.values<0, 0, ds.gs.values)
    # ds.g_index.values = np.where(ds.g_index.values>1, 1, ds.g_index.values)
    # ds.gy.values = np.where(ds.gy.values>1, 1, ds.gy.values)
    # ds.gs.values = np.where(ds.gs.values>1, 1, ds.gs.values)
    # timelist = ds.time.values
    # ds['time'] = [dt.strptime(j, "%m/%d/%Y") for j in timelist]
    # g_season = ds.g_index.resample(time = "QS-DEC").mean(dim="time")
    # g_season = g_season.rename({'time':'season'})
    # ds = ds.assign(g_seasonal_mean = g_season)
    
    
    gs_season = ds.gs.resample(time = "QS-DEC").mean(dim="time")
    gs_season = gs_season.rename({'time':'season'})
    ds = ds.assign(gs_seasonal_mean = gs_season)
    gy_season = ds.gy.resample(time = "QS-DEC").mean(dim="time")
    gy_season = gy_season.rename({'time':'season'})
    ds = ds.assign(gy_seasonal_mean = gy_season)
    
    encoded = ds.xvec.encode_cf()
    encoded.to_netcdf(f'{o_path}{file}')


