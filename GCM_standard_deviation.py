# -*- coding: utf-8 -*-
"""
Created on Wed Sep 16 14:00:57 2026

@author: m337l400
"""

import pandas as pd
import geopandas as gpd
import xarray as xr
import xvec
import matplotlib.pyplot as plt
import matplotlib
import contextily as cx

fn2 = 'F:/HMA_glacio_hydro_index/gindex_all_models_scenarioSSP2-45.nc'
fn3 = 'F:/HMA_glacio_hydro_index/gindex_all_models_scenarioSSP5-85.nc'

ds245 = xr.open_dataset(fn2).xvec.decode_cf()
ds585 = xr.open_dataset(fn3).xvec.decode_cf()
gdf245 = gpd.GeoDataFrame().set_geometry(ds245.geometry.values)
gdf245= gdf245.set_crs("EPSG:4326")


summer_ds245 = ds245.g_seasonal_mean.sel(season = ds245.season.dt.month.isin([6]))
summer_ds585 = ds585.g_seasonal_mean.sel(season = ds585.season.dt.month.isin([6]))

g_summer_245 =summer_ds245.rolling({"season":10}, center = True).mean()
g_summer_585 =summer_ds585.rolling({"season":10}, center = True).mean()


summer_diff245 = g_summer_245.isel({"season":81})-g_summer_245.isel({"season":5})
summer_diff585 = g_summer_585.isel({"season":81})-g_summer_585.isel({"season":5})

summer_rel_diff245 = (summer_diff245/ g_summer_245.isel({"season":5}))*100
summer_rel_diff585 = (summer_diff585/ g_summer_585.isel({"season":5}))*100


summer245_stdv= summer_rel_diff245.std(dim="model")
summer585_stdv= summer_rel_diff585.std(dim="model")

summer245_mean= summer_rel_diff245.mean(dim="model")
summer585_mean= summer_rel_diff585.mean(dim="model")

#summer245_stdv.to_dataset(name="stdv").xvec.encode_cf().to_netcdf("summer245_stdv.nc")
#summer585_stdv.to_dataset(name="stdv").xvec.encode_cf().to_netcdf("summer585_stdv.nc")

#%%

gdf_245 = gpd.GeoDataFrame(summer245_stdv, geometry =ds245.geometry.values)
gdf_585 = gpd.GeoDataFrame(summer585_stdv, geometry =ds245.geometry.values)

from matplotlib.ticker import FuncFormatter
def lat_formatter(x, pos):
    if x > 0:
        return f"{abs(x):g}°N"
    elif x < 0:
        return f"{abs(x):g}°S"
    else:
        return f"{x:g}°"

def lon_formatter(x, pos):
    if x > 0:
        return f"{abs(x):g}°E"
    elif x < 0:
        return f"{abs(x):g}°W"
    else:
        return f"{x:g}°"


# cmap1 = matplotlib.cm.PuOr
fig, ax = plt.subplots(1, 1, figsize=(6,8), dpi = 300)

gdf_585.plot(ax = ax, column = gdf_585[0],
                  cmap = "Greens", edgecolor = "black", linewidth=0.1, missing_kwds={
                 "color": "grey",
                 "edgecolor": "black",
                 "label": "Missing values"})

ax.set_xlim(65,107)
ax.set_ylim(20,50)
cx.add_basemap(ax, crs=ds245.geometry.crs.to_string(), source=cx.providers.Esri.WorldPhysical, attribution_size=1)


# ax.xaxis.set_major_formatter(FuncFormatter(lon_formatter))
# ax.yaxis.set_major_formatter(FuncFormatter(lat_formatter))
# ax.yaxis.tick_right()

# plt.xticks(fontsize=10)  # Set font size for x-axis tick labels
# plt.yticks(fontsize=10)  # Set font size for y-axis tick labels
