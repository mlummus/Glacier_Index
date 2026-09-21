# -*- coding: utf-8 -*-
"""
Created on Wed Oct  8 11:33:27 2025

@author: m337l400
"""

## This code will create Figure 2 of the manuscript. Used to compare the 
## Glacier Index in the small-scale basins vs the major hydro-basins. Can be 
## edited for any season and both SSPs
## Note: The basin & mountain range labels in Figure 2 were added in Illustrator 

import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import contextily as cx
import cartopy.crs as ccrs
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
from matplotlib import colors, cm
import matplotlib
from mpl_toolkits.axes_grid1 import make_axes_locatable
import xarray as xr
import xvec
import math
import numpy as np

## Load in the datasets
scenario = '2-45'
fn1 = f'F:/HMA_glacio_hydro_index/gindex_all_models_scenarioSSP{scenario}.nc'
ds = xr.open_dataset(fn1).xvec.decode_cf()
gdf = gpd.GeoDataFrame().set_geometry(ds.geometry.values)
gdf= gdf.set_crs("EPSG:4326")

# major_fn = "F:/HMA_glacio_hydro_index/level_3_basins/level_3_selected.shp"
major_fn = "F:/HMA_glacio_hydro_index/level_3_basins/major_hydrobasins_selected.shp"
major = gpd.read_file(major_fn).set_geometry("geometry")
major['geometry'] = major['geometry'].make_valid()

#%%
## Isolate the seasons from the dataset
winter_ds = ds.g_seasonal_mean.sel(season = ds.season.dt.month.isin([12])).mean(dim= "model")
spring_ds = ds.g_seasonal_mean.sel(season = ds.season.dt.month.isin([3])).mean(dim= "model")
summer_ds = ds.g_seasonal_mean.sel(season = ds.season.dt.month.isin([6])).mean(dim= "model")
fall_ds = ds.g_seasonal_mean.sel(season = ds.season.dt.month.isin([9])).mean(dim= "model")

## get seasonal 10 year mean
g_winter_10yr =pd.DataFrame(winter_ds).T.rolling(10, center = True).mean()
g_spring_10yr =pd.DataFrame(spring_ds).T.rolling(10, center = True).mean()
g_summer_10yr =pd.DataFrame(summer_ds).T.rolling(10, center = True).mean()
g_fall_10yr =pd.DataFrame(fall_ds).T.rolling(10, center = True).mean()


## get the centroids of the small-scale basins
poly = gpd.GeoSeries(ds.geometry.values)
pts = poly.centroid

## winter
g = gpd.GeoDataFrame(g_winter_10yr.T).set_geometry(pts).set_crs("EPSG:4326")
gw = gpd.GeoDataFrame(g_winter_10yr.T).set_geometry(poly).set_crs("EPSG:4326")
combined = g.sjoin(major[["MAJ_NAME","geometry"]],how='left')
combined = combined.drop('geometry',axis=1)
maj_g = combined.groupby("MAJ_NAME").mean()
maj_g = maj_g.drop('index_right', axis = 1)
merged = pd.merge(maj_g, major[["MAJ_NAME","geometry"]], left_index=True, right_on='MAJ_NAME')
winter = merged.set_index("MAJ_NAME")

## spring
g = gpd.GeoDataFrame(g_spring_10yr.T).set_geometry(pts).set_crs("EPSG:4326")
gsp = gpd.GeoDataFrame(g_spring_10yr.T).set_geometry(poly).set_crs("EPSG:4326")
combined = g.sjoin(major[["MAJ_NAME","geometry"]],how='left')
combined = combined.drop('geometry',axis=1)
maj_g = combined.groupby("MAJ_NAME").mean()
maj_g = maj_g.drop('index_right', axis = 1)
merged = pd.merge(maj_g, major[["MAJ_NAME","geometry"]], left_index=True, right_on='MAJ_NAME')
spring = merged.set_index("MAJ_NAME")

## summer
g = gpd.GeoDataFrame(g_summer_10yr.T).set_geometry(pts).set_crs("EPSG:4326")
gsu = gpd.GeoDataFrame(g_summer_10yr.T).set_geometry(poly).set_crs("EPSG:4326")
combined = g.sjoin(major[["MAJ_NAME","geometry"]],how='left')
combined = combined.drop('geometry',axis=1)
maj_g = combined.groupby("MAJ_NAME").mean()
maj_g = maj_g.drop('index_right', axis = 1)
merged = pd.merge(maj_g, major[["MAJ_NAME","geometry"]], left_index=True, right_on='MAJ_NAME')
summer = merged.set_index("MAJ_NAME")


## fall
g = gpd.GeoDataFrame(g_fall_10yr.T).set_geometry(pts).set_crs("EPSG:4326")
gf = gpd.GeoDataFrame(g_fall_10yr.T).set_geometry(poly).set_crs("EPSG:4326")
combined = g.sjoin(major[["MAJ_NAME","geometry"]],how='left')
combined = combined.drop('geometry',axis=1)
maj_g = combined.groupby("MAJ_NAME").mean()
maj_g = maj_g.drop('index_right', axis = 1)
merged = pd.merge(maj_g, major[["MAJ_NAME","geometry"]], left_index=True, right_on='MAJ_NAME')
fall = merged.set_index("MAJ_NAME")

