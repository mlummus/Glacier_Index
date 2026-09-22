# Glacier_Index
Code used to create a Glacio-Hydrologic Index for High Mountain Asia. Data needed to execute this code can be found on Zenodo at DOI: 10.5281/zenodo.18686202

# Python File Descriptions
## combine_pygem_batches.py
`combine_pygem_batches.py` reads the PyGEM batch files and creates an xarray dataframe with all batches contained. Repeat this code for datasets with glacier mass and glacier runoff for regions 13, 14, and 15 for SSP2-4.5 and SSP5-8.5. Repeat for both singular climate model files and the GFDL-SPEAR-MED files. You should have 24 files in the end.
1. R15_glac_mass_monthly_ensemble_ssp245_combined.nc
2. R15_glac_mass_monthly_ensemble_ssp585_combined.nc
3. R15_glac_mass_monthly_GFDL-SPEAR-MED_ssp245_combined.nc
4. R15_glac_mass_monthly_GFDL-SPEAR-MED_ssp585_combined.nc
5. R15_glac_runoff_monthly_ensemble_ssp245_combined.nc
6. R15_glac_runoff_monthly_ensemble_ssp585_combined.nc
7. R15_glac_runoff_monthly_GFDL-SPEAR-MED_ssp245_combined.nc
8. R15_glac_runoff_monthly_GFDL-SPEAR-MED_ssp585_combined.nc
9. R14_glac_mass_monthly_ensemble_ssp245_combined.nc
10. R14_glac_mass_monthly_ensemble_ssp585_combined.nc
11. R14_glac_mass_monthly_GFDL-SPEAR-MED_ssp245_combined.nc
12. R14_glac_mass_monthly_GFDL-SPEAR-MED_ssp585_combined.nc
13. R14_glac_runoff_monthly_ensemble_ssp245_combined.nc
14. R14_glac_runoff_monthly_ensemble_ssp585_combined.nc
15. R14_glac_runoff_monthly_GFDL-SPEAR-MED_ssp245_combined.nc
16. R14_glac_runoff_monthly_GFDL-SPEAR-MED_ssp585_combined.nc
17. R13_glac_mass_monthly_ensemble_ssp245_combined.nc
18. R13_glac_mass_monthly_ensemble_ssp585_combined.nc
19. R13_glac_mass_monthly_GFDL-SPEAR-MED_ssp245_combined.nc
10. R13_glac_mass_monthly_GFDL-SPEAR-MED_ssp585_combined.nc
21. R13_glac_runoff_monthly_ensemble_ssp245_combined.nc
22. R13_glac_runoff_monthly_ensemble_ssp585_combined.nc
23. R13_glac_runoff_monthly_GFDL-SPEAR-MED_ssp245_combined.nc
24. R13_glac_runoff_monthly_GFDL-SPEAR-MED_ssp585_combined.nc
## combine_rgi_regions.py
`combine_rgi_regions.py` combines the PyGEM files from the three RGI regions into one xarray dataframe. Repeat this code for glacier mass and glacier runoff for SSP2-4.5 and SSP5-8.5. You should now have 8 files.
1. all_rgi_glac_mass_monthly_ensemble_ssp245.nc
2. all_rgi_glac_mass_monthly_ensemble_ssp585.nc
3. all_rgi_glac_mass_monthly_GFDL-SPEAR-MED_ssp245.nc
4. all_rgi_glac_mass_monthly_GFDL-SPEAR-MED_ssp585.nc
5. all_rgi_glac_runoff_monthly_ensemble_ssp245.nc
6. all_rgi_glac_runoff_monthly_ensemble_ssp585.nc
7. all_rgi_glac_runoff_monthly_GFDL-SPEAR-MED_ssp245.nc
8. all_rgi_glac_runoff_monthly_GFDL-SPEAR-MED_ssp585.nc
## create_basin_dataframe.py 
`create_basin_dataframe.py` creates an xarray dataset that consists of the mass, runoff, Glacier Index, Glacier Storage, and Glacier Yield of the glaciers within the basins using the corresponding precipitation data. Repeat for SSP245 and SSP585. You should have 16 files: 2 per climate model
## create_basin_dataframe_GFDL.py
`create_basin_dataframe_GFDL.py` creates an xarray dataset that consists of the mass, runoff, Glacier Index, Glacier Storage, and Glacier Yield of the glaciers within the basins using the corresponding precipitation data from all 30 GFDL-SPEAR-MED realizations. Repeat for SSP245 and SSP585. You should have 60 files: 2 per climate realization
## fix_g.py
`fix_g.py` was used to ensure that G calculations were based on water volumes.
## save_combined_netcdf.py
`save_combined_netcdf.py`combines the Glacier Index datasets created with the different climate models into one dataset. Combines the Glacier Index created with different GFDL-SPEAR-MED realizations into one dataset.

## major_hydrobasin_analysis_GI.py
`create_basin_dataframe.py` creates Figure 2 of the manuscript. Used to compare the Glacier Index in the small-scale basins vs the major hydro-basins. Can be edited for any season and both SSPs. Note: The basin & mountain range labels in Figure 2 were added later in Illustrator

## trajectory_clustering_and_fig3.py
`trajectory_clustering_and_fig3.py` creates Figure 3 of the manuscript. Uses kmeans clustering to group the trajectory of the Glacier Index of each basin into three groups: steady decline, stability, and rapid collapse. Plots the clusters with representative basins for each group, chosen for their proximity in the same major basin. Each basin also has the season of maximum G throughout the timeseries plotted in a strip beneath the respective graphs. Plots a map of all the basins colored by cluster.
