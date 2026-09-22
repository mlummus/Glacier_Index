# -*- coding: utf-8 -*-
"""
Created on Tue Apr  8 13:33:11 2025

@author: m337l400
"""

import xarray as xr
import geopandas as gpd
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import contextily as cx
import xvec
from matplotlib import colors, cm


scenario = '2-45'
# fn1 = f'F:/HMA_glacio_hydro_index/gindex_GFDL-SPEAR-MED_r1i1p1f1_scenarioSSP{scenario}.nc'
fn1 = f"F:/HMA_glacio_hydro_index/gindex_all_models_scenarioSSP{scenario}.nc"

ds = xr.open_dataset(fn1).xvec.decode_cf()

## Isolate the seasons from the dataset
winter_ds = ds.g_seasonal_mean.sel(season = ds.season.dt.month.isin([12])).mean(dim= "model")
spring_ds = ds.g_seasonal_mean.sel(season = ds.season.dt.month.isin([3])).mean(dim= "model")
summer_ds = ds.g_seasonal_mean.sel(season = ds.season.dt.month.isin([6])).mean(dim= "model")
fall_ds = ds.g_seasonal_mean.sel(season = ds.season.dt.month.isin([9])).mean(dim= "model")

## get winter 10 year mean
g_winter_10yr =pd.DataFrame(winter_ds).T.rolling(10, center = True).mean()

## get spring 10 year mean 
g_spring_10yr =pd.DataFrame(spring_ds).T.rolling(10, center = True).mean()

## get summer 10 year mean 
g_summer_10yr =pd.DataFrame(summer_ds).T.rolling(10, center = True).mean()

## get fall 10 year mean 
g_fall_10yr =pd.DataFrame(fall_ds).T.rolling(10, center = True).mean()

winter_BOC = pd.Series(g_winter_10yr.iloc[5], name ='BOC')
spring_BOC = pd.Series(g_spring_10yr.iloc[5], name = 'BOC')
summer_BOC = pd.Series(g_summer_10yr.iloc[5], name = 'BOC')
fall_BOC = pd.Series(g_fall_10yr.iloc[5], name = 'BOC')

winter_EOC = pd.Series(g_winter_10yr.iloc[81], name = 'EOC')
spring_EOC = pd.Series(g_spring_10yr.iloc[81], name = 'EOC')
summer_EOC = pd.Series(g_summer_10yr.iloc[81], name = 'EOC')
fall_EOC = pd.Series(g_fall_10yr.iloc[81], name = 'EOC')

winter_diff = pd.Series(g_winter_10yr.iloc[81]-g_winter_10yr.iloc[5], name = 'diff')
spring_diff = pd.Series(g_spring_10yr.iloc[81]-g_spring_10yr.iloc[5], name = 'diff')
summer_diff = pd.Series(g_summer_10yr.iloc[81]-g_summer_10yr.iloc[5], name = 'diff')
fall_diff = pd.Series(g_fall_10yr.iloc[81]-g_fall_10yr.iloc[5], name = 'diff')

winter_rel_diff = pd.Series(winter_diff/(g_winter_10yr.iloc[5]), name = 'rel_diff')
spring_rel_diff = pd.Series(spring_diff/(g_spring_10yr.iloc[5]), name = 'rel_diff')
summer_rel_diff = pd.Series(summer_diff/(g_summer_10yr.iloc[5]), name = 'rel_diff')
fall_rel_diff = pd.Series(fall_diff/(g_fall_10yr.iloc[5]), name = 'rel_diff')

winter_rel_diff = winter_rel_diff * 100
spring_rel_diff = spring_rel_diff * 100
summer_rel_diff = summer_rel_diff * 100
fall_rel_diff = fall_rel_diff * 100

winter_df = pd.concat([winter_BOC, winter_EOC, winter_diff, winter_rel_diff],axis=1)
spring_df = pd.concat([spring_BOC, spring_EOC, spring_diff, spring_rel_diff],axis=1)
summer_df = pd.concat([summer_BOC, summer_EOC, summer_diff, summer_rel_diff],axis=1)
fall_df = pd.concat([fall_BOC, fall_EOC, fall_diff, fall_rel_diff],axis=1)

g_summer_gdf = gpd.GeoDataFrame(summer_df, 
                              geometry =summer_ds.geometry.values)
g_winter_gdf = gpd.GeoDataFrame(winter_df, 
                              geometry =winter_ds.geometry.values)
g_spring_gdf = gpd.GeoDataFrame(spring_df, 
                              geometry =spring_ds.geometry.values)
g_fall_gdf = gpd.GeoDataFrame(fall_df, 
                              geometry =fall_ds.geometry.values)