#%% Plots all seasons in one figure  

cmap = matplotlib.cm.Blues
# cmap = cmap.reversed()

fig, ((ax1, ax2),(ax3,ax4)) = plt.subplots(2, 2, figsize=(8,6), dpi = 300)
# fig.suptitle(f"Relative Chance of Glacier Index \n Using multi-GCM mean SSP{scenario}")
# plt.subplots_adjust(top = 3, bottom=1, hspace=3, wspace=1)

winter = winter.set_geometry("geometry")
winter.plot(ax = ax1, column = winter[81], vmin = 0, vmax = 1, 
                  cmap = cmap, edgecolor = "black", linewidth=0.1)
gw.plot(ax=ax1, column = gw[81], vmin=0, vmax=1, cmap = cmap, edgecolor = "black", linewidth=0.1)
winter.plot(ax = ax1, facecolor = "none", edgecolor = "black", linewidth=0.1)

spring = spring.set_geometry("geometry")
spring.plot(ax = ax2, column = spring[81], vmin = 0, vmax = 1, 
                  cmap = cmap, edgecolor = "black", linewidth=0.1)
gsp.plot(ax=ax2, column = gsp[81], vmin=0, vmax=1, cmap = cmap, edgecolor = "black", linewidth=0.1)
spring.plot(ax = ax2, facecolor = "none", edgecolor = "black", linewidth=0.1)

summer = summer.set_geometry("geometry")
summer.plot(ax= ax3, column = summer[81], vmin = 0, vmax = 1, 
                  cmap = cmap, edgecolor = "black", linewidth=0.1)
gsu.plot(ax=ax3, column = gsu[81], vmin=0, vmax=1, cmap = cmap, edgecolor = "black", linewidth=0.1)
summer.plot(ax = ax3, facecolor = "none", edgecolor = "black", linewidth=0.1)

fall = fall.set_geometry("geometry")
fall.plot(ax = ax4, column = fall[81], vmin = 0, vmax = 1, 
                  cmap = cmap, edgecolor = "black", linewidth=0.1)
gf.plot(ax=ax4, column = gf[81], vmin=0, vmax=1, cmap = cmap, edgecolor = "black", linewidth=0.1)
fall.plot(ax = ax4, facecolor = "none", edgecolor = "black", linewidth=0.1)

ax1.set_title("Winter")
ax2.set_title("Spring")
ax3.set_title("Summer")
ax4.set_title("Fall")

cx.add_basemap(ax1, crs=gw.geometry.crs.to_string(), source=cx.providers.Esri.WorldPhysical, attribution_size=1)
cx.add_basemap(ax2, crs=gsp.geometry.crs.to_string(), source=cx.providers.Esri.WorldPhysical, attribution_size=1)
cx.add_basemap(ax3, crs=gsu.geometry.crs.to_string(), source=cx.providers.Esri.WorldPhysical, attribution_size=1)
cx.add_basemap(ax4, crs=gf.geometry.crs.to_string(), source=cx.providers.Esri.WorldPhysical, attribution_size=1)

cbar_ax = fig.add_axes([0.95, 0.25, 0.02, 0.5])
fig.colorbar(cm.ScalarMappable(norm=colors.Normalize(vmin = 0,vmax = 1), cmap=cmap), cax=cbar_ax, label= 'Glacier Index')

#%% Plots one season. Summer in this case.

# Format the map tick marks 
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

## set the color scheme
cmap = matplotlib.cm.Blues

## Start the figure and set the extent of the map
fig, ax1 = plt.subplots(1, 1, dpi = 300)
ax1.set_xlim(55,125)
ax1.set_ylim(8,55)

## Zoomed in extent
# ax1.set_xlim(65,110)
# ax1.set_ylim(25,50)

## Plot the summer Glacier Index
summer = summer.set_geometry("geometry")
summer.plot(ax= ax1, column = summer[81], vmin = 0, vmax = 1, 
                  cmap = cmap, edgecolor = "black", linewidth=0.1)
gsu.plot(ax=ax1, column = gsu[5], vmin=0, vmax=1, cmap = cmap, edgecolor = "black", linewidth=0.1)
summer.plot(ax = ax1, facecolor = "none", edgecolor = "black", linewidth=0.3)

## Call to the tickmark formatter funtion 
ax1.xaxis.set_major_formatter(FuncFormatter(lon_formatter))
ax1.yaxis.set_major_formatter(FuncFormatter(lat_formatter))

plt.xticks(fontsize=10)  # Set font size for x-axis tick labels
plt.yticks(fontsize=10)  # Set font size for y-axis tick labels

## add basemap
cx.add_basemap(ax1, crs=gsu.geometry.crs.to_string(), source=cx.providers.Esri.WorldPhysical, attribution_size=1)

## format colorbar 
cbar_ax = fig.add_axes([0.90, 0.25, 0.02, 0.5])
fig.colorbar(cm.ScalarMappable(norm=colors.Normalize(vmin = 0,vmax = 1), cmap=cmap), cax=cbar_ax)#,label= 'Glacier Index')       
cbar_ax.tick_params(labelsize=10)

## Save out. Ensure proper name 
# plt.savefig('F:/HMA_glacio_hydro_index/Figures/GI_small_and_large_basins_585.pdf',dpi=300)
