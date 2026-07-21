import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

pwd = Path(r"a:\Calibration_validation\IGM_MS\validation")

# Choose one:
# "stock" = plot vali_obs_sim.csv
# "rate"  = plot vali_pairs_for_fig.csv
plot_type = "rate"

# Plot configurations
configs = {
    "stock": {
        "file_name": "vali_obs_sim.csv",
        "site_col": "site_name",
        "obs_col": "obd",
        "model_cols": ["sim_DayCent", "sim_DayCent-IGM"],
        "model_names": ["DayCent", "DayCent-IGM"],
        "xlabel": "Observed SOC (g/m²)",
        "ylabel": "Simulated SOC (g/m²)",
        "unit": "g/m²",
        "out_png": "DayCent_vs_DayCentIGM_validation.png",
    },
    "rate": {
        "file_name": "vali_pairs_for_fig.csv",
        "site_col": "pair_name",
        "obs_col": "obd_rate",
        "model_cols": ["DayCent_rate", "DayCent-IGM_rate"],
        "model_names": ["DayCent", "DayCent-IGM"],
        "xlabel": "Observed SOC change rate (Mg/ha/yr)",
        "ylabel": "Simulated SOC change rate (Mg/ha/yr)",
        "unit": "Mg/ha/yr",
        "out_png": "DayCent_vs_DayCentIGM_delta_rate.png",
    },
}

cfg = configs[plot_type]

file_path = pwd / cfg["file_name"]
out_png = pwd / cfg["out_png"]

site_col = cfg["site_col"]
obs_col = cfg["obs_col"]
model_cols = cfg["model_cols"]
model_names = cfg["model_names"]

# Read data
df = pd.read_csv(file_path)

required_cols = [site_col, obs_col] + model_cols
missing_cols = [col for col in required_cols if col not in df.columns]

if missing_cols:
    raise ValueError(
        f"Missing required columns in {file_path.name}: {missing_cols}\n"
        f"Available columns are: {df.columns.tolist()}"
    )

if plot_type == "rate":    
    df["obs_Mg_ha_yr"] = df[obs_col] 
    for model_col, model_name in zip(model_cols, model_names):
        clean_model_name = model_name.replace("-", "")
        new_col = f"{clean_model_name}_Mg_ha_yr"
        df[new_col] = df[model_col] 

# Metric functions
def calc_metrics(obd, sim):
    obd = pd.to_numeric(obd, errors="coerce")
    sim = pd.to_numeric(sim, errors="coerce")
    mask = np.isfinite(obd) & np.isfinite(sim)
    obs = np.asarray(obd[mask], dtype=float)
    sim = np.asarray(sim[mask], dtype=float)
    if len(obs) < 2:
        return np.nan, np.nan, np.nan, np.nan, np.nan, np.nan

    obs_ss = np.sum((obs - np.mean(obs)) ** 2)
    if obs_ss == 0:
        r2 = np.nan
        nse = np.nan
    else:
        r = np.corrcoef(obs, sim)[0, 1]
        r2 = r ** 2
        nse = 1 - np.sum((obs - sim) ** 2) / obs_ss        

    rmse = np.sqrt(np.mean((sim - obs) ** 2))
    bias = np.mean(sim - obs)

    if len(np.unique(obs)) < 2:
        slope = np.nan
        intercept = np.nan
    else:
        slope, intercept = np.polyfit(obs, sim, 1)
    return r2, nse, rmse, bias, slope, intercept

# Plot settings
sites = sorted(df[site_col].dropna().unique())

cmap = plt.get_cmap("tab20")
site_colors = {site: cmap(i % 20) for i, site in enumerate(sites)}

fig, axes = plt.subplots(1, 2, figsize=(12, 5.5), sharex=True, sharey=True)

title_fs = 16
axis_label_fs = 15
tick_fs = 13
stat_fs = 13
legend_fs = 12
legend_title_fs = 14

# Axis limits
all_values = pd.concat(
    [df[obs_col]] + [df[col] for col in model_cols],
    axis=0
)
all_values = pd.to_numeric(all_values, errors="coerce").dropna()

