import yaml
import json
from pathlib import Path
import numpy as np
import pandas as pd

# This imports the functions you will create in the `src` directory
# Make sure you have created these files in your repo first
from src.parse_sparc import parse_table1, parse_massmodels
from src.compute_compactness import compute_lambda, select_samples
from src.odr_fits import odr_loglog
from src.massmodels_analysis import compute_A
from src.coherence import coherence

print("--- Starting Analysis Pipeline ---")

# --- 1. Load Configuration ---
CFG = yaml.safe_load(open("config.yaml"))
print("Loaded configuration.")

# --- 2. Parse Raw Data ---
raw_path = Path("data/raw")
output_path = Path("outputs/tables")
output_path.mkdir(parents=True, exist_ok=True)

tab1 = parse_table1(raw_path / "SPARC_Lelli2016c.mrt.txt")
tab1_with_lambda = compute_lambda(tab1, **CFG["constants"])
print(f"Parsed {len(tab1_with_lambda)} galaxies from Table 1.")

# --- 3. Define Samples ---
strict_cfg = CFG["samples"]["strict"]
extended_cfg = CFG["samples"]["extended"]

strict_sample = select_samples(tab1_with_lambda, **strict_cfg)
extended_sample = select_samples(tab1_with_lambda, **extended_cfg)
print(f"Created strict sample (N={len(strict_sample)}) and extended sample (N={len(extended_sample)}).")

# --- 4. Calculate Headline Statistics ---
rng = np.random.default_rng(CFG["bootstrap"]["seed"])

def boot_median(x, n_iter):
    if len(x) == 0:
        return np.nan, np.nan, np.nan
    idx = rng.integers(0, len(x), size=(n_iter, len(x)))
    meds = np.median(x[idx], axis=1)
    return float(np.median(x)), float(np.quantile(meds, 0.025)), float(np.quantile(meds, 0.975))

def shapiro_p(x):
    from scipy import stats
    if len(x) < 3:
        return np.nan
    # Shapiro-Wilk test is reliable for N < 5000
    return float(stats.shapiro(np.log10(x[:5000]))[1])

strict_med, strict_lo, strict_hi = boot_median(strict_sample["lambda"].values, CFG["bootstrap"]["n_iter"])
ext_med, ext_lo, ext_hi = boot_median(extended_sample["lambda"].values, CFG["bootstrap"]["n_iter"])

strict_p_val = shapiro_p(strict_sample["lambda"].values)
ext_p_val = shapiro_p(extended_sample["lambda"].values)

# --- 5. Perform ODR Fits ---
odr_strict = odr_loglog(np.log10(strict_sample["Mbar_Msun"]), np.log10(strict_sample["lambda"]))
odr_ext = odr_loglog(np.log10(extended_sample["Mbar_Msun"]), np.log10(extended_sample["lambda"]))
print("Performed ODR fits.")

# --- 6. Analyze Mass Models ---
mm = parse_massmodels(raw_path / "MassModels_Lelli2016c.mrt.txt", use_ids=set(extended_sample["Galaxy"]))
mmA = compute_A(mm, **CFG["stellar_ML_36"])

gal_lam = tab1_with_lambda[["Galaxy", "lambda"]]
mmA = mmA.merge(gal_lam, left_on="ID", right_on="Galaxy", how="left")

nA_strict = int(mmA[mmA["ID"].isin(set(strict_sample["Galaxy"]))]["A"].notna().sum())
nA_ext = int(mmA[mmA["ID"].isin(set(extended_sample["Galaxy"]))]["A"].notna().sum())

# --- 7. Save Summary CSV ---
summary_df = pd.DataFrame({
    "Sample": ["Strict", "Extended"],
    "N_gal": [strict_sample["Galaxy"].nunique(), extended_sample["Galaxy"].nunique()],
    "Median_lambda": [strict_med, ext_med],
    "CI_lo": [strict_lo, ext_lo],
    "CI_hi": [strict_hi, ext_hi],
    "Shapiro_p": [strict_p_val, ext_p_val],
    "ODR_slope": [odr_strict["b"], odr_ext["b"]],
    "ODR_slope_err": [odr_strict["sb"], odr_ext["sb"]],
    "Pearson_r": [odr_strict["r"], odr_ext["r"]],
    "Sigma_excess_vs_0.5": [odr_strict["sig_excess"], odr_ext["sig_excess"]],
    "N_points_A": [nA_strict, nA_ext]
})

summary_filepath = output_path / "SPARC_compactness_crosscheck_summary.csv"
summary_df.to_csv(summary_filepath, index=False)
print(f"SUCCESS: Wrote summary to {summary_filepath}")

print("\n--- Pipeline Finished ---")
