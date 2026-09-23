"""
Figure 6: 2x2 grid, A/B/C/D panel labels, one representative basin per
Glacier Index magnitude category -- Basin 356 (Precipitation-dominated),
Basin 168 (Glacier-influenced), Basin 622 (Balanced), Basin 481
(Glacier-dominated) -- with season-of-max-GI strips per scenario beneath
each panel, and a yellow outline marking the 2090-2100 window used to
classify each basin's category.


"""

import numpy as np
import pandas as pd
import xarray as xr
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

FILES = {"SSP2-4.5": "F:/HMA_glacio_hydro_index/gindex_all_models_scenarioSSP2-45.nc",
         "SSP5-8.5": "F:/HMA_glacio_hydro_index/gindex_all_models_scenarioSSP5-85.nc"}

raw = {}
for ssp, path in FILES.items():
    ds = xr.open_dataset(path)
    raw[ssp] = {
        "G": ds.g_index.mean(dim="model").values,
        "G_std": ds.g_index.std(dim="model").values,
        "months": ds.time.dt.month.values,
        "years": ds.time.dt.year.values,
    }

summer = np.isin(raw["SSP2-4.5"]["months"], [6, 7, 8])
years_arr = raw["SSP2-4.5"]["years"]
months_arr = raw["SSP2-4.5"]["months"]
late_mask = summer & (years_arr >= 2090) & (years_arr <= 2100)

n_basins = raw["SSP2-4.5"]["G"].shape[0]
native_id = np.arange(n_basins)

G_2100 = {ssp: np.nanmean(raw[ssp]["G"][:, late_mask], axis=1) for ssp in FILES}
df = pd.DataFrame({"basin_id": native_id, "G_245": G_2100["SSP2-4.5"], "G_585": G_2100["SSP5-8.5"]})
df["diff"] = df["G_585"] - df["G_245"]

def classify(g):
    if g < 0.1:
        return "Precipitation-dominated"
    elif g <= 0.4:
        return "Glacier-influenced"
    elif g > 0.5:
        return "Glacier-dominated"
    else:
        return "Balanced"
df["group"] = df["G_245"].apply(classify)

GROUP_ORDER = ["Precipitation-dominated", "Glacier-influenced", "Balanced", "Glacier-dominated"]
reps = {"Precipitation-dominated": 356, "Glacier-influenced": 168, "Balanced": 622, "Glacier-dominated": 481}
print("Representative basins:", reps)

year_range = np.arange(2015, 2101)

def annual_trajectory(ssp, basin_idx):
    G = raw[ssp]["G"][basin_idx]
    yrs = raw[ssp]["years"]
    traj = np.full(len(year_range), np.nan)
    for i, yr in enumerate(year_range):
        mask = summer & (yrs == yr)
        traj[i] = np.nanmean(G[mask])
    return traj

def annual_trajectory_ribbon(ssp, basin_idx):
    G = raw[ssp]["G"][basin_idx]
    G_std = raw[ssp]["G_std"][basin_idx]
    yrs = raw[ssp]["years"]
    traj_min = np.full(len(year_range), np.nan)
    traj_max = np.full(len(year_range), np.nan)
    for i, yr in enumerate(year_range):
        mask = summer & (yrs == yr)
        traj_min[i] = np.nanmean(G[mask])- np.nanmean(G_std[mask])
        traj_max[i] = np.nanmean(G[mask])+ np.nanmean(G_std[mask])
    return traj_min, traj_max

season_map = {12: "Winter", 1: "Winter", 2: "Winter", 3: "Spring", 4: "Spring", 5: "Spring",
              6: "Summer", 7: "Summer", 8: "Summer", 9: "Fall", 10: "Fall", 11: "Fall"}
seasons_arr = np.array([season_map[m] for m in months_arr])
season_color = {"Winter": "#C9BFE8", "Spring": "#F2EFA0", "Summer": "#B8DDB0", "Fall": "#F0CE9E"}

def season_of_max_by_year(ssp, basin_idx):
    G = raw[ssp]["G"][basin_idx]
    yrs = raw[ssp]["years"]
    out = []
    for yr in year_range:
        yr_mask = yrs == yr
        means = {s: np.nanmean(G[yr_mask & (seasons_arr == s)]) for s in ["Winter", "Spring", "Summer", "Fall"]}
        out.append(max(means, key=means.get))
    return out