g_winter_gdf['rel_diff'] = np.where(g_winter_gdf["BOC"] < 0.01, np.nan, g_winter_gdf['rel_diff'])
g_spring_gdf['rel_diff'] = np.where(g_spring_gdf["BOC"] < 0.01, np.nan, g_spring_gdf['rel_diff'])
g_summer_gdf['rel_diff'] = np.where(g_summer_gdf["BOC"] < 0.01, np.nan, g_summer_gdf['rel_diff'])
g_fall_gdf['rel_diff'] = np.where(g_fall_gdf["BOC"] < 0.01, np.nan, g_fall_gdf['rel_diff'])

#%% Plots one plot of all seasons

cmap = matplotlib.cm.PuOr

fig, ((ax1, ax2),(ax3,ax4)) = plt.subplots(2, 2, figsize=(8,6), dpi = 300)
fig.suptitle(f"Glacier Index Relative Change \n Using Multi-GCM mean SSP{scenario}")


g_winter_gdf.plot(ax = ax1, column = g_winter_gdf['rel_diff'], vmin = -100, vmax = 100, 
                  cmap = cmap, edgecolor = "black", linewidth=0.1, 
             missing_kwds={
                 "color": "grey",
                 "edgecolor": "black",

                 "label": "Missing values",
             })
g_spring_gdf.plot(ax = ax2, column = g_spring_gdf['rel_diff'], vmin = -100, vmax = 100, 
                  cmap = cmap, edgecolor = "black", linewidth=0.1,
             missing_kwds={
                 "color": "grey",
                 "edgecolor": "black",

                 "label": "Missing values",
             })
g_summer_gdf.plot(ax= ax3, column = g_summer_gdf['rel_diff'], vmin = -100, vmax = 100, 
                  cmap = cmap, edgecolor = "black", linewidth=0.1,
             missing_kwds={
                 "color": "grey",
                 "edgecolor": "black",

                 "label": "Missing values",
             })
g_fall_gdf.plot(ax = ax4, column = g_fall_gdf['rel_diff'], vmin = -100, vmax = 100, 
                  cmap = cmap, edgecolor = "black", linewidth=0.1, 
             missing_kwds={
                 "color": "grey",
                 "edgecolor": "black",

                 "label": "Missing values",
             })


ax1.set_title("Winter")
ax2.set_title("Spring")
ax3.set_title("Summer")
ax4.set_title("Fall")

cbar_ax = fig.add_axes([0.95, 0.25, 0.02, 0.5])
fig.colorbar(cm.ScalarMappable(norm=colors.Normalize(vmin = -100,vmax = 100), cmap=cmap), cax=cbar_ax, label= 'Relative Change (%)')

#%% Compares SSPs

fn1 = "F:/HMA_glacio_hydro_index/gindex_all_models_scenarioSSP2-45.nc"
fn2 = "F:/HMA_glacio_hydro_index/gindex_all_models_scenarioSSP5-85.nc"
fn3 = "F:/HMA_glacio_hydro_index/orographic-regions-master/orographic-regions-master/orographic-regions.shp"
ds_245 = xr.open_dataset(fn1).xvec.decode_cf()
ds_585 = xr.open_dataset(fn2).xvec.decode_cf()
oro= gpd.read_file(fn3)

summer_245 = ds_245.g_seasonal_mean.sel(season = ds_245.season.dt.month.isin([6])).mean(dim= "model")
summer_585 = ds_585.g_seasonal_mean.sel(season = ds_585.season.dt.month.isin([6])).mean(dim= "model")

summer_10yr_245 =pd.DataFrame(summer_245).T.rolling(10, center = True).mean()
summer_10yr_585 =pd.DataFrame(summer_585).T.rolling(10, center = True).mean()

summer_245_BOC = pd.Series(summer_10yr_245.iloc[5], name = 'BOC')
summer_585_BOC = pd.Series(summer_10yr_585.iloc[5], name = 'BOC')

summer_245_EOC = pd.Series(summer_10yr_245.iloc[81], name = 'EOC')
summer_585_EOC = pd.Series(summer_10yr_585.iloc[81], name = 'EOC')

summer_245_diff = pd.Series(summer_245_EOC-summer_245_BOC, name = "diff")
summer_585_diff = pd.Series(summer_585_EOC-summer_585_BOC, name = "diff")

summer_245_rel_diff = pd.Series(summer_245_diff/(summer_245_BOC), name = 'rel_diff')
summer_585_rel_diff = pd.Series(summer_585_diff/(summer_585_BOC), name = 'rel_diff')

