"""
Figure 7: Glacier Index Formulation.

Contour plot of G = 0.5*Yield + 0.5*Storage over the full [0,1]x[0,1]
Yield-Storage space, with three annotated example points along the
G=0.5 contour (Storage=0.95/Yield=0.05; Storage=0.50/Yield=0.50;
Storage=0.05/Yield=0.95) showing that a single Glacier Index value can
result from very different underlying physical situations. Actual
basin-month Storage/Yield pairs are scattered lightly in the
background for context.

"""

import numpy as np
import xarray as xr
import matplotlib.pyplot as plt


# Load actual basin Storage/Yield values for background scatter
#    (summer, 2090-2100, SSP2-4.5)

ds = xr.open_dataset("F:/HMA_glacio_hydro_index/gindex_all_models_scenarioSSP2-45.nc").mean(dim="model")
gy = ds["gy"].values
gs = ds["gs"].values
summer = np.isin(ds.time.dt.month.values, [6, 7, 8])
years = ds.time.dt.year.values
late_mask = summer & (years >= 2090) & (years <= 2100)

yield_pts = np.nanmean(gy[:, late_mask], axis=1)
storage_pts = np.nanmean(gs[:, late_mask], axis=1)


# Contour of G = 0.5*Yield + 0.5*Storage over full [0,1] x [0,1] space

yield_grid = np.linspace(0, 1, 300)
storage_grid = np.linspace(0, 1, 300)
Y, S = np.meshgrid(yield_grid, storage_grid)
G_grid = 0.5 * Y + 0.5 * S

plt.rcParams.update({"font.size": 12, "figure.dpi": 150})
fig, ax = plt.subplots(figsize=(7.5, 6.5))

levels = np.linspace(0, 1, 11)
cf = ax.contourf(Y, S, G_grid, levels=levels, cmap="viridis")
cbar = fig.colorbar(cf, ax=ax)
cbar.set_label("Glacier Index (G)")

# background scatter of actual basin Storage/Yield values
ax.scatter(yield_pts, storage_pts, s=8, color="white", alpha=0.5,
           edgecolor="gray", linewidth=0.3, zorder=2)


# G=0.5 contour line and three annotated example points

example_points = [
    (0.05, 0.95, "Storage=0.95, Yield=0.05\n\u2192 G=0.50"),
    (0.50, 0.50, "Storage=0.50, Yield=0.50\n\u2192 G=0.50"),
    (0.95, 0.05, "Storage=0.05, Yield=0.95\n\u2192 G=0.50"),
]

# the G=0.5 line: Storage = 1 - Yield
line_yield = np.linspace(0, 1, 100)
line_storage = 1 - line_yield
ax.plot(line_yield, line_storage, color="red", lw=2, zorder=3)

offsets = {(0.05, 0.95): (0.16, -0.06), (0.50, 0.50): (0.16, 0.02), (0.95, 0.05): (-0.55, 0.05)}
for yv, sv, label in example_points:
    ax.scatter([yv], [sv], s=90, color="red", edgecolor="black", zorder=5)
    dx, dy = offsets[(yv, sv)]
    ax.annotate(label, (yv, sv), xytext=(yv + dx, sv + dy), fontsize=9.5,
                bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="black", alpha=0.95),
                zorder=6)

ax.set_xlabel("Glacier Yield")
ax.set_ylabel("Glacier Storage")
ax.set_title("Glacier Index Formulation", pad=14)
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)

fig.tight_layout()
fig.savefig("F:/HMA_glacio_hydro_index/Figures/fig7_formulation_contour.png", bbox_inches="tight")
print("Saved fig7_formulation_contour.png")
