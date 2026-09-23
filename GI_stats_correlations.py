# -*- coding: utf-8 -*-
"""
Created on Fri Aug 28 13:07:57 2026

@author: m337l400
"""

"""
Spatial autocorrelation, confidence intervals, multivariate analysis, 
and collinearity for the Glacier Index vs. glacier-characteristics correlations
(manuscript Table 2).

  1. Assess spatial autocorrelation (Moran's I on relative change)
  2. Report confidence intervals (naive Fisher-z + spatially-aware
     block-bootstrap)
  3. Conduct multivariate analysis (multiple regression, standardized
     coefficients)
  4. Evaluate collinearity among predictors (correlation matrix + VIF)

"""
 
import numpy as np
import pandas as pd
import geopandas as gpd
import xarray as xr
from functools import reduce
import matplotlib.pyplot as plt
from scipy import stats
from sklearn.cluster import KMeans
from sklearn.neighbors import NearestNeighbors
import statsmodels.api as sm
from statsmodels.stats.outliers_influence import variance_inflation_factor
 
rng = np.random.default_rng(42)

# Load data
scenario = '2-45'
fn1 = f'F:/HMA_glacio_hydro_index/gindex_all_models_scenarioSSP{scenario}.nc'
ds = xr.open_dataset(fn1).xvec.decode_cf()
gdf = gpd.GeoDataFrame().set_geometry(ds.geometry.values)

glac_fn = "F:/HMA_glacio_hydro_index/level_3_basins/RGI6_13_14_15.shp"
glac = gpd.read_file(glac_fn).set_geometry("geometry")
glac['geometry'] = glac['geometry'].make_valid()

bas_fn = "F:/HMA_impact_index/level_7_basins/level_7_selected/RGI_13_14_15_selected_basins.shp"
bas = gpd.read_file(bas_fn).set_geometry("geometry")
bas['geometry'] = bas['geometry'].make_valid()

basin = bas.merge(gdf)

t = glac.sjoin(basin,how='left')
zmed = t[['Zmed','HYBAS_ID']].groupby("HYBAS_ID").mean()
area =  t[['Area','HYBAS_ID']].groupby("HYBAS_ID").mean()
slope =  t[['Slope','HYBAS_ID']].groupby("HYBAS_ID").mean()
length =  t[['Lmax','HYBAS_ID']].groupby("HYBAS_ID").mean()
length=length.rename(columns = {"Lmax": "L_mean"})
max_length =t[['Lmax','HYBAS_ID']].groupby("HYBAS_ID").max()
lstd = t[['Lmax','HYBAS_ID']].groupby("HYBAS_ID").std()
lstd=lstd.rename(columns = {"Lmax": "L_stdv"})
cv = lstd/length
cv=cv.rename(columns = {"Lmax": "cv"})

## definition to get aspect direction 
def condition(x):
    if x <= 45.0 or 315.0 <= x <=360.0:
        return "N"
    elif  46.0 <= x <= 135.0:
        return "E"
    elif  136.0 <= x <= 225.0:
        return "S"
    elif  226.0 <= x <= 314.0:
        return "W"
t['aspect_dir'] = t["Aspect"].apply(condition)
aspect =  t[['aspect_dir','HYBAS_ID']].groupby("HYBAS_ID").agg(lambda x: x.mode().iloc[0])

data_frames = [zmed, area, slope, aspect, length, max_length, lstd, cv]
chars = reduce(lambda  left,right: pd.merge(left,right,on=['HYBAS_ID']), data_frames)
chars = chars.drop(columns = ['L_stdv_y', 'L_mean_y'])
chars = chars.rename(columns = {"L_mean_x": "Lmean", "L_stdv_x":"Lstdv"})
chars['volume'] = ds.volume.mean(dim="model").isel(time=0).values


PREDICTORS = ["Zmed", "Area", "Slope", "Lmean", "Lmax", "volume"]
 
FILES = {"SSP2-4.5": "F:/HMA_glacio_hydro_index/gindex_all_models_scenarioSSP2-45.nc",
         "SSP5-8.5": "F:/HMA_glacio_hydro_index/gindex_all_models_scenarioSSP5-85.nc"}
 
