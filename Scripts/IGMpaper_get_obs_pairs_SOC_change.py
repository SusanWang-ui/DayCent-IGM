from pathlib import Path
import pandas as pd

pwd = Path(r"a:\Calibration_validation\IGM_MS\validation") 

dSOC_path = pwd / "obs_pairs.csv"
obd_path = pwd / "all_sim_obd.csv"

dSOC = pd.read_csv(dSOC_path)
obd = pd.read_csv(obd_path)

obs = obd.copy()

obs["treat_name"] = obs["treat_name"].astype(str) + "_" + obs["time"].astype(str)
obs["SOC_change"] = obs["obd"] - obs["ini_SOC_obs"]
obs = obs.drop(columns=["somsc_sim", "ini_SOC_obs"], errors="ignore")

# Join obs to treatment 1
merg_df1 = dSOC.merge(
    obs,
    how="left",
    left_on=["site_name", "treat_1", "time"],
    right_on=["site_name", "treat_name", "time"],
    suffixes=("", "_obs1"))

merg_df1 = merg_df1.rename(
    columns={
        "obd": "treat1_Obs",
        "iniSOC": "treat1_iniSOC",
        "SOC_change": "treat1_socChange"
    })

# Remove helper column from first join if present
merg_df1 = merg_df1.drop(columns=["treat_name"], errors="ignore")

# Join obs to treatment 2
merg_df2 = merg_df1.merge(
    obs,
    how="left",
    left_on=["site_name", "treat_2", "ini_year", "numOfYears", "time"],
    right_on=["site_name", "treat_name", "ini_year", "numOfYears", "time"],
    suffixes=("", "_obs2"))

merg_df2 = merg_df2.rename(
    columns={
        "obd": "treat2_Obs",
        "iniSOC": "treat2_iniSOC",
        "SOC_change": "treat2_socChange"
    })

merg_df2 = merg_df2.drop(columns=["treat_name"], errors="ignore")

# Filter rows with valid initial SOC
merg_df2 = merg_df2[
    (merg_df2["treat1_iniSOC"] > 0) &
    (merg_df2["treat2_iniSOC"] > 0)
].copy()

# Calculate SOC stock differences between treatment pairs
soc_change = merg_df2.copy()

soc_change["SOC_changeY"] = soc_change["treat1_Obs"] - soc_change["treat2_Obs"]
soc_change["SOC_change"] = soc_change["treat1_socChange"] - soc_change["treat2_socChange"]
soc_change["iniSOC_dif"] = soc_change["treat1_iniSOC"] - soc_change["treat2_iniSOC"]
soc_change["SOC_change_rate_t.ha.y"] = (
    soc_change["SOC_change"] / soc_change["numOfYears"] / 100)

soc_change.to_csv(pwd / "soc_diff.csv",index=False)

# python IGMpaper_get_obs_pairs_SOC_change.py