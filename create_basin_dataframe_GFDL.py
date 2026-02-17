 # -*- coding: utf-8 -*-
"""
Created on Thu Jan  9 16:02:11 2025

@author: m337l400
"""

## This code is used to create an xarray dataset that consists of the mass and 
## runoff of the glaciers within the basins

import xarray as xr
import xvec
import geopandas as gpd
import pandas as pd
from multiprocessing import cpu_count
import matplotlib.pyplot as plt
import cftime
from datetime import datetime as dt


# Identify the files needed
f_mass = "F:/HMA_glacio_hydro_index/glac_mass_monthly/all_rgi_glac_mass_monthly_GFDL-SPEAR-MED_ssp585.nc"
f_runoff = "F:/HMA_glacio_hydro_index/glac_runoff_monthly/all_rgi_glac_runoff_monthly_GFDL-SPEAR-MED_ssp585.nc"
f_sh = "F:/HMA_impact_index/level_7_basins/level_7_selected/RGI_13_14_15_selected_basins.shp"

ds_mass = xr.open_dataset(f_mass)
ds_runoff = xr.open_dataset(f_runoff)
bas= gpd.read_file(f_sh)

#%%

r = 1
for i in range(30):
    realization = f'r{r}i1p1f1'
     
    f_pr = f"F:/HMA_glacio_hydro_index/precipitation/GFDL_ssp585/pr_month_downscaled_GFDL-SPEAR-MED_scenarioSSP5-85_{realization}_gr3_20150101-21001231.nc"
    
    # Open the datasets as a dask array with the chunks being each model and 12 months (a year)
    pr = xr.open_mfdataset(f_pr)
    
    # Create points from the centroids provided in the dataset
    x = ds_mass.lon.isel().data
    y = ds_mass.lat.isel().data
    pts = gpd.points_from_xy(x,y,crs='EPSG:4326')
    
    # Select one model. Create GeoDataFrames of mass and runoff that have all the monthly data and the point geometry of each glacier
    mass_df = gpd.GeoDataFrame(data=ds_mass.glac_mass_monthly.isel(realization = i, glacier=slice(None), time=slice(180,1212)),geometry=pts,columns=ds_mass.time.isel(time =slice(180,1212)), crs='EPSG:4326')
    runoff_df = gpd.GeoDataFrame(data=ds_runoff.glac_runoff_monthly.isel(realization = i, glacier=slice(None), time=slice(180,1212)),geometry=pts,columns=ds_mass.time.isel(time =slice(180,1212)), crs='EPSG:4326')
    
    # Create a GeoDataFrame that has the basin ID and the polygon geootry of each basin
    basin_ids = bas[['HYBAS_ID','geometry']]
    
    # Spatially join the basins and the mass GeoDataFrames. All glaciers will be assigned a basin ID
    mass_sjoin = mass_df.sjoin(basin_ids,how='left')
    mass_sjoin = mass_sjoin.set_index('HYBAS_ID')
    mass_sjoin = mass_sjoin.drop(columns = ['index_right', 'geometry']) # Drop the unneccesary column and the point geometry of the glaciers
    
    # Spatially join the basins and the runoff GeoDataFrames. All glaciers will be assigned a basin ID
    runoff_sjoin = runoff_df.sjoin(basin_ids,how='left')
    runoff_sjoin = runoff_sjoin.set_index('HYBAS_ID')
    runoff_sjoin = runoff_sjoin.drop(columns = ['index_right', 'geometry'])
    
    # Group by the basin ID and take the sum of all those with the same ID for both
    # the mass and runoff dataframes
    sum_glac_monthly_mass = mass_sjoin.groupby(by='HYBAS_ID').sum()
    sum_glac_monthly_runoff = runoff_sjoin.groupby(by='HYBAS_ID').sum()
    
    # Now we need to add the subbasin geometry back in with a merge based on the basin ID
    mass_df = pd.merge(sum_glac_monthly_mass, basin_ids, left_index=True, right_on='HYBAS_ID')
    runoff_df = pd.merge(sum_glac_monthly_runoff, basin_ids, left_index=True, right_on='HYBAS_ID')
                       
    # Turn the basin geometry, basin area, mass data, and runoff data into arrays so that they 
    #  can be added to the new dataset later
    geom = mass_df.set_geometry('geometry')
    basin_data = mass_df["geometry"].to_numpy()
    mass_data = mass_df.iloc[:,:-2].values
    runoff_data = runoff_df.iloc[:,:-2].values
    new_bas= bas[bas.HYBAS_ID.isin(mass_df.HYBAS_ID)]
    new_bas = new_bas.set_geometry("geometry",crs='EPSG:4326')
    area_data = new_bas["SUB_AREA"].to_numpy()
    
    
    ## Convert the weird cftime data to strings, make the strings a list, make the 
    ##  string datetimes. Now the dates can be used as the time array later
    mass_df.columns = [i.strftime('%Y-%m') if isinstance(i, cftime.DatetimeNoLeap) else i for i in mass_df.columns]
    string_list = list(mass_df.columns[:-2])
    mass_df.columns = [dt.strptime(i, "%Y-%m") if i in string_list else i for i in mass_df.columns]
    
    # Create the new dataset with the data arrays
    da= xr.Dataset(
        data_vars=dict(
            mass=(["geometry", "time"], mass_data),
            runoff=(["geometry", "time"], runoff_data),
    #        basins = (["HYBAS_ID"], basin_data),
            area = (["HYBAS_ID"], area_data)
        ),
        coords=dict(
            HYBAS_ID=mass_df['HYBAS_ID'].to_numpy(),
            geometry=mass_df.geometry.to_numpy(),
            time=mass_df.columns[:-2]
        ),
    ).xvec.set_geom_indexes("geometry", crs=geom.crs)
    
    # Get the precipitation in the basins
    pr_aggregated_sum = pr.xvec.zonal_stats(
        new_bas.geometry, x_coords="longitude", y_coords="latitude", stats="sum", method = "iterate"
    )
    
    ## rechunk the precipitation (and read into memory)
    chunks = {"geometry" : 934, "time" : 12}
    pr_aggregated_sum['precipitation']= pr_aggregated_sum.precipitation.chunk(chunks)
    
    ## Only do this if you need to compute right away, otherwise leave it in dask
    pr_aggregated_sum= pr_aggregated_sum.precipitation.compute()
    
    ## merge the dataset the precipitation dataset
    ds = da.merge(pr_aggregated_sum)
    
    ## make a new variable that is the volume of the glacier by dividing by the mass
    ds = ds.assign(volume=lambda x: x.mass / 917)
    
    ## calculate Gy, Gs, and G
    ds = ds.assign(g_y=lambda x: x.runoff / (x.runoff + x.precipitation))
    ds = ds.assign(g_s=lambda x: x.volume / (x.volume + x.precipitation))
    ds = ds.assign(g_index=lambda x: (x.g_y + x.g_s) / 2)
    
    # convert the time to string so it can be saved out
    timelist = ds.time.values
    ds['time'] = [dt.strftime(i, "%m/%d/%Y") for i in timelist]
    
    # encode the dataset according to xvec standards so it can be saved out
    encoded = ds.xvec.encode_cf()
    encoded.to_netcdf(f"F:/HMA_glacio_hydro_index/gindex_GFDL-SPEAR-MED_{realization}_scenarioSSP5-85.nc", mode="w")
    
    r = r + 1