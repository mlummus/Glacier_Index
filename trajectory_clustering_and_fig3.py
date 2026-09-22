"""
Figure 3 (final): trajectory patterns (left) + basin map (right), using
the basin polygons (summer_245_gdf.shp and the major hydrologic basin
boundaries (major_hydrobasins_selected.shp) for the Ganges-Brahmaputra
outline. Representative basins: 752 (rapid collapse), 757 (steady
decline), 753 (stability) all within the Ganges-Brahmaputra
basin and within 171 km of each other.

Season-of-max-GI strips show, for the representative basin only, the
season of maximum Glacier Index in each year (2015-2100), aligned to
the same year axis as the trajectory plot above it.

"""

import numpy as np
import xarray as xr
import geopandas as gpd
import xvec
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.collections import PatchCollection
from matplotlib.patches import Polygon as MplPolygon
from sklearn.cluster import KMeans

## Load data

scenario = '2-45'
fn1 = f'F:/HMA_glacio_hydro_index/gindex_all_models_scenarioSSP{scenario}.nc'
ds = xr.open_dataset(fn1).xvec.decode_cf().mean(dim= "model")
basins_gdf= gpd.GeoDataFrame(ds.geometry, columns=["geometry"]).set_crs(epsg=4326, allow_override=True)

major_gdf = gpd.read_file("F:\HMA_glacio_hydro_index\level_3_basins\major_hydrobasins_selected.shp")

gy = ds["gy"].values
gs = ds["gs"].values
years_arr = ds.time.dt.year.values
months_arr = ds.time.dt.month.values
summer = np.isin(months_arr, [6, 7, 8])
G = 0.5 * gy + 0.5 * gs
n_basins = G.shape[0]
native_id = np.arange(n_basins) 


#%% Trajectory clustering (k=3)

year_range = np.arange(2015, 2101)
traj = np.full((n_basins, len(year_range)), np.nan)
for i, yr in enumerate(year_range):
    mask = summer & (years_arr == yr)
    traj[:, i] = np.nanmean(G[:, mask], axis=1)

baseline = np.nanmean(traj[:, (year_range >= 2015) & (year_range <= 2025)], axis=1)
valid = baseline > 0.01
traj_norm = traj[valid] / baseline[valid, None]
native_id_valid = native_id[valid]

km3 = KMeans(n_clusters=3, n_init=10, random_state=42).fit(traj_norm)
labels = km3.labels_

REP_BASINS = {757: "Steady decline", 753: "Stability", 752: "Rapid collapse"}
cluster_for_basin = {}
for b in REP_BASINS:
    idx = np.where(native_id_valid == b)[0][0]
    cluster_for_basin[b] = labels[idx]
    print(f"Basin {b} ({REP_BASINS[b]}): cluster {labels[idx]}")

cluster_order = sorted(set(labels), key=lambda c: np.nanmean(traj_norm[labels == c][:, -1]))
pattern_labels = {}
for b, name in REP_BASINS.items():
    pattern_labels[cluster_for_basin[b]] = name
colors = ["#2b6cb0", "#38a169", "#c05621"]
cluster_color = {c: colors[i] for i, c in enumerate(cluster_order)}

# Season-of-max-GI color scheme 
season_map = {12: "Winter", 1: "Winter", 2: "Winter", 3: "Spring", 4: "Spring", 5: "Spring",
              6: "Summer", 7: "Summer", 8: "Summer", 9: "Fall", 10: "Fall", 11: "Fall"}
seasons_arr = np.array([season_map[m] for m in months_arr])
season_color = {"Winter": "#C9BFE8", "Spring": "#F2EFA0", "Summer": "#B8DDB0", "Fall": "#F0CE9E"}


#%% Build figure: 3 trajectory panels (with per-basin, per-year season strips) 

plt.rcParams.update({"font.size": 10.5, "figure.dpi": 150})
fig = plt.figure(figsize=(15, 9))
gs_fig = fig.add_gridspec(3, 2, width_ratios=[1.15, 1], height_ratios=[1, 1, 1], hspace=0.55, wspace=0.25)

trajectory_axes = [fig.add_subplot(gs_fig[i, 0]) for i in range(3)]
strip_axes = [ax.inset_axes([0, -0.16, 1, 0.06]) for ax in trajectory_axes]

