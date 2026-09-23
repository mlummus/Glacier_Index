# -*- coding: utf-8 -*-
"""
Created on Wed Sep 23 14:56:48 2026

@author: m337l400

Glacier Index sensitivity suite -- SSP2-4.5 vs. SSP5-8.5, side by side.
 
Weight sweep, Monte Carlo by functional form, variance decomposition, 
basin-level divergence, and seasonal breakdown. Loops over both scenario files 

"""
 
import numpy as np
import pandas as pd
import xarray as xr
import xvec
import matplotlib.pyplot as plt
 
rng = np.random.default_rng(seed=42)
 
FILES = {"SSP2-4.5": "F:/HMA_glacio_hydro_index/gindex_all_models_scenarioSSP2-45.nc",
         "SSP5-8.5": "F:/HMA_glacio_hydro_index/gindex_all_models_scenarioSSP5-85.nc"}
 
data = {}
for ssp, path in FILES.items():
    ds = xr.open_dataset(path).xvec.decode_cf().mean(dim="model")
    data[ssp] = {
        "gy": ds["gy"].values,
        "gs": ds["gs"].values,
        "basin_id": ds["index"].values,
        "months": ds.time.dt.month.values,
        "years": ds.time.dt.year.values,
    }
 
summer = np.isin(data["SSP2-4.5"]["months"], [6, 7, 8])
years = data["SSP2-4.5"]["years"]
early_mask = summer & (years >= 2015) & (years <= 2025)
late_mask = summer & (years >= 2090) & (years <= 2100)
basin_id = data["SSP2-4.5"]["basin_id"]
 
def compute_G(gy, gs, w, form="arithmetic"):
    if form == "arithmetic":
        return w * gy + (1 - w) * gs
    y = np.clip(gy, 1e-6, 1)
    s = np.clip(gs, 1e-6, 1)
    if form == "geometric":
        return (y ** w) * (s ** (1 - w))
    if form == "harmonic":
        return 1 / (w / y + (1 - w) / s)
    raise ValueError(form)
 
def headline_stats(G):
    early = np.nanmean(G[:, early_mask], axis=1)
    late = np.nanmean(G[:, late_mask], axis=1)
    rel_change = np.where(early != 0, (late - early) / early, np.nan)
    return {
        "pct_zero_2100": np.mean(late == 0) * 100,
        "mean_relchange": np.nanmean(rel_change) * 100,
        "late_by_basin": late,
    }
 

#%% Weight sweep, both scenarios (arithmetic form)

weights = np.round(np.arange(0.0, 1.01, 0.05), 2)
sweep_rows = []
for ssp, d in data.items():
    for w in weights:
        G = compute_G(d["gy"], d["gs"], w, "arithmetic")
        s = headline_stats(G)
        sweep_rows.append({"ssp": ssp, "weight": w,
                            "pct_zero_2100": s["pct_zero_2100"],
                            "mean_relchange": s["mean_relchange"]})
sweep_df = pd.DataFrame(sweep_rows)
sweep_df.to_csv("F:/HMA_glacio_hydro_index/combined_sensitivity_sweep.csv", index=False)
 

#%% Monte Carlo across weight + functional form, both scenarios

N_ITER = 5000
forms = ["arithmetic", "geometric", "harmonic"]
mc_rows = []
for ssp, d in data.items():
    baseline_late = headline_stats(compute_G(d["gy"], d["gs"], 0.5, "arithmetic"))["late_by_basin"]
    baseline_rank = pd.Series(baseline_late, index=basin_id).rank()
    for i in range(N_ITER):
        w = rng.uniform(0, 1)
        form = rng.choice(forms)
        G = compute_G(d["gy"], d["gs"], w, form)
        s = headline_stats(G)
        rank_i = pd.Series(s["late_by_basin"], index=basin_id).rank()
        rho = baseline_rank.corr(rank_i, method="spearman")
        mc_rows.append({"ssp": ssp, "iter": i, "weight": w, "form": form,
                         "mean_relchange": s["mean_relchange"], "rank_rho": rho})
mc_df = pd.DataFrame(mc_rows)
mc_df.to_csv("F:/HMA_glacio_hydro_index/combined_monte_carlo.csv", index=False)
 

#%% Variance decomposition, both scenarios (summer, w=0.5)

