cat > scripts/summary_stats.py <<'PY'
import os, json, yaml, numpy as np, pandas as pd
from scipy.stats import shapiro
from src.parse_sparc import parse_table1
from src.compute_compactness import compute_lambda
from src.select_samples import apply_cuts

def bootstrap_ci_med(values, n_iter=20000, seed=12345):
    rng = np.random.default_rng(seed)
    vals = np.asarray(values, dtype=float)
    meds = []
    n = len(vals)
    for _ in range(n_iter):
        samp = rng.choice(vals, size=n, replace=True)
        meds.append(np.median(samp))
    lo, hi = np.percentile(meds, [2.5, 97.5])
    return float(lo), float(hi)

def one_sample(name, df, inc_min, inc_max, qmax):
    sub = apply_cuts(df, inc_min, inc_max, qmax)
    lam = np.asarray(sub["lambda"], dtype=float)
    log10lam = np.log10(lam)
    med = float(np.median(lam))
    lo, hi = bootstrap_ci_med(lam)
    # Shapiro on log10 λ (as in paper)
    W, p = shapiro(log10lam)
    out = dict(
        N=int(len(sub)),
        median_lambda=med,
        ci95_low=lo,
        ci95_high=hi,
        shapiro_W=float(W),
        shapiro_p=float(p),
        inc_min=float(inc_min),
        inc_max=float(inc_max),
        Q_max=int(qmax),
    )
    return out

def main():
    with open("config.yaml") as f:
        cfg = yaml.safe_load(f)
    C = cfg["constants"]
    G, c, Msun, kpc = float(C["G_m3kg1s2"]), float(C["c_ms"]), float(C["Msun_kg"]), float(C["kpc_m"])

    tab1 = parse_table1("data/raw/SPARC_Lelli2016c.mrt.txt")
    tab1 = compute_lambda(tab1, G=G, c=c, Msun=Msun, kpc=kpc)

    S = cfg["samples"]
    strict   = one_sample("strict",   tab1, S["strict"]["inc_min"],   S["strict"]["inc_max"],   S["strict"]["Q_max"])
    extended = one_sample("extended", tab1, S["extended"]["inc_min"], S["extended"]["inc_max"], S["extended"]["Q_max"])

    os.makedirs("outputs/summary", exist_ok=True)
    out = {"strict": strict, "extended": extended}
    with open("outputs/summary/lambda_summary.json", "w") as f:
        json.dump(out, f, indent=2)

    # Console summary
    def fmt(d):
        return (f"N={d['N']}; median={d['median_lambda']:.3e}; "
                f"95% CI=[{d['ci95_low']:.3e}, {d['ci95_high']:.3e}]; "
                f"Shapiro p={d['shapiro_p']:.2e}")
    print("STRICT  :", fmt(strict))
    print("EXTENDED:", fmt(extended))

if __name__ == "__main__":
    main()
PY