results_by_ssp = {}
for ssp, path in FILES.items():
    ds = xr.open_dataset(path).mean(dim= "model")
    gy, gs = ds["gy"].values, ds["gs"].values
    lon, lat = ds["lon"].values, ds["lat"].values
    summer = np.isin(ds.time.dt.month.values, [6, 7, 8])
    years = ds.time.dt.year.values
    early_mask = summer & (years >= 2015) & (years <= 2025)
    late_mask = summer & (years >= 2090) & (years <= 2100)
 
    G = 0.5 * gy + 0.5 * gs
    early = np.nanmean(G[:, early_mask], axis=1)
    late = np.nanmean(G[:, late_mask], axis=1)
    rel_change = np.where(early != 0, (late - early) / early * 100, np.nan)
 
    df = chars.copy()
    df["lon"], df["lat"] = lon, lat
    df["rel_change"] = rel_change
    df = df.dropna(subset=["rel_change"]).reset_index(drop=True)
    results_by_ssp[ssp] = df
 
print(f"Basins retained after dropping undefined relative change: "
      f"{ {ssp: len(d) for ssp, d in results_by_ssp.items()} }")
#%% SPATIAL AUTOCORRELATION -- Moran's I (permutation test) on
#    relative change, using k-nearest-neighbor spatial weights

def knn_weights(lon, lat, k=8):
    coords = np.radians(np.column_stack([lat, lon]))
    nn = NearestNeighbors(n_neighbors=k + 1, metric="haversine").fit(coords)
    _, idx = nn.kneighbors(coords)
    n = len(lon)
    W = np.zeros((n, n))
    for i in range(n):
        for j in idx[i, 1:]:  # skip self (first neighbor)
            W[i, j] = 1
    row_sums = W.sum(axis=1, keepdims=True)
    row_sums[row_sums == 0] = 1
    return W / row_sums
 
def morans_i(x, W, n_perm=999, seed=42):
    n = len(x)
    xbar = x.mean()
    z = x - xbar
    S0 = W.sum()
    num = (W * np.outer(z, z)).sum()
    den = (z ** 2).sum()
    I = (n / S0) * (num / den)
 
    rng_local = np.random.default_rng(seed)
    perm_I = np.empty(n_perm)
    for p in range(n_perm):
        zp = rng_local.permutation(z)
        num_p = (W * np.outer(zp, zp)).sum()
        perm_I[p] = (n / S0) * (num_p / den)
    p_value = (np.sum(perm_I >= I) + 1) / (n_perm + 1) if I > perm_I.mean() else \
              (np.sum(perm_I <= I) + 1) / (n_perm + 1)
    return I, p_value, perm_I
 
moran_results = {}
for ssp, df in results_by_ssp.items():
    W = knn_weights(df["lon"].values, df["lat"].values, k=8)
    I, p, perm_I = morans_i(df["rel_change"].values, W)
    moran_results[ssp] = {"I": I, "p_value": p, "perm_dist": perm_I, "W": W}
    print(f"{ssp}: Moran's I = {I:.4f}, permutation p-value = {p:.4f} "
          f"(k=8 nearest-neighbor weights, n={len(df)})")

#%% CONFIDENCE INTERVALS -- naive Fisher-z vs. spatial block bootstrap

def fisher_ci(r, n, alpha=0.05):
    z = np.arctanh(r)
    se = 1 / np.sqrt(n - 3)
    zcrit = stats.norm.ppf(1 - alpha / 2)
    lo, hi = np.tanh(z - zcrit * se), np.tanh(z + zcrit * se)
    return lo, hi
 
def block_bootstrap_ci(df, xcol, ycol, n_blocks=25, n_boot=2000, seed=42):
    coords = df[["lon", "lat"]].values
    km = KMeans(n_clusters=n_blocks, n_init=10, random_state=seed).fit(coords)
    df = df.copy()
    df["_block"] = km.labels_
    blocks = df["_block"].unique()
    rng_local = np.random.default_rng(seed)
    boot_r = np.empty(n_boot)
    for b in range(n_boot):
        sampled_blocks = rng_local.choice(blocks, size=len(blocks), replace=True)
        sample = pd.concat([df[df["_block"] == blk] for blk in sampled_blocks])
        boot_r[b] = np.corrcoef(sample[xcol], sample[ycol])[0, 1]
    lo, hi = np.percentile(boot_r, [2.5, 97.5])
    return lo, hi, boot_r
 