var_rows = []
for ssp, d in data.items():
    y = d["gy"][:, late_mask].ravel()
    s = d["gs"][:, late_mask].ravel()
    valid = ~np.isnan(y) & ~np.isnan(s)
    y, s = y[valid], s[valid]
    vy, vs = np.var(y), np.var(s)
    cov = np.mean((y - y.mean()) * (s - s.mean()))
    w = 0.5
    ty, ts, tc = w**2 * vy, (1 - w)**2 * vs, 2 * w * (1 - w) * cov
    tot = ty + ts + tc
    var_rows.append({"ssp": ssp, "yield_share": ty / tot * 100,
                      "storage_share": ts / tot * 100, "cov_share": tc / tot * 100})
var_df = pd.DataFrame(var_rows)
var_df.to_csv("F:/HMA_glacio_hydro_index/combined_variance_decomposition.csv", index=False)
 

#%% Basin-level divergence (arithmetic vs. harmonic), both scenarios

div_rows_all = []
for ssp, d in data.items():
    yb = np.nanmean(d["gy"][:, late_mask], axis=1)
    sb = np.nanmean(d["gs"][:, late_mask], axis=1)
    y = np.clip(yb, 1e-6, 1)
    s = np.clip(sb, 1e-6, 1)
    g_arith = 0.5 * yb + 0.5 * sb
    g_harm = 1 / (0.5 / y + 0.5 / s)
    df = pd.DataFrame({"ssp": ssp, "basin_id": basin_id, "yield": yb, "storage": sb,
                        "G_arithmetic": g_arith, "G_harmonic": g_harm})
    df["divergence"] = df["G_arithmetic"] - df["G_harmonic"]
    df["quartile_arith"] = pd.qcut(df["G_arithmetic"], 4, labels=False, duplicates="drop")
    df["quartile_harm"] = pd.qcut(df["G_harmonic"].clip(lower=1e-9), 4, labels=False, duplicates="drop")
    div_rows_all.append(df)
div_df = pd.concat(div_rows_all, ignore_index=True)
div_df.to_csv("F:/HMA_glacio_hydro_indexcombined_basin_divergence.csv", index=False)
 
div_summary = []
for ssp in FILES:
    dd = div_df[div_df["ssp"] == ssp]
    n_shift = (dd["quartile_arith"] != dd["quartile_harm"]).sum()
    n_905 = ((dd["storage"] > 0.3) & (dd["yield"] < 0.1)).sum()
    div_summary.append({"ssp": ssp, "pct_quartile_shift": n_shift / len(dd) * 100,
                         "pct_905type": n_905 / len(dd) * 100})
div_summary_df = pd.DataFrame(div_summary)
 

#%% Seasonal breakdown, both scenarios

season_map = {12: "DJF", 1: "DJF", 2: "DJF", 3: "MAM", 4: "MAM", 5: "MAM",
              6: "JJA", 7: "JJA", 8: "JJA", 9: "SON", 10: "SON", 11: "SON"}
seasons_arr = np.array([season_map[m] for m in data["SSP2-4.5"]["months"]])
SEASONS = ["DJF", "MAM", "JJA", "SON"]
late_all = (years >= 2090) & (years <= 2100)
 
seasonal_rows = []
for ssp, d in data.items():
    for seas in SEASONS:
        mask = (seasons_arr == seas) & late_all
        y = d["gy"][:, mask].ravel()
        s = d["gs"][:, mask].ravel()
        valid = ~np.isnan(y) & ~np.isnan(s)
        y, s = y[valid], s[valid]
        vy, vs = np.var(y), np.var(s)
        cov = np.mean((y - y.mean()) * (s - s.mean()))
        w = 0.5
        ty, ts, tc = w**2 * vy, (1 - w)**2 * vs, 2 * w * (1 - w) * cov
        tot = ty + ts + tc
        seasonal_rows.append({"ssp": ssp, "season": seas,
                               "yield_share": ty / tot * 100,
                               "storage_share": ts / tot * 100,
                               "pct_yield_zero": np.mean(y == 0) * 100})
seasonal_df = pd.DataFrame(seasonal_rows)
seasonal_df.to_csv("F:/HMA_glacio_hydro_index/combined_seasonal_variance.csv", index=False)
 

#%% PRINT SUMMARY

print("=" * 70)
print("SUMMARY: SSP2-4.5 vs. SSP5-8.5")
print("=" * 70)
print("\n--- Published (w=0.5) headline stats ---")
for ssp, d in data.items():
    s = headline_stats(compute_G(d["gy"], d["gs"], 0.5, "arithmetic"))
    print(f"{ssp}: mean_relchange={s['mean_relchange']:.2f}%, "
          f"pct_zero_2100={s['pct_zero_2100']:.2f}%")
 
print("\n--- Weight-sweep range (arithmetic form) ---")
for ssp in FILES:
    sub = sweep_df[sweep_df.ssp == ssp]
    print(f"{ssp}: mean_relchange range = "
          f"[{sub.mean_relchange.min():.2f}, {sub.mean_relchange.max():.2f}]")
 