summer_245_df = pd.concat([summer_245_BOC, summer_245_EOC, summer_245_diff, summer_245_rel_diff],axis=1)
summer_585_df = pd.concat([summer_585_BOC, summer_585_EOC, summer_585_diff, summer_585_rel_diff],axis=1)

summer_245_gdf = gpd.GeoDataFrame(summer_245_df, 
                              geometry =summer_245.geometry.values)
summer_585_gdf = gpd.GeoDataFrame(summer_585_df, 
                              geometry =summer_585.geometry.values)

summer_245_gdf['rel_diff'] = np.where(summer_245_gdf["BOC"] < 0.01, np.nan, summer_245_gdf['rel_diff'])
summer_585_gdf['rel_diff'] = np.where(summer_585_gdf["BOC"] < 0.01, np.nan, summer_585_gdf['rel_diff'])

summer_245_gdf['rel_diff'] = summer_245_gdf['rel_diff']* 100
summer_585_gdf['rel_diff'] = summer_585_gdf['rel_diff'] * 100

cmap1 = matplotlib.cm.PuOr
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8,6), dpi = 300)
#fig.suptitle(f"Glacier Index Difference from Beginning to End of Century \n Using GFDL-SPEAR-MED r1i1p1f1 SSP{scenario}")


summer_245_gdf.plot(ax = ax1, column = summer_245_gdf['rel_diff'], vmin = -100, vmax = 100, 
                  cmap = cmap1, edgecolor = "black", linewidth=0.1, missing_kwds={
                 "color": "grey",
                 "edgecolor": "black",
                 "label": "Missing values",
             })
summer_585_gdf.plot(ax= ax2, column = summer_585_gdf['rel_diff'], vmin = -100, vmax = 100, 
                  cmap = cmap1, edgecolor = "black", linewidth=0.1, missing_kwds={
                 "color": "grey",
                 "edgecolor": "black",
                 "label": "Missing values",
             })

# ax1.scatter(oro.geometry.centroid.x, oro.geometry.centroid.y, s= 0.5, facecolor="black")
# ax2.scatter(oro.geometry.centroid.x, oro.geometry.centroid.y, s= 0.5, facecolor="black")

# oro.plot(ax=ax1, facecolor= "None", edgecolor = "black", linewidth=0.1)
# oro.plot(ax=ax2, facecolor= "None", edgecolor = "black", linewidth=0.1)

# for x, y, label in zip(oro.geometry.centroid.x, oro.geometry.centroid.y, oro.FULL_NAME):
#     ax1.annotate(label, xy=(x, y), xytext=(-2, 0.3), textcoords="offset fontsize", fontsize= 6)


ax1.set_title("Relative Change Summer G SSP245")
ax2.set_title("Relative Change Summer G SSP585")

cbar_ax = fig.add_axes([0.95, 0.37, 0.02, 0.25])

fig.colorbar(cm.ScalarMappable(norm=colors.Normalize(vmin = -100,vmax = 100), cmap=cmap1), 
             cax=cbar_ax, label= 'Relative Change (%)')
cx.add_basemap(ax1, crs=ds.geometry.crs.to_string(), source=cx.providers.Esri.WorldPhysical, attribution_size=1)
cx.add_basemap(ax2, crs=ds.geometry.crs.to_string(), source=cx.providers.Esri.WorldPhysical, attribution_size=1)

#%%

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

fn1 = "F:/HMA_glacio_hydro_index/gindex_all_models_scenarioSSP2-45.nc"
ds_245 = xr.open_dataset(fn1).xvec.decode_cf()
fn2= "F:/HMA_glacio_hydro_index/level_3_basins/major_hydrobasins_selected.shp"
maj = gpd.read_file(fn2)

min_g = pd.DataFrame(ds_245.g_index.mean(dim="model")).T.idxmin()
gdf = gpd.GeoDataFrame(min_g, geometry = ds_245.geometry.values)

fig, ax1 = plt.subplots(1, 1, figsize=(8,16), dpi = 300)


# ax1.set_extent([65,110,20,50], crs = "EPSG:4326")
ax1.set_xlim(65,107)
ax1.set_ylim(20,50)
# cbar_ax = fig.add_axes([0.95, 0.25, 0.02, 0.5])
# fig.colorbar(cm.ScalarMappable(norm=colors.Normalize(vmin = 50,vmax = 1031), cmap=cmap), cax=cbar_ax)
cx.add_basemap(ax1, crs=ds_245.geometry.crs.to_string(), source=cx.providers.Esri.WorldPhysical, attribution_size=1, alpha=0.5)

ax1.xaxis.set_major_formatter(FuncFormatter(lon_formatter))
ax1.yaxis.set_major_formatter(FuncFormatter(lat_formatter))