ci_rows = []
for ssp, df in results_by_ssp.items():
    n = len(df)
    for pred in PREDICTORS:
        r, p_naive = stats.pearsonr(df[pred], df["rel_change"])
        lo_f, hi_f = fisher_ci(r, n)
        lo_b, hi_b, _ = block_bootstrap_ci(df, pred, "rel_change")
        ci_rows.append({
            "ssp": ssp, "predictor": pred, "r": r, "p_naive": p_naive,
            "fisher_ci_lo": lo_f, "fisher_ci_hi": hi_f,
            "block_boot_ci_lo": lo_b, "block_boot_ci_hi": hi_b,
        })
ci_df = pd.DataFrame(ci_rows)
# ci_df.to_csv("F:/HMA_glacio_hydro_index/correlation_CIs.csv", index=False)
print("\nCorrelation CIs (naive Fisher-z vs. spatial block bootstrap):")
print(ci_df.round(3).to_string(index=False))

#%% MULTIVARIATE ANALYSIS -- multiple regression, standardized coefs
mv_rows = []
resid_moran = {}
for ssp, df in results_by_ssp.items():
    X = df[PREDICTORS].copy()
    X = (X - X.mean()) / X.std()  # standardize -> comparable beta coefficients
    X = sm.add_constant(X)
    y = df["rel_change"].values
    model = sm.OLS(y, X, missing="drop").fit()
 
    for pred in PREDICTORS:
        mv_rows.append({
            "ssp": ssp, "predictor": pred,
            "beta": model.params[pred], "se": model.bse[pred],
            "t": model.tvalues[pred], "p": model.pvalues[pred],
            "ci_lo": model.conf_int().loc[pred, 0],
            "ci_hi": model.conf_int().loc[pred, 1],
        })
    print(f"\n{ssp}: multivariate R^2 = {model.rsquared:.3f}, "
          f"adj. R^2 = {model.rsquared_adj:.3f}, n = {int(model.nobs)}")
 
    W = moran_results[ssp]["W"]
    I_resid, p_resid, _ = morans_i(model.resid.values, W)
    resid_moran[ssp] = {"I": I_resid, "p": p_resid}
    print(f"{ssp}: Moran's I on regression residuals = {I_resid:.4f} "
          f"(p={p_resid:.4f}) -- spatial autocorrelation remaining after controls")
 
mv_df = pd.DataFrame(mv_rows)
# mv_df.to_csv("F:/HMA_glacio_hydro_index/multivariate_regression.csv", index=False)
print("\nMultivariate regression (standardized coefficients):")
print(mv_df.round(3).to_string(index=False))
 
#%% COLLINEARITY -- correlation matrix + VIF

corr_matrix = chars[PREDICTORS].corr()
corr_matrix.to_csv("F:/HMA_glacio_hydro_index/predictor_correlation_matrix.csv")
print("\nPredictor correlation matrix:")
print(corr_matrix.round(2))
 
X_vif = sm.add_constant(chars[PREDICTORS])
vif_data = pd.DataFrame({
    "predictor": PREDICTORS,
    "VIF": [variance_inflation_factor(X_vif.values, i + 1) for i in range(len(PREDICTORS))],
})
vif_data.to_csv("F:/HMA_glacio_hydro_index/vif.csv", index=False)
print("\nVariance Inflation Factors:")
print(vif_data.round(2).to_string(index=False))

#%% fig_moran_scatter

plt.rcParams.update({"font.size": 11, "figure.dpi": 150})
 
