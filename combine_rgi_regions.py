# -*- coding: utf-8 -*-
"""
Created on Wed Jan  8 14:13:49 2025

@author: m337l400
"""
import xarray as xr

# identify the file names
fn1 = "F:/HMA_glacio_hydro_index/glac_runoff_monthly/13/R13_glac_runoff_monthly_ensemble_ssp245_combined.nc"
fn2 = "F:/HMA_glacio_hydro_index/glac_runoff_monthly/14/R14_glac_runoff_monthly_ensemble_ssp245_combined.nc"
fn3 = "F:/HMA_glacio_hydro_index/glac_runoff_monthly/15/R15_glac_runoff_monthly_ensemble_ssp245_combined.nc"

# open the files and combine on the "glacier" dimension
com = xr.open_mfdataset([fn1,fn2,fn3], combine='nested', concat_dim = 'glacier') #this open loads them as dask arrays

# delete the region attribute
del com.attrs["Region"]

# save to file
com.to_netcdf("F:/HMA_glacio_hydro_index/glac_runoff_monthly/all_rgi_glac_runoff_monthly_ensemble_ssp245.nc")
