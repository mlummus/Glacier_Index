# -*- coding: utf-8 -*-
"""
Created on Mon Mar  3 12:58:02 2025

@author: m337l400
"""

import xarray as xr
import geopandas as gpd
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from datetime import datetime as dt
import numpy as np
import contextily as cx
import cartopy.crs as ccrs
import os
import xvec
from scipy.signal import detrend
import contextily as cx
from matplotlib import colors, cm
from mpl_toolkits.axes_grid1 import make_axes_locatable

scenario = '2-45'

fn1 = f'F:/HMA_glacio_hydro_index/gindex_AWI-CM-1-1-MR_scenarioSSP{scenario}.nc'
fn2 = f'F:/HMA_glacio_hydro_index/gindex_CMCC-ESM2_scenarioSSP{scenario}.nc'
fn3 = f'F:/HMA_glacio_hydro_index/gindex_EC-Earth3_scenarioSSP{scenario}.nc'
fn4 = f'F:/HMA_glacio_hydro_index/gindex_INM-CM4-8_scenarioSSP{scenario}.nc'
fn5 = f'F:/HMA_glacio_hydro_index/gindex_MPI-ESM1-2-HR_scenarioSSP{scenario}.nc'
fn6 = f'F:/HMA_glacio_hydro_index/gindex_MRI-ESM2-0_scenarioSSP{scenario}.nc'
fn7 = f'F:/HMA_glacio_hydro_index/gindex_NorESM2-MM_scenarioSSP{scenario}.nc'
fn8 = f'F:/HMA_glacio_hydro_index/gindex_TaiESM1_scenarioSSP{scenario}.nc'
fn9 = f'F:/HMA_glacio_hydro_index/gindex_GFDL-SPEAR-MED_r1i1p1f1_scenarioSSP{scenario}.nc'

da1 = xr.open_dataset(fn1).xvec.decode_cf()
da2 = xr.open_dataset(fn2).xvec.decode_cf()
da3 = xr.open_dataset(fn3).xvec.decode_cf()
da4 = xr.open_dataset(fn4).xvec.decode_cf()
da5 = xr.open_dataset(fn5).xvec.decode_cf()
da6 = xr.open_dataset(fn6).xvec.decode_cf()
da7 = xr.open_dataset(fn7).xvec.decode_cf()
da8 = xr.open_dataset(fn8).xvec.decode_cf()
da9 = xr.open_dataset(fn9).xvec.decode_cf()

da_concat = xr.concat([da1, da2, da3, da4, da5, da6, da7, da8, da9], pd.Index([1, 2, 3, 4, 5, 6, 7, 8, 9], name='model'))

model_mean = da_concat.mean(dim = "model")

# encode the dataset according to xvec standards so it can be saved out
encoded = model_mean.xvec.encode_cf()
encoded.to_netcdf(f"F:/HMA_glacio_hydro_index/gindex_model_mean_scenarioSSP{scenario}.nc", mode="w")

#%%
scenario = '5-85'