#%% Plot: 2x2 grid, shorter aspect ratio, A/B/C/D labels

plt.rcParams.update({"font.size": 12, "figure.dpi": 150})
fig, axes = plt.subplots(2, 2, figsize=(14, 7.5))
panel_labels = ["A", "B", "C", "D"]
ssp_colors = {"SSP2-4.5": "#2b4a7a", "SSP5-8.5": "#e0507a"}

for panel_i, grp in enumerate(GROUP_ORDER):
    row, col = divmod(panel_i, 2)
    ax = axes[row, col]
    basin = reps[grp]

    for ssp in FILES:
        traj = annual_trajectory(ssp, basin)
        traj_min, traj_max = annual_trajectory_ribbon(ssp, basin)
        ax.plot(year_range, traj, color=ssp_colors[ssp], lw=1.6, label=ssp, zorder=3)
        ax.fill_between(year_range, traj_min, traj_max, alpha = 0.3, color=ssp_colors[ssp])

    ax.set_ylim(-0.02, 1.0)
    ax.set_xlim(year_range[0], year_range[-1])
    ax.set_ylabel("Glacier Index")
    ax.set_title(f"Basin {basin}: {grp} Example", fontsize=13, fontweight="bold", loc="left")

    # highlight the 2090-2100 classification window
    from matplotlib.patches import Rectangle
    rect = Rectangle((2090, -0.02), 10, 1.02, linewidth=1.6, edgecolor="#D4A017",
                      facecolor="none", zorder=4)
    ax.add_patch(rect)

    # season-of-max-GI strips, one per scenario, beneath the panel
    strip_ax = ax.inset_axes([0, -0.34, 1, 0.16])
    y_offset = {"SSP2-4.5": 0.5, "SSP5-8.5": 0.0}
    for ssp in FILES:
        seasons_yearly = season_of_max_by_year(ssp, basin)
        colors_row = [mcolors.to_rgb(season_color[s]) for s in seasons_yearly]
        strip_ax.imshow([colors_row], aspect="auto",
                         extent=[year_range[0], year_range[-1], y_offset[ssp], y_offset[ssp] + 0.5])
        strip_ax.text(year_range[-1] + 1.5, y_offset[ssp] + 0.25, ssp.replace("SSP", ""),
                       va="center", ha="left", fontsize=8.5)
    strip_ax.set_ylim(0, 1)
    strip_ax.set_xlim(year_range[0], year_range[-1])
    strip_ax.set_yticks([])
    strip_ax.axhline(0.5, color="black", lw=0.8)
    strip_ax.set_xlabel("Year" if row == 1 else "")
    if row == 0:
        strip_ax.set_xticklabels([])

    ax.text(-0.12, -0.45, panel_labels[panel_i], transform=ax.transAxes,
            fontsize=15, fontweight="bold", va="top")

# Legends at bottom
handles_proj = [plt.Line2D([0], [0], color=ssp_colors[s], lw=2) for s in FILES]
fig.legend(handles_proj, FILES.keys(), loc="lower center", ncol=2, fontsize=10,
           bbox_to_anchor=(0.28, -0.06), title="Projection", frameon=False)

handles_season = [plt.Rectangle((0, 0), 1, 1, color=c) for c in season_color.values()]
fig.legend(handles_season, season_color.keys(), loc="lower center", ncol=4, fontsize=10,
           bbox_to_anchor=(0.72, -0.06), title="Season of Max GI", frameon=False)

fig.text(0.5, 0.015, "Yellow outline: 2090\u20132100 window used to classify each basin's magnitude category",
         ha="center", fontsize=9.5, style="italic")

fig.tight_layout(rect=[0, 0.05, 1, 1])
# fig.savefig("F:/HMA_glacio_hydro_index/Figures/fig6_restyled.png", bbox_inches="tight")
# fig.savefig("F:/HMA_glacio_hydro_index/Figures/fig6_restyled.pdf", bbox_inches="tight")
# fig.savefig("F:/HMA_glacio_hydro_index/Figures/fig6_restyled.svg", bbox_inches="tight")
# plt.close(fig)
print("Saved fig6_restyled.png, .pdf, and .svg")
