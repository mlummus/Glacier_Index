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
`major_hydrobasin_analysis_GI.py` creates Figure 2 of the manuscript. Used to compare the Glacier Index in the small-scale basins vs the major hydro-basins. Can be edited for any season and both SSPs. Note: The basin & mountain range labels in Figure 2 were added later in Illustrator

## trajectory_clustering_and_fig3.py
`trajectory_clustering_and_fig3.py` creates Figure 3 of the manuscript. Uses kmeans clustering to group the trajectory of the Glacier Index of each basin into three groups: steady decline, stability, and rapid collapse. Plots the clusters with representative basins for each group, chosen for their proximity in the same major basin. Each basin also has the season of maximum G throughout the timeseries plotted in a strip beneath the respective graphs. Plots a map of all the basins colored by cluster.

## relative_change.py
`relative_change.py` helps create Figure 4 of the manuscript. Finds the relative change of each of the seasons from the beginning of the century to the end. There are plot options for different types of plots: One figure that shows a map of each of the 4 seasons, one figure that compares the SSPs of one season, and one that just shows one map of the relative change. The code can be edited to plot Glacier Storage and Glacier Yield. We used the last section to create the maps that were then put into illustrator and resized to make Figure 4.

## scenario_divergence_block_bootstrap_figure5.py
`scenario_divergence_block_bootstrap_figure5.py` creates Figure 5 of the manuscript. We pair each basin's 2100 summer Glacier Index under SSP2-4.5 with its value under SSP5-8.5, grouped basins into the four magnitude categories, and tested the mean scenario difference within each group. We use a spatial block-bootstrap to measure the confidence interval of out findings. We also compare the two scenarios with a 1-to-1 line to demonstrate how each magnitude category differs between scenarios.

## figure6_ssp_compare_timeseries_with_ribbon.py
`figure6_ssp_compare_timeseries_with_ribbon.py` creates Figure 6 of the manuscript. Here we compare the different scenarios of four example basins from the different magnitude categories. We show the season of maximum G for every year between 2015-2100 in a strip below each example.

## figure7_index_formulation.py
`figure7_index_formulation.py` Contour plot of Glacier Index over the full [0,1]x[0,1] Yield-Storage space, with three annotated example points along the G=0.5 contour (Storage=0.95/Yield=0.05; Storage=0.50/Yield=0.50; Storage=0.05/Yield=0.95) showing that a single Glacier Index value can result from very different underlying physical situations. Actual basin-month Storage/Yield pairs are scattered lightly in the background for context

## climate_drivers_fig8.py
`climate_drivers_fig8.py` Climatic driver attribution for Glacier Index change. Disentangles the independent roles of temperature change and precipitation change in driving relative Glacier Index change (multivariate regression, spatially-aware CIs, collinearity check). Classifies basins by monsoon vs. westerlies dominance (summer share of annual precipitation) and tests whether climatic driver importance differs between regimes. Figures 'fig8_panelA_monsoon_map' and 'fig_climate_driver_coefficients' are used to create Figure 8 of the maunscript