print("\n--- Monte Carlo (weight + form) rank stability ---")
for ssp in FILES:
    sub = mc_df[mc_df.ssp == ssp]
    print(f"{ssp}: median rank_rho = {sub.rank_rho.median():.4f}, "
          f"mean_relchange range = [{sub.mean_relchange.min():.2f}, {sub.mean_relchange.max():.2f}]")
 
print("\n--- Variance decomposition (summer, w=0.5) ---")
print(var_df.round(1).to_string(index=False))
 
print("\n--- Basin classification sensitivity ---")
print(div_summary_df.round(2).to_string(index=False))
 
print("\n--- Seasonal Yield variance share (w=0.5) ---")
print(seasonal_df.pivot(index="season", columns="ssp", values="yield_share").round(1))
 

#%% Weight sweep comparison

plt.rcParams.update({"font.size": 11, "figure.dpi": 150})
colors = {"SSP2-4.5": "#2b6cb0", "SSP5-8.5": "#c05621"}
 
fig, ax = plt.subplots(figsize=(7.5, 4.8))
for ssp in FILES:
    sub = sweep_df[sweep_df.ssp == ssp]
    ax.plot(sub["weight"], sub["mean_relchange"], color=colors[ssp], lw=2, label=ssp)
ax.axvline(0.5, color="gray", ls="--", lw=1)
ax.set_xlabel("Weight on Glacier Yield (w)")
ax.set_ylabel("Mean relative change in Glacier Index (%)\n2090-2100 vs. 2015-2025, summer")
ax.set_title("Weight sensitivity: SSP2-4.5 vs. SSP5-8.5")
ax.legend(fontsize=9)
fig.tight_layout()
# fig.savefig("F:/HMA_glacio_hydro_index/Figures/fig_combined_weight_sweep.png")
# plt.close(fig)
 
#%%. MC distribution comparison
fig, axes = plt.subplots(1, 2, figsize=(12, 4.8), sharey=False)
for ax, ssp in zip(axes, FILES):
    sub = mc_df[mc_df.ssp == ssp]
    for form, c in zip(forms, ["#2b6cb0", "#38a169", "#805ad5"]):
        ax.hist(sub.loc[sub.form == form, "mean_relchange"], bins=40, alpha=0.5, label=form, color=c)
    ax.set_title(ssp)
    ax.set_xlabel("Mean relative change (%)")
    ax.set_ylabel("MC iterations")
    ax.legend(fontsize=8)
fig.suptitle("Monte Carlo distribution by functional form, both scenarios")
fig.tight_layout()
# fig.savefig("F:/HMA_glacio_hydro_index/Figures/fig_combined_mc_distribution.png")
# plt.close(fig)
 
#%% Variance decomposition comparison
fig, ax = plt.subplots(figsize=(6.5, 4.8))
x = np.arange(len(FILES))
ax.bar(x, var_df["storage_share"], label="Storage", color="#c05621")
ax.bar(x, var_df["yield_share"], bottom=var_df["storage_share"], label="Yield", color="#2b6cb0")
ax.bar(x, var_df["cov_share"], bottom=var_df["storage_share"] + var_df["yield_share"],
       label="Covariance", color="#a0aec0")
ax.set_xticks(x)
ax.set_xticklabels(var_df["ssp"])
ax.set_ylabel("Share of Var(G) (%)")
ax.set_title("Storage dominance at w=0.5:\nSSP2-4.5 vs. SSP5-8.5")
ax.legend(fontsize=9)
fig.tight_layout()
# fig.savefig("F:/HMA_glacio_hydro_index/Figures/fig_combined_variance_decomp.png")
# plt.close(fig)
 
#%% Seasonal Yield-share comparison
fig, ax = plt.subplots(figsize=(7.5, 4.8))
x = np.arange(len(SEASONS))
width = 0.35
for i, ssp in enumerate(FILES):
    sub = seasonal_df[seasonal_df.ssp == ssp].set_index("season").loc[SEASONS]
    ax.bar(x + (i - 0.5) * width, sub["yield_share"], width, label=ssp, color=colors[ssp])
ax.set_xticks(x)
ax.set_xticklabels(SEASONS)
ax.set_ylabel("Yield's share of Var(G) (%)")
ax.set_title("Seasonal Yield contribution:\nSSP2-4.5 vs. SSP5-8.5")
ax.legend(fontsize=9)
fig.tight_layout()
# fig.savefig("F:/HMA_glacio_hydro_index/Figures/fig_combined_seasonal.png")
# plt.close(fig)
