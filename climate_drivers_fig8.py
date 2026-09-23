# -*- coding: utf-8 -*-
"""
Created on Wed Sep 23 13:45:48 2026

@author: m337l400
"""

"""
Climatic driver attribution for Glacier Index change.
Disentangles the independent roles of temperature change and precipitation 
change in driving relative Glacier Index change (multivariate regression, 
spatially-aware CIs, collinearity check).
Classifies basins by monsoon vs. westerlies dominance (summer share of annual
precipitation) and test whether climatic driver importance differs between regimes.

"""
 
import numpy as np
import pandas as pd
import xarray as xr
import matplotlib.pyplot as plt
import contextily as cx
import geopandas as gpd
from scipy import stats
from sklearn.cluster import KMeans
import statsmodels.api as sm
from statsmodels.stats.outliers_influence import variance_inflation_factor
 
rng = np.random.default_rng(42)
 
FILES = {
    "SSP2-4.5": {
        "gi": "F:/HMA_glacio_hydro_index/gindex_all_models_scenarioSSP2-45.nc",
        "temp": "F:/HMA_glacio_hydro_index/temperature/aggregated_by_basin/temp_slice_scenarioSSP2-45.nc",
        "precip": "F:/HMA_glacio_hydro_index/precipitation/precipitation_slice_scenarioSSP2-45.nc",
    },
    "SSP5-8.5": {
        "gi": "F:/HMA_glacio_hydro_index/gindex_all_models_scenarioSSP2-45.nc",
        "temp": "F:/HMA_glacio_hydro_index/temperature/aggregated_by_basin/temp_slice_scenarioSSP5-85.nc",
        "precip": "F:/HMA_glacio_hydro_index/precipitation/precipitation_slice_scenarioSSP5-85.nc",
    },
}
 
# Load, compute basin-level summer relative change (G, Temp) and
#    relative % change (Precip), plus monsoon-fraction classification

results = {}
for ssp, paths in FILES.items():
    gi = xr.open_dataset(paths["gi"]).xvec.decode_cf().mean(dim='model')
    temp = xr.open_dataset(paths["temp"])
    precip = xr.open_dataset(paths["precip"])
 
    # lon, lat = gi["lon"].values, gi["lat"].values
    geometry =gi.geometry
    months = gi.time.dt.month.values
    years = gi.time.dt.year.values
    summer = np.isin(months, [6, 7, 8])
    early_mask = summer & (years >= 2015) & (years <= 2025)
    late_mask = summer & (years >= 2090) & (years <= 2100)
 
    G = 0.5 * gi["gy"].values + 0.5 * gi["gs"].values
    G_early = np.nanmean(G[:, early_mask], axis=1)
    G_late = np.nanmean(G[:, late_mask], axis=1)
    G_relchange = np.where(G_early != 0, (G_late - G_early) / G_early * 100, np.nan)
 
    T = temp["temp"].values
    T_early = np.nanmean(T[:, early_mask], axis=1)
    T_late = np.nanmean(T[:, late_mask], axis=1)
    dT = T_late - T_early  # absolute change, Kelvin (= degC change)
 
    P = precip["precipitation"].values
    P_early = np.nanmean(P[:, early_mask], axis=1)
    P_late = np.nanmean(P[:, late_mask], axis=1)
    dP_rel = np.where(P_early != 0, (P_late - P_early) / P_early * 100, np.nan)
 
    # monsoon fraction: share of ANNUAL precipitation falling in JJA,
    # using the baseline period (2015-2025)
    annual_early_mask = (years >= 2015) & (years <= 2025)
    P_annual_total = np.nansum(
        P[:, annual_early_mask].reshape(P.shape[0], -1), axis=1
    )
    P_jja_total = np.nansum(P[:, early_mask], axis=1)
    monsoon_frac = P_jja_total / P_annual_total
 
    df = pd.DataFrame({
        "geometry":geometry,
        # "lon": lon, "lat": lat,
        "G_relchange": G_relchange, "dT": dT, "dP_rel": dP_rel,
        "monsoon_frac": monsoon_frac,
    }).dropna()
    results[ssp] = df
    print(f"{ssp}: {len(df)} basins retained")
    print(f"  dT range: [{df.dT.min():.2f}, {df.dT.max():.2f}] K, mean={df.dT.mean():.2f} K")
    print(f"  dP_rel range: [{df.dP_rel.min():.1f}, {df.dP_rel.max():.1f}]%, mean={df.dP_rel.mean():.1f}%")
 