fn1 = f'F:/HMA_glacio_hydro_index/gindex_GFDL-SPEAR-MED_r1i1p1f1_scenarioSSP{scenario}.nc'
fn2 = f'F:/HMA_glacio_hydro_index/gindex_GFDL-SPEAR-MED_r2i1p1f1_scenarioSSP{scenario}.nc'
fn3 = f'F:/HMA_glacio_hydro_index/gindex_GFDL-SPEAR-MED_r3i1p1f1_scenarioSSP{scenario}.nc'
fn4 = f'F:/HMA_glacio_hydro_index/gindex_GFDL-SPEAR-MED_r4i1p1f1_scenarioSSP{scenario}.nc'
fn5 = f'F:/HMA_glacio_hydro_index/gindex_GFDL-SPEAR-MED_r5i1p1f1_scenarioSSP{scenario}.nc'
fn6 = f'F:/HMA_glacio_hydro_index/gindex_GFDL-SPEAR-MED_r6i1p1f1_scenarioSSP{scenario}.nc'
fn7 = f'F:/HMA_glacio_hydro_index/gindex_GFDL-SPEAR-MED_r7i1p1f1_scenarioSSP{scenario}.nc'
fn8 = f'F:/HMA_glacio_hydro_index/gindex_GFDL-SPEAR-MED_r8i1p1f1_scenarioSSP{scenario}.nc'
fn9 = f'F:/HMA_glacio_hydro_index/gindex_GFDL-SPEAR-MED_r9i1p1f1_scenarioSSP{scenario}.nc'
fn10 = f'F:/HMA_glacio_hydro_index/gindex_GFDL-SPEAR-MED_r10i1p1f1_scenarioSSP{scenario}.nc'
fn11 = f'F:/HMA_glacio_hydro_index/gindex_GFDL-SPEAR-MED_r11i1p1f1_scenarioSSP{scenario}.nc'
fn12 = f'F:/HMA_glacio_hydro_index/gindex_GFDL-SPEAR-MED_r12i1p1f1_scenarioSSP{scenario}.nc'
fn13 = f'F:/HMA_glacio_hydro_index/gindex_GFDL-SPEAR-MED_r13i1p1f1_scenarioSSP{scenario}.nc'
fn14 = f'F:/HMA_glacio_hydro_index/gindex_GFDL-SPEAR-MED_r14i1p1f1_scenarioSSP{scenario}.nc'
fn15 = f'F:/HMA_glacio_hydro_index/gindex_GFDL-SPEAR-MED_r15i1p1f1_scenarioSSP{scenario}.nc'
fn16 = f'F:/HMA_glacio_hydro_index/gindex_GFDL-SPEAR-MED_r16i1p1f1_scenarioSSP{scenario}.nc'
fn17 = f'F:/HMA_glacio_hydro_index/gindex_GFDL-SPEAR-MED_r17i1p1f1_scenarioSSP{scenario}.nc'
fn18 = f'F:/HMA_glacio_hydro_index/gindex_GFDL-SPEAR-MED_r18i1p1f1_scenarioSSP{scenario}.nc'
fn19 = f'F:/HMA_glacio_hydro_index/gindex_GFDL-SPEAR-MED_r19i1p1f1_scenarioSSP{scenario}.nc'
fn20 = f'F:/HMA_glacio_hydro_index/gindex_GFDL-SPEAR-MED_r20i1p1f1_scenarioSSP{scenario}.nc'
fn21 = f'F:/HMA_glacio_hydro_index/gindex_GFDL-SPEAR-MED_r21i1p1f1_scenarioSSP{scenario}.nc'
fn22 = f'F:/HMA_glacio_hydro_index/gindex_GFDL-SPEAR-MED_r22i1p1f1_scenarioSSP{scenario}.nc'
fn23 = f'F:/HMA_glacio_hydro_index/gindex_GFDL-SPEAR-MED_r23i1p1f1_scenarioSSP{scenario}.nc'
fn24 = f'F:/HMA_glacio_hydro_index/gindex_GFDL-SPEAR-MED_r24i1p1f1_scenarioSSP{scenario}.nc'
fn25 = f'F:/HMA_glacio_hydro_index/gindex_GFDL-SPEAR-MED_r25i1p1f1_scenarioSSP{scenario}.nc'
fn26 = f'F:/HMA_glacio_hydro_index/gindex_GFDL-SPEAR-MED_r26i1p1f1_scenarioSSP{scenario}.nc'
fn27 = f'F:/HMA_glacio_hydro_index/gindex_GFDL-SPEAR-MED_r27i1p1f1_scenarioSSP{scenario}.nc'
fn28 = f'F:/HMA_glacio_hydro_index/gindex_GFDL-SPEAR-MED_r28i1p1f1_scenarioSSP{scenario}.nc'
fn29 = f'F:/HMA_glacio_hydro_index/gindex_GFDL-SPEAR-MED_r29i1p1f1_scenarioSSP{scenario}.nc'
fn30 = f'F:/HMA_glacio_hydro_index/gindex_GFDL-SPEAR-MED_r30i1p1f1_scenarioSSP{scenario}.nc'

da1 = xr.open_dataset(fn1).xvec.decode_cf()
da2 = xr.open_dataset(fn2).xvec.decode_cf()
da3 = xr.open_dataset(fn3).xvec.decode_cf()
da4 = xr.open_dataset(fn4).xvec.decode_cf()
da5 = xr.open_dataset(fn5).xvec.decode_cf()
da6 = xr.open_dataset(fn6).xvec.decode_cf()
da7 = xr.open_dataset(fn7).xvec.decode_cf()
da8 = xr.open_dataset(fn8).xvec.decode_cf()
da9 = xr.open_dataset(fn9).xvec.decode_cf()
da10 = xr.open_dataset(fn10).xvec.decode_cf()
da11 = xr.open_dataset(fn11).xvec.decode_cf()
da12 = xr.open_dataset(fn12).xvec.decode_cf()
da13 = xr.open_dataset(fn13).xvec.decode_cf()
da14 = xr.open_dataset(fn14).xvec.decode_cf()
da15 = xr.open_dataset(fn15).xvec.decode_cf()
da16 = xr.open_dataset(fn16).xvec.decode_cf()
da17 = xr.open_dataset(fn17).xvec.decode_cf()
da18 = xr.open_dataset(fn18).xvec.decode_cf()
da19 = xr.open_dataset(fn19).xvec.decode_cf()
da20 = xr.open_dataset(fn20).xvec.decode_cf()
da21 = xr.open_dataset(fn21).xvec.decode_cf()
da22 = xr.open_dataset(fn22).xvec.decode_cf()
da23 = xr.open_dataset(fn23).xvec.decode_cf()
da24 = xr.open_dataset(fn24).xvec.decode_cf()
da25 = xr.open_dataset(fn25).xvec.decode_cf()
da26 = xr.open_dataset(fn26).xvec.decode_cf()
da27 = xr.open_dataset(fn27).xvec.decode_cf()
da28 = xr.open_dataset(fn28).xvec.decode_cf()
da29 = xr.open_dataset(fn29).xvec.decode_cf()
da30 = xr.open_dataset(fn30).xvec.decode_cf()


da_concat = xr.concat([da1, da2, da3, da4, da5, da6, da7, da8, da9, da10,
                       da11, da12, da13, da14, da15, da16, da17, da18, da19, da20,
                       da21, da22, da23, da24, da25, da26, da27, da28, da29, da30], pd.Index(list(range(1,31)), name='model'))

model_mean = da_concat.mean(dim = "model")

# encode the dataset according to xvec standards so it can be saved out
encoded = da_concat.xvec.encode_cf()
encoded.to_netcdf(f"F:/HMA_glacio_hydro_index/gindex_all_realizations_scenarioSSP{scenario}.nc", mode="w")
