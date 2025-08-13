import os, json, yaml, numpy as np
from scipy import odr
from src.parse_sparc import parse_table1
from src.compute_compactness import compute_lambda
from src.select_samples import apply_cuts

def odr_line(x, y, beta0=(0.7, -16.0)):
    model = odr.Model(lambda B, x: B[0]*x + B[1]); data = odr.RealData(x, y)
    fit = odr.ODR(data, model, beta0=list(beta0)).run()
    a, b = fit.beta; sa, sb = fit.sd_beta; return a, b, sa, sb

def do_fit(df, inc_min, inc_max, qmax):
    sub = apply_cuts(df, inc_min, inc_max, qmax)
    x = np.log10(sub["Mbar_Msun"].astype(float).to_numpy())
    y = np.log10(sub["lambda"].astype(float).to_numpy())
    a, b, sa, sb = odr_line(x, y); r = np.corrcoef(x, y)[0,1]; z = (a - 0.5)/sa
    return dict(N=int(len(sub)), slope=a, slope_err=sa, intercept=b, intercept_err=sb, r=r, z_sigma_vs_0p5=z)

def main():
    cfg = yaml.safe_load(open("config.yaml")); C = cfg["constants"]
    G, c, Msun, kpc = float(C["G_m3kg1s2"]), float(C["c_ms"]), float(C["Msun_kg"]), float(C["kpc_m"])
    df = compute_lambda(parse_table1("data/raw/SPARC_Lelli2016c.mrt.txt"), G, c, Msun, kpc)
    S = cfg["samples"]
    strict   = do_fit(df, S["strict"]["inc_min"],   S["strict"]["inc_max"],   S["strict"]["Q_max"])
    extended = do_fit(df, S["extended"]["inc_min"], S["extended"]["inc_max"], S["extended"]["Q_max"])
    os.makedirs("outputs/summary", exist_ok=True)
    json.dump({"strict": strict, "extended": extended},
              open("outputs/summary/mass_compactness_odr.json","w"), indent=2)
    p=lambda d: f"N={d['N']}; slope={d['slope']:.3f}±{d['slope_err']:.3f}; r={d['r']:.3f}; z_vs_0.5={d['z_sigma_vs_0p5']:.1f}σ"
    print("STRICT  :", p(strict)); print("EXTENDED:", p(extended))

if __name__ == "__main__": main()