ssp_plot = "SSP2-4.5"
df = results_by_ssp[ssp_plot]
W = moran_results[ssp_plot]["W"]
x = df["rel_change"].values
z = x - x.mean()
lag = W @ z
fig, ax = plt.subplots(figsize=(6.5, 6))
ax.scatter(z, lag, s=14, alpha=0.5, color="#2b6cb0")
b, a = np.polyfit(z, lag, 1)
xs = np.linspace(z.min(), z.max(), 10)
ax.plot(xs, a + b * xs, color="black", lw=1.5)
ax.axhline(0, color="gray", lw=0.5)
ax.axvline(0, color="gray", lw=0.5)
ax.set_xlabel("Relative change (centered)")
ax.set_ylabel("Spatial lag (neighbor-weighted average)")
ax.set_title(f"Moran scatterplot, {ssp_plot}\nMoran's I = {moran_results[ssp_plot]['I']:.3f}, "
             f"p = {moran_results[ssp_plot]['p_value']:.3f}")
fig.tight_layout()
# fig.savefig("F:/HMA_glacio_hydro_index/fig_moran_scatter.png")
# plt.close(fig)
 
#%% fig_ci_comparison

fig, axes = plt.subplots(1, 2, figsize=(13, 5), sharey=True)
for ax, ssp in zip(axes, FILES):
    sub = ci_df[ci_df.ssp == ssp].reset_index(drop=True)
    ypos = np.arange(len(sub))
    ax.errorbar(sub["r"], ypos - 0.15, xerr=[sub["r"] - sub["fisher_ci_lo"], sub["fisher_ci_hi"] - sub["r"]],
                fmt="o", color="#2b6cb0", label="naive Fisher-z CI", capsize=3)
    ax.errorbar(sub["r"], ypos + 0.15, xerr=[sub["r"] - sub["block_boot_ci_lo"], sub["block_boot_ci_hi"] - sub["r"]],
                fmt="s", color="#c05621", label="spatial block-bootstrap CI", capsize=3)
    ax.axvline(0, color="gray", lw=0.7)
    ax.set_yticks(ypos)
    ax.set_yticklabels(sub["predictor"])
    ax.set_xlabel("Pearson r (predictor vs. relative change)")
    ax.set_title(ssp)
    ax.legend(fontsize=8, loc="lower right")
fig.suptitle("Correlation confidence intervals: naive vs. spatially-aware", y=1.02)
fig.tight_layout()
# fig.savefig("F:/HMA_glacio_hydro_index/fig_ci_comparison.png", bbox_inches="tight")
# plt.close(fig)
 
#%% fig_univariate_vs_multivariate

fig, axes = plt.subplots(1, 2, figsize=(13, 5), sharey=True)
for ax, ssp in zip(axes, FILES):
    df = results_by_ssp[ssp]
    uni = [stats.pearsonr(df[p], df["rel_change"])[0] for p in PREDICTORS]
    multi = mv_df[mv_df.ssp == ssp].set_index("predictor").loc[PREDICTORS, "beta"].values
    ypos = np.arange(len(PREDICTORS))
    width = 0.35
    ax.barh(ypos - width/2, uni, width, label="univariate r", color="#2b6cb0")
    ax.barh(ypos + width/2, multi, width, label="multivariate standardized beta", color="#c05621")
    ax.set_yticks(ypos)
    ax.set_yticklabels(PREDICTORS)
    ax.axvline(0, color="gray", lw=0.7)
    ax.set_xlabel("Coefficient")
    ax.set_title(ssp)
    ax.legend(fontsize=8)
fig.suptitle("Univariate correlation vs. multivariate standardized coefficient", y=1.02)
fig.tight_layout()
# fig.savefig("F:/HMA_glacio_hydro_index/fig_univariate_vs_multivariate.png", bbox_inches="tight")
# plt.close(fig)

#%% fig_vif

fig, ax = plt.subplots(figsize=(6.5, 4.5))
colors = ["#c05621" if v > 5 else "#2b6cb0" for v in vif_data["VIF"]]
ax.bar(vif_data["predictor"], vif_data["VIF"], color=colors)
ax.axhline(5, color="black", ls="--", lw=1, label="common concern threshold (VIF=5)")
ax.set_ylabel("Variance Inflation Factor")
ax.set_title("Collinearity among predictors")
ax.legend(fontsize=9)
fig.tight_layout()
# fig.savefig("F:/HMA_glacio_hydro_index/fig_vif.png")
# plt.close(fig)
 