min_val = all_values.min()
max_val = all_values.max()

if min_val == max_val:
    pad = abs(min_val) * 0.1 if min_val != 0 else 1
else:
    pad = (max_val - min_val) * 0.08

lim_min = min_val - pad
lim_max = max_val + pad

# Make panels
for ax, model_col, model_name in zip(axes, model_cols, model_names):
    for site in sites:
        sub = df[df[site_col] == site]

        ax.scatter(
            sub[obs_col],
            sub[model_col],
            color=site_colors[site],
            label=site,
            alpha=0.8,
            s=45
        )

    # 1:1 line
    ax.plot(
        [lim_min, lim_max],
        [lim_min, lim_max],
        color="red",
        linewidth=1.2,
        linestyle="--",
        label="1:1 line"
    )

    r2, nse, rmse, bias, slope, intercept = calc_metrics(
        df[obs_col],
        df[model_col]
    )

    # Fitted linear regression line
    if np.isfinite(slope) and np.isfinite(intercept):
        ax.plot(
            [lim_min, lim_max],
            [slope * lim_min + intercept, slope * lim_max + intercept],
            color="blue",
            linewidth=1.2,
            linestyle="-",
            label="Fitted line"
        )

    if plot_type == "rate":
        clean_model_name = model_name.replace("-", "")
        #sim_tco2e_col = f"{clean_model_name}_tCO2e_ha_yr"
        #obs_tco2e_mean = df["obs_tCO2e_ha_yr"].mean()
        obs_SOC_mean = df["obs_Mg_ha_yr"].mean()
        sim_SOC_col = f"{clean_model_name}_Mg_ha_yr"        
        sim_SOC_mean = df[sim_SOC_col].mean()      
        
        stat_text = (
            f"R² = {r2:.4f}\n"
            f"NSE = {nse:.4f}\n"
            f"RMSE = {rmse:.3f} {cfg['unit']}\n"            
            f"Bias = {bias:.3f} {cfg['unit']}\n"
            f"Obs. = {obs_SOC_mean:.3f} Mg/ha/yr\n"
            f"Sim. = {sim_SOC_mean:.3f} Mg/ha/yr"
        )
    else:
        stat_text = (
            f"R² = {r2:.3f}\n"
            f"NSE = {nse:.3f}\n"
            f"RMSE = {rmse:.1f} {cfg['unit']}\n"
            f"Bias = {bias:.1f} {cfg['unit']}"
        )

    ax.text(
        0.06, 0.94,
        stat_text,
        transform=ax.transAxes,
        va="top",
        ha="left",
        fontsize=stat_fs
    )

    if np.isfinite(slope) and np.isfinite(intercept):
        eq_text = f"y = {slope:.3f}x {'+' if intercept >= 0 else '-'} {abs(intercept):.3f}"
    else:
        eq_text = "y = NA"

    ax.text(
        0.97, 0.05,
        eq_text,
        transform=ax.transAxes,
        va="bottom",
        ha="right",
        fontsize=stat_fs
    )

    ax.set_title(model_name, fontsize=title_fs)
    ax.set_xlabel(cfg["xlabel"], fontsize=axis_label_fs)
    ax.tick_params(axis="both", labelsize=tick_fs)

    ax.set_xlim(lim_min, lim_max)
    ax.set_ylim(lim_min, lim_max)
    ax.grid(True, alpha=0.3)

axes[0].set_ylabel(cfg["ylabel"], fontsize=axis_label_fs)

# Legend
if plot_type == "stock":
    handles, labels = axes[0].get_legend_handles_labels()
    legend = fig.legend(
        handles,
        labels,
        title="Site name",
        loc="center left",
        bbox_to_anchor=(0.86, 0.54),
        frameon=False,
        fontsize=legend_fs,
        markerscale=1.2
    )
    legend.get_title().set_fontsize(legend_title_fs)

plt.tight_layout(rect=[0, 0, 0.86, 1])
plt.savefig(out_png, dpi=600, bbox_inches="tight")
plt.show()

print(f"Figure saved to: {out_png}")

# python IGMpaper_plot_R2_NSE.py
