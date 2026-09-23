"""
Figure 5: paired basin-level SSP2-4.5 vs SSP5-8.5 comparison. Pairs basins across scenarios,
using spatial block-bootstrap confidence intervals (25 geographic
clusters across all 934 basins.

Panel A: mean paired difference in 2100 summer Glacier Index
(SSP5-8.5 minus SSP2-4.5) by magnitude group, with 95% CI.
Panel B: basin-paired scatter, SSP2-4.5 vs SSP5-8.5, colored by group.
"""

import numpy as np
import pandas as pd
import xarray as xr
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans

FILES = {"SSP2-4.5": "F:/HMA_glacio_hydro_index/gindex_all_models_scenarioSSP2-45.nc",
         "SSP5-8.5": "F:/HMA_glacio_hydro_index/gindex_all_models_scenarioSSP5-85.nc"}


#%% Load both scenarios, compute basin-level summer G at 2100
#    (2090-2100 mean, consistent with the rest of the manuscript)

data = {}
for ssp, path in FILES.items():
    ds = xr.open_dataset(path).mean(dim="model")
    gy, gs = ds["gy"].values, ds["gs"].values
    lon, lat = ds["lon"].values, ds["lat"].values
    summer = np.isin(ds.time.dt.month.values, [6, 7, 8])
    years = ds.time.dt.year.values
    late_mask = summer & (years >= 2090) & (years <= 2100)
    G = 0.5 * gy + 0.5 * gs
    G_2100 = np.nanmean(G[:, late_mask], axis=1)
    data[ssp] = pd.DataFrame({"lon": lon, "lat": lat, "G": G_2100})

df = pd.DataFrame({
    "lon": data["SSP2-4.5"]["lon"], "lat": data["SSP2-4.5"]["lat"],
    "G_245": data["SSP2-4.5"]["G"], "G_585": data["SSP5-8.5"]["G"],
})
df["diff"] = df["G_585"] - df["G_245"]  # paired difference, same basin

# classify basins by SSP2-4.5 magnitude
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

print("Basin counts by group:")
print(df["group"].value_counts())


#%% Spatial block bootstrap on mean paired difference, by group

def block_bootstrap_mean_diff(sub, n_blocks=25, n_boot=2000, seed=42):
    if len(sub) < n_blocks:
        n_blocks = max(2, len(sub) // 3)
    coords = sub[["lon", "lat"]].values
    km = KMeans(n_clusters=n_blocks, n_init=10, random_state=seed).fit(coords)
    sub = sub.copy()
    sub["_block"] = km.labels_
    blocks = sub["_block"].unique()
    rng = np.random.default_rng(seed)
    boot_means = np.empty(n_boot)
    for b in range(n_boot):
        sampled = rng.choice(blocks, size=len(blocks), replace=True)
        resample = pd.concat([sub[sub["_block"] == blk] for blk in sampled])
        boot_means[b] = resample["diff"].mean()
    return np.percentile(boot_means, [2.5, 97.5]), boot_means

GROUP_ORDER = ["Precipitation-dominated", "Glacier-influenced", "Balanced", "Glacier-dominated"]
results = []
for grp in GROUP_ORDER:
    sub = df[df["group"] == grp]
    if len(sub) < 5:
        continue
    mean_diff = sub["diff"].mean()
    (ci_lo, ci_hi), boot_dist = block_bootstrap_mean_diff(sub)
    cohens_d = mean_diff / sub["diff"].std() if sub["diff"].std() > 0 else np.nan
    results.append({"group": grp, "n": len(sub), "mean_diff": mean_diff,
                     "ci_lo": ci_lo, "ci_hi": ci_hi, "cohens_d": cohens_d,
                     "excludes_zero": (ci_lo > 0) or (ci_hi < 0)})
res_df = pd.DataFrame(results)
# res_df.to_csv("F:/HMA_glacio_hydro_index/paired_scenario_comparison.csv", index=False)
# print("\nPaired basin-level SSP2-4.5 vs SSP5-8.5 comparison, by group:")
# print(res_df.round(4).to_string(index=False))


#%% Combined two-panel figure: bar chart + scatter

plt.rcParams.update({"font.size": 11, "figure.dpi": 150})
fig, axes = plt.subplots(1, 2, figsize=(13.5, 5.8), gridspec_kw={"width_ratios": [1, 1.05]})

# Panel A: grouped mean difference with bootstrap CI
# (display order: Glacier-dominated at top, Precip.-dominated at bottom)
display_order = ["Glacier-dominated", "Balanced", "Glacier-influenced", "Precipitation-dominated"]
res_df_display = res_df.set_index("group").loc[display_order].reset_index()

ax = axes[0]
y = np.arange(len(res_df_display))
ax.barh(y, res_df_display["mean_diff"], color="#2b6cb0",
        xerr=[res_df_display["mean_diff"] - res_df_display["ci_lo"],
              res_df_display["ci_hi"] - res_df_display["mean_diff"]],
        capsize=4)
ax.set_yticks(y)
ax.set_yticklabels([f"{g}\n(n={n})" for g, n in zip(res_df_display["group"], res_df_display["n"])])
ax.axvline(0, color="gray", lw=0.8)
ax.set_xlabel("Mean paired difference in Glacier Index, 2100\n(SSP5-8.5 \u2212 SSP2-4.5)")
ax.set_title("A) Scenario divergence by magnitude\n(spatial block-bootstrap 95% CI, n=934)", fontsize=11.5, loc="left")

# Panel B: paired scatter, colored by group, 1:1 line
ax2 = axes[1]
group_colors = {"Precipitation-dominated": "#2b6cb0", "Glacier-influenced": "#c05621",
                 "Balanced": "#805ad5", "Glacier-dominated": "#38a169"}
for grp, c in group_colors.items():
    sub = df[df["group"] == grp]
    ax2.scatter(sub["G_245"], sub["G_585"], s=10, alpha=0.5, color=c, label=grp)
ax2.plot([0, 1], [0, 1], color="black", lw=1, ls="--", label="1:1 (no scenario difference)")
ax2.set_xlabel("Glacier Index, 2100 (SSP2-4.5)")
ax2.set_ylabel("Glacier Index, 2100 (SSP5-8.5)")
ax2.set_title("B) Basin-paired comparison\nacross emissions scenarios", fontsize=11.5, loc="left")
ax2.legend(fontsize=8, loc="upper left")
ax2.set_xlim(-0.02, 1.02)
ax2.set_ylim(-0.02, 1.02)

fig.tight_layout()
# fig.savefig("F:/HMA_glacio_hydro_index/Figures/fig5_paired_scenario_combined.png", bbox_inches="tight")
plt.close(fig)
# print("\nSaved fig5_paired_scenario_combined.png")
