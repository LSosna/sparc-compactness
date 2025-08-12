from pathlib import Path
import yaml
import numpy as np
import pandas as pd

from src.parse_sparc import parse_table1, parse_massmodels
from src.compute_compactness import compute_lambda, select_samples
from src.massmodels_analysis import compute_A
from src.odr_fits import odr_loglog
from scipy import stats

CFG = yaml.safe_load(open("config.yaml"))

raw = Path("data/raw")
tab1 = parse_table1(raw/"SPARC_Lelli2016c.mrt.txt")
tab1 = compute_lambda(tab1,
                      G=CFG["constants"]["G_m3kg1s2"],
                      c=CFG["constants"]["c_ms"],
                      Msun=CFG["constants"]["Msun_kg"],
                      kpc=CFG["constants"]["kpc_m"])

# samples
strict = select_samples(tab1, **CFG["samples"]["strict"])
extended = select_samples(tab1, **CFG["samples"]["extended"])

# bootstrap median + CI
rng = np.random.default_rng(CFG["bootstrap"]["seed"])
def boot_median(x, n=CFG["bootstrap"]["n_iter"]):
    idx = rng.integers(0, len(x), size=(n,len(x)))
    meds = np.median(x[idx], axis=1)
    return float(np.median(x)), float(np.quantile(meds,0.025)), float(np.quantile(meds,0.975))

def shapiro_p(x):
    x = np.asarray(x)
    x = x[np.isfinite(x)]
    return float(stats.shapiro(np.log10(x[:5000]))[1])

strict_med, strict_lo, strict_hi = boot_median(strict["lambda"].values)
ext_med, ext_lo, ext_hi = boot_median(extended["lambda"].values)
strict_p = shapiro_p(strict["lambda"].values)
ext_p    = shapiro_p(extended["lambda"].values)

# ODR slopes
odr_strict = odr_loglog(np.log10(strict["Mbar_Msun"]), np.log10(strict["lambda"]))
odr_ext    = odr_loglog(np.log10(extended["Mbar_Msun"]), np.log10(extended["lambda"]))

# mass models → A
mm = parse_massmodels(raw/"MassModels_Lelli2016c.mrt.txt", use_ids=set(extended["Galaxy"]))
mmA = compute_A(mm)
mmA = mmA.merge(tab1[["Galaxy","lambda"]], left_on="ID", right_on="Galaxy", how="left")

nA_strict = int(mmA[mmA["ID"].isin(set(strict["Galaxy"]))]["A"].notna().sum())
nA_ext    = int(mmA[mmA["ID"].isin(set(extended["Galaxy"]))]["A"].notna().sum())

# save summary table
out = Path("outputs/tables"); out.mkdir(parents=True, exist_ok=True)
pd.DataFrame({
  "Sample":["Strict","Extended"],
  "N_gal":[strict["Galaxy"].nunique(), extended["Galaxy"].nunique()],
  "Median_lambda":[strict_med, ext_med],
  "CI_lo":[strict_lo, ext_lo], "CI_hi":[strict_hi, ext_hi],
  "Shapiro_p":[strict_p, ext_p],
  "ODR_slope":[odr_strict["b"], odr_ext["b"]],
  "ODR_sigma":[odr_strict["sb"], odr_ext["sb"]],
  "Pearson_r":[odr_strict["r"], odr_ext["r"]],
  "Sigma_excess_vs_0.5":[odr_strict["sig_excess"], odr_ext["sig_excess"]],
  "N_points_A":[nA_strict, nA_ext]
}).to_csv(out/"SPARC_compactness_crosscheck_summary.csv", index=False)

print("Done. Summary written to outputs/tables/SPARC_compactness_crosscheck_summary.csv")