plt.xticks(fontsize=14)  # Set font size for x-axis tick labels
plt.yticks(fontsize=14)  # Set font size for y-axis tick labels

cmap1 = matplotlib.cm.PuOr
# cmap1 = matplotlib.cm.Blues

summer_585_gdf.plot(ax = ax1, column = summer_585_gdf['rel_diff'], vmin = -100, vmax = 100, 
                  cmap = cmap1, edgecolor = "black", linewidth=0.1, missing_kwds={
                 "color": "grey",
                 "edgecolor": "black",
                 "label": "Missing values",
             })

maj.plot(ax = ax1, facecolor = "none", edgecolor = "navy", linewidth=0.3)
         
cbar_ax = fig.add_axes([0.92, 0.35, 0.02, 0.30])

fig.colorbar(cm.ScalarMappable(norm=colors.Normalize(vmin = -100,vmax = 100), cmap=cmap1), 
              cax=cbar_ax).set_label(label= 'Relative Difference (%)' , size=14)

# fig.colorbar(cm.ScalarMappable(norm=colors.Normalize(vmin = 0,vmax = 1), cmap=cmap1), 
#               cax=cbar_ax).set_label(label= 'Glacier Index' , size=14)

cbar_ax.tick_params(labelsize=14)
cx.add_basemap(ax1, crs=ds.geometry.crs.to_string(), source=cx.providers.Esri.WorldPhysical, attribution_size=1)
# b=628
# bas1 = gpd.GeoDataFrame(gdf.iloc[b]).T.set_geometry("geometry")
# # b=250
# # bas2 = gpd.GeoDataFrame(gdf.iloc[b]).T.set_geometry("geometry")
# b=2
# bas3 = gpd.GeoDataFrame(gdf.iloc[b]).T.set_geometry("geometry")
# b=312
# bas4 = gpd.GeoDataFrame(gdf.iloc[b]).T.set_geometry("geometry")
# b=905
# bas5 = gpd.GeoDataFrame(gdf.iloc[b]).T.set_geometry("geometry")
# b=171
# bas6 = gpd.GeoDataFrame(gdf.iloc[b]).T.set_geometry("geometry")
# # b=402
# # bas7 = gpd.GeoDataFrame(gdf.iloc[b]).T.set_geometry("geometry")
# # b=21
# # bas8 = gpd.GeoDataFrame(gdf.iloc[b]).T.set_geometry("geometry")
# # b=906
# # bas9 = gpd.GeoDataFrame(gdf.iloc[b]).T.set_geometry("geometry")
# # b=712
# # bas10 = gpd.GeoDataFrame(gdf.iloc[b]).T.set_geometry("geometry")
# # b=741
# # bas11 = gpd.GeoDataFrame(gdf.iloc[b]).T.set_geometry("geometry")
# b=738
# bas12 = gpd.GeoDataFrame(gdf.iloc[b]).T.set_geometry("geometry")
# # b=559
# # bas13 = gpd.GeoDataFrame(gdf.iloc[b]).T.set_geometry("geometry")


# bas1.plot(ax=ax1, facecolor= "none", edgecolor = "#ce5160", linewidth=1.5)
# # bas2.plot(ax=ax1, facecolor= "none", edgecolor = "#677fd8", linewidth=1.5)
# bas3.plot(ax=ax1, facecolor= "none", edgecolor = "#92b440", linewidth=1.5)
# bas4.plot(ax=ax1, facecolor= "none", edgecolor = "#58388b", linewidth=1.5)
# bas5.plot(ax=ax1, facecolor= "none", edgecolor = "#5cbf77", linewidth=1.5)
# bas6.plot(ax=ax1, facecolor= "none", edgecolor = "#bf73cb", linewidth=1.5)
# # bas7.plot(ax=ax1, facecolor= "none", edgecolor = "#578836", linewidth=1.5)
# # bas8.plot(ax=ax1, facecolor= "none", edgecolor = "#b34f8e", linewidth=1.5)
# # bas9.plot(ax=ax1, facecolor= "none", edgecolor = "#43c9b0", linewidth=1.5)
# # bas10.plot(ax=ax1, facecolor= "none", edgecolor = "#bb486a", linewidth=1.5)
# # bas11.plot(ax=ax1, facecolor= "none", edgecolor = "#d19e34", linewidth=1.5)
# bas12.plot(ax=ax1, facecolor= "none", edgecolor = "#b94b45", linewidth=1.5)
# # bas13.plot(ax=ax1, facecolor= "none", edgecolor = "#ac9747", linewidth=1.5)