#%% Univariate correlations: G change vs dT, G change vs dP

print("\n--- Univariate correlations ---")
uni_rows = []
for ssp, df in results.items():
    for var in ["dT", "dP_rel"]:
        r, p = stats.pearsonr(df[var], df["G_relchange"])
        uni_rows.append({"ssp": ssp, "predictor": var, "r": r, "p": p})
        print(f"{ssp}: G_relchange vs {var}: r={r:.3f}, p={p:.2e}")
uni_df = pd.DataFrame(uni_rows)
 
# collinearity between dT and dP themselves
print("\n--- Collinearity between dT and dP_rel ---")
for ssp, df in results.items():
    r, p = stats.pearsonr(df["dT"], df["dP_rel"])
    print(f"{ssp}: corr(dT, dP_rel) = {r:.3f} (p={p:.2e})")
 

#%% Multivariate regression: disentangle dT vs dP_rel

print("\n--- Multivariate regression: G_relchange ~ dT + dP_rel (standardized) ---")
mv_rows = []
for ssp, df in results.items():
    X = df[["dT", "dP_rel"]].copy()
    X = (X - X.mean()) / X.std()
    X = sm.add_constant(X)
    y = df["G_relchange"].values
    model = sm.OLS(y, X).fit()
    print(f"\n{ssp}: R^2={model.rsquared:.3f}, n={int(model.nobs)}")
    print(model.summary().tables[1])
    for var in ["dT", "dP_rel"]:
        mv_rows.append({
            "ssp": ssp, "predictor": var, "beta": model.params[var],
            "se": model.bse[var], "p": model.pvalues[var],
            "ci_lo": model.conf_int().loc[var, 0], "ci_hi": model.conf_int().loc[var, 1],
        })
    # VIF
    X_vif = sm.add_constant(df[["dT", "dP_rel"]])
    for i, var in enumerate(["dT", "dP_rel"]):
        vif = variance_inflation_factor(X_vif.values, i + 1)
        print(f"  VIF({var}) = {vif:.2f}")
mv_df = pd.DataFrame(mv_rows)
# mv_df.to_csv("F:/HMA_glacio_hydro_index/climate_driver_regression.csv", index=False)
 

#%% Monsoon vs. westerlies classification and comparison

print("\n--- Monsoon vs. westerlies regime comparison ---")
regime_rows = []
for ssp, df in results.items():
    median_frac = df["monsoon_frac"].median()
    df["regime"] = np.where(df["monsoon_frac"] >= median_frac, "Monsoon-dominated", "Westerlies-dominated")
    for regime in ["Monsoon-dominated", "Westerlies-dominated"]:
        sub = df[df["regime"] == regime]
        r_t, p_t = stats.pearsonr(sub["dT"], sub["G_relchange"])
        r_p, p_p = stats.pearsonr(sub["dP_rel"], sub["G_relchange"])
        regime_rows.append({"ssp": ssp, "regime": regime, "n": len(sub),
                             "r_temp": r_t, "p_temp": p_t,
                             "r_precip": r_p, "p_precip": p_p,
                             "mean_G_relchange": sub["G_relchange"].mean(),
                             "mean_dT": sub["dT"].mean(), "mean_dP_rel": sub["dP_rel"].mean()})
    results[ssp] = df  # store regime label back
regime_df = pd.DataFrame(regime_rows)
# regime_df.to_csv("F:/HMA_glacio_hydro_index/monsoon_westerlies_comparison.csv", index=False)
print(regime_df.round(3).to_string(index=False))
 

#%% Plot map of monsoon fraction (SSP2-4.5)

plt.rcParams.update({"font.size": 11, "figure.dpi": 300})

basins_gdf= gpd.GeoDataFrame(gi.geometry, columns=["geometry"]).set_crs(epsg=4326, allow_override=True)
basins_gdf["monsoon_frac"] = monsoon_frac

fig, ax = plt.subplots(figsize=(7.5, 6.5))

basins_gdf.plot(
    column="monsoon_frac",
    cmap="BrBG",
    vmin=0, vmax=1,
    edgecolor="black", linewidth=0.15,
    legend=True,
    legend_kwds={"label": "Summer share of annual precipitation", "shrink": 0.7},
    ax=ax,
)

cx.add_basemap(ax, crs=gi.geometry.crs.to_string(), source=cx.providers.Esri.WorldPhysical, attribution_size=1)

