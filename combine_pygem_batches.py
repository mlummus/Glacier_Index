# -*- coding: utf-8 -*-
"""
Created on Mon Jan  6 13:26:32 2025

@author: m337l400
"""

import xarray as xr
import glob

# template for reading batched pygem sims

# get list of files containing annual glacier runoff and mass for regions 13, 14, and 15 for SSP245 and SSP585

ds_fns = glob.glob('F:/HMA_glacio_hydro_index/glac_runoff_monthly/13/R13_glac_runoff_monthly_GFDL-SPEAR-MED_ssp585*.nc')
# ds_fns = glob.glob('F:/HMA_glacio_hydro_index/glac_runoff_monthly/14/R14_glac_runoff_monthly_GFDL-SPEAR-MED_ssp585*.nc')
# ds_fns = glob.glob('F:/HMA_glacio_hydro_index/glac_runoff_monthly/15/R15_glac_runoff_monthly_GFDL-SPEAR-MED_ssp585*.nc')

# ds_fns = glob.glob('F:/HMA_glacio_hydro_index/glac_mass_monthly/13/R13_glac_mass_monthly_GFDL-SPEAR-MED_ssp585*.nc')
# ds_fns = glob.glob('F:/HMA_glacio_hydro_index/glac_mass_monthly/14/R14_glac_mass_monthly_GFDL-SPEAR-MED_ssp585*.nc')
# ds_fns = glob.glob('F:/HMA_glacio_hydro_index/glac_mass_monthly/15/R15_glac_mass_monthly_GFDL-SPEAR-MED_ssp585*.nc')

# check for batched outputs so we can aggregate them
ds_fns_int = []                
for i in ds_fns:
    # if 'MED_ssp585_Batch' in i:
    if 'Batch' in i:
        ds_fns_int.append(int(i.split('-')[-2]))

# sort filenames
if len(ds_fns_int) > 0:
    ds_fns = [x for _,x in sorted(zip(ds_fns_int, ds_fns))]

# load data (aggregate if necessary)
for nfn, ds_fn in enumerate(ds_fns):
    if nfn == 0:
        ds = xr.open_dataset(ds_fn)
    else:
        ds_batch = xr.open_dataset(ds_fn)
        ds = xr.concat((ds, ds_batch), dim='glacier')

# ds is now a aggregated dataset with all batches contained. Save out.

# change ds_fns for each RGI region. Repeat for glacier mass