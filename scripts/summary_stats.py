import os, json, yaml, numpy as np
from scipy.stats import shapiro
from src.parse_sparc import parse_table1
from src.compute_compactness import compute_lambda
from src.select_samples import apply_cuts

def bootstrap_ci_med(values, n_iter=20000, seed=12345):
    rng = np.random.default_rng(seed); vals = np.asarray(values, dtype=float)
    meds = [np.median(rng.choice(vals, size=len(vals), replace=True)) for _ in range(n_iter)]
    lo, hi = np.percentile(meds, [2.5, 97.5]); return float(lo), float(hi)

def summarize(df, inc_min, inc_max, qmax):
    sub = apply_cuts(df, inc_min, inc_max, qmax)
    lam = sub["lambda"].astype(float).to_numpy(); log10lam = np.log10(lam)
    med = float(np.median(lam)); lo, hi = bootstrap_ci_med(lam); W, p = shapiro(log10lam)
    return dict(N=int(len(sub)), median_lambda=med, ci95_low=lo, ci95_high=hi,
                shapiro_W=float(W), shapiro_p=float(p),
                inc_min=float(inc_min), inc_max=float(inc_max), Q_max=int(qmax))

def main():
    cfg = yaml.safe_load(open("config.yaml")); C = cfg["constants"]
    G, c, Msun, kpc = float(C["G_m3kg1s2"]), float(C["c_ms"]), float(C["Msun_kg"]), float(C["kpc_m"])
    tab1 = compute_lambda(parse_table1("data/raw/SPARC_Lelli2016c.mrt.txt"), G, c, Msun, kpc)
    S = cfg["samples"]
    strict   = summarize(tab1, S["strict"]["inc_min"],   S["strict"]["inc_max"],   S["strict"]["Q_max"])
    extended = summarize(tab1, S["extended"]["inc_min"], S["extended"]["inc_max"], S["extended"]["Q_max"])
    os.makedirs("outputs/summary", exist_ok=True)
    json.dump({"strict": strict, "extended": extended},
              open("outputs/summary/lambda_summary.json","w"), indent=2)
    fmt=lambda d: f"N={d['N']}; median={d['median_lambda']:.3e}; 95% CI=[{d['ci95_low']:.3e}, {d['ci95_high']:.3e}]; Shapiro p={d['shapiro_p']:.2e}"
    print("STRICT  :", fmt(strict)); print("EXTENDED:", fmt(extended))

if __name__ == "__main__": main()