for panel_i, c in enumerate(cluster_order):
    ax = trajectory_axes[panel_i]
    strip_ax = strip_axes[panel_i]
    members = np.where(labels == c)[0]
    for m in members:
        ax.plot(year_range, traj_norm[m], color=colors[panel_i], alpha=0.06, lw=0.8)

    rep_basin = [b for b, cl in cluster_for_basin.items() if cl == c][0]
    rep_idx = np.where(native_id_valid == rep_basin)[0][0]
    ax.plot(year_range, traj_norm[rep_idx], color="black", lw=2.0, label=f"Representative: Basin {rep_basin}")
    ax.axhline(1.0, color="gray", lw=0.5, ls=":")
    n_members = len(members)
    pct = n_members / len(native_id_valid) * 100
    label_name = pattern_labels.get(c, f"Cluster {c}")
    ax.set_title(f"{label_name} (n={n_members} basins, {pct:.1f}% of dataset)", fontsize=10.5)
    ax.set_ylabel("GI / 2015-2025 Baseline", fontsize=9.5)
    ax.legend(fontsize=8, loc="upper right")
    ax.set_xticklabels([])
    ax.set_xlim(year_range[0], year_range[-1])

    # season of max GI, per YEAR, for the representative basin only
    yearly_season = []
    for yr in year_range:
        yr_mask = years_arr == yr
        means = {s: np.nanmean(G[rep_basin][yr_mask & (seasons_arr == s)]) for s in ["Winter", "Spring", "Summer", "Fall"]}
        yearly_season.append(max(means, key=means.get))
    strip_colors = [mcolors.to_rgb(season_color[s]) for s in yearly_season]
    strip_ax.imshow([strip_colors], aspect="auto", extent=[year_range[0], year_range[-1], 0, 1])
    strip_ax.set_yticks([])
    strip_ax.set_xlim(year_range[0], year_range[-1])
    if panel_i == 2:
        strip_ax.set_xlabel(f"Year  (strip: season of max GI, Basin {rep_basin}, by year)", fontsize=8.5)
        strip_ax.tick_params(labelsize=8)
    else:
        strip_ax.set_xticklabels([])

legend_handles = [plt.Rectangle((0, 0), 1, 1, color=c) for c in season_color.values()]
fig.legend(legend_handles, season_color.keys(), loc="lower center", ncol=4,
           bbox_to_anchor=(0.29, -0.02), fontsize=9, frameon=False, title="Season of Max GI")


#%% Map panel: polygons colored by cluster + Ganges-Brahmaputra outline 

ax_map = fig.add_subplot(gs_fig[:, 1])

patch_colors = []
for i in range(n_basins):
    vidx = np.where(native_id_valid == i)[0]
    if len(vidx) == 0:
        patch_colors.append("#cccccc")
    else:
        patch_colors.append(cluster_color[labels[vidx[0]]])

basins_gdf_plot = basins_gdf.copy()
basins_gdf_plot["plot_color"] = patch_colors
basins_gdf_plot.plot(ax=ax_map, color=basins_gdf_plot["plot_color"], edgecolor="white", linewidth=0.1)

major_gdf.boundary.plot(ax=ax_map, edgecolor="#555555", linewidth=0.5, linestyle="--")
gb = major_gdf[major_gdf["MAJ_NAME"] == "Ganges - Bramaputra"]
gb.boundary.plot(ax=ax_map, edgecolor="black", linewidth=2.2)

bounds = basins_gdf.total_bounds
ax_map.set_xlim(bounds[0] - 1, bounds[2] + 1)
ax_map.set_ylim(bounds[1] - 1, bounds[3] + 1)
ax_map.set_aspect("equal")
ax_map.set_facecolor("#eef4f8")

ax_map.set_xlabel("Longitude")
ax_map.set_ylabel("Latitude")
ax_map.set_title("Basin trajectory pattern (cluster membership)\nGanges-Brahmaputra basin outlined in bold", fontsize=10.5)
legend_elements = [plt.Rectangle((0, 0), 1, 1, color=cluster_color[c], label=pattern_labels.get(c, f"Cluster {c}")) for c in cluster_order]
ax_map.legend(handles=legend_elements, loc="lower left", fontsize=9)

fig.suptitle("Basin trajectory patterns and spatial distribution", y=1.02, fontsize=13)
fig.savefig("C:/Users/m337l400/Downloads/fig3_vector.png", bbox_inches="tight")
plt.close(fig)