ax.set_xlabel("Longitude")
ax.set_ylabel("Latitude")
ax.set_title("Monsoon vs. westerlies regime (2015\u20132025 baseline)")
ax.set_aspect("equal")

fig.tight_layout()
fig.savefig("F:/HMA_glacio_hydro_index/Figures/fig8_panelA_monsoon_map.png", bbox_inches="tight")


#%% Plot G relative change vs dT and dP_rel, colored by regime, both scenarios
fig, axes = plt.subplots(2, 2, figsize=(12, 10))
colors = {"Monsoon-dominated": "#2b6cb0", "Westerlies-dominated": "#c05621"}
for row, ssp in enumerate(FILES):
    df = results[ssp]
    for regime, c in colors.items():
        sub = df[df["regime"] == regime]
        axes[row, 0].scatter(sub["dT"], sub["G_relchange"], s=10, alpha=0.5, color=c, label=regime)
        axes[row, 1].scatter(sub["dP_rel"], sub["G_relchange"], s=10, alpha=0.5, color=c, label=regime)
    axes[row, 0].set_xlabel("\u0394 Temperature (K, summer, 2090-2100 vs 2015-2025)")
    axes[row, 0].set_ylabel(f"{ssp}\nGlacier Index relative change (%)")
    axes[row, 1].set_xlabel("\u0394 Precipitation (%, summer, 2090-2100 vs 2015-2025)")
    axes[row, 1].set_ylabel("Glacier Index relative change (%)")
    axes[row, 0].legend(fontsize=8)
    axes[row, 1].legend(fontsize=8)
axes[0, 0].set_title("Temperature change vs. Glacier Index change")
axes[0, 1].set_title("Precipitation change vs. Glacier Index change")
fig.tight_layout()
# fig.savefig("F:/HMA_glacio_hydro_index/Figures/fig_climate_driver_scatter.png")
# plt.close(fig)
 
#%% Regression coefficient comparison: temp vs precip, both scenarios
fig, ax = plt.subplots(figsize=(7.5, 5))
x = np.arange(2)
width = 0.35
for i, ssp in enumerate(FILES):
    sub = mv_df[mv_df.ssp == ssp].set_index("predictor")
    betas = [sub.loc["dT", "beta"], sub.loc["dP_rel", "beta"]]
    errs = [sub.loc["dT", "beta"] - sub.loc["dT", "ci_lo"], sub.loc["dP_rel", "beta"] - sub.loc["dP_rel", "ci_lo"]]
    ax.bar(x + (i - 0.5) * width, betas, width, yerr=errs, label=ssp, capsize=4)
ax.set_xticks(x)
ax.set_xticklabels(["\u0394 Temperature", "\u0394 Precipitation"])
ax.axhline(0, color="gray", lw=0.7)
ax.set_ylabel("Standardized regression coefficient")
ax.set_title("Independent contribution of temperature vs. precipitation change\nto Glacier Index relative change")
ax.legend(fontsize=9)
fig.tight_layout()
# fig.savefig("F:/HMA_glacio_hydro_index/Figures/fig_climate_driver_coefficients.png")
# plt.close(fig)
 
#%% Regime comparison bar chart: r(temp) and r(precip) by regime
fig, ax = plt.subplots(figsize=(8.5, 5))
x = np.arange(4)
labels = []
vals = []
for ssp in FILES:
    for regime in ["Monsoon-dominated", "Westerlies-dominated"]:
        row = regime_df[(regime_df.ssp == ssp) & (regime_df.regime == regime)].iloc[0]
        labels.append(f"{ssp}\n{regime}")
width = 0.35
temp_r = regime_df.pivot_table(index=["ssp", "regime"], values="r_temp").values.ravel()
precip_r = regime_df.pivot_table(index=["ssp", "regime"], values="r_precip").values.ravel()
ax.bar(x - width/2, temp_r, width, label="r (Temperature)", color="#c05621")
ax.bar(x + width/2, precip_r, width, label="r (Precipitation)", color="#2b6cb0")
ax.set_xticks(x)
ax.set_xticklabels(labels, fontsize=8)
ax.axhline(0, color="gray", lw=0.7)
ax.set_ylabel("Pearson r vs. Glacier Index relative change")
ax.set_title("Climatic driver correlation by regime")
ax.legend(fontsize=9)
fig.tight_layout()
# fig.savefig("F:/HMA_glacio_hydro_index/Figures/fig_regime_comparison.png")
# plt.close(fig)
 
 
