cat > scripts/run_all.py <<'PY'
import os
import yaml
import pandas as pd

from src.parse_sparc import parse_table1, parse_massmodels
from src.compute_compactness import compute_lambda

def _find_name_column(df):
    # Try common variants used in SPARC parsers
    candidates = {"galaxy","name","galname","object","id"}
    for col in df.columns:
        if str(col).strip().lower() in candidates:
            return col
    return None

def main():
    # --- Load constants and ensure numeric types ---
    with open("config.yaml") as f:
        CFG = yaml.safe_load(f)
    C = CFG.get("constants", {})
    G    = float(C.get("G_m3kg1s2"))
    c    = float(C.get("c_ms"))
    Msun = float(C.get("Msun_kg"))
    kpc  = float(C.get("kpc_m"))

    # --- Read SPARC tables ---
    tab1 = parse_table1("data/raw/SPARC_Lelli2016c.mrt.txt")
    # mass models not used here, but keep the call if you want to validate availability:
    # mm   = parse_massmodels("data/raw/MassModels_Lelli2016c.mrt.txt")

    # --- Compute compactness (coercion handled in compute_lambda) ---
    tab1 = compute_lambda(tab1, G=G, c=c, Msun=Msun, kpc=kpc)

    # --- Choose a sensible name column if available ---
    name_col = _find_name_column(tab1)
    if name_col is None:
        print("NOTE: No obvious name column found. Available columns:\n", list(tab1.columns))

    cols = [c for c in [name_col, "Mbar_Msun", "Reff_kpc", "lambda"] if c and c in tab1.columns]
    out = tab1[cols].copy() if cols else tab1[["Mbar_Msun","Reff_kpc","lambda"]].copy()

    os.makedirs("outputs/tables", exist_ok=True)
    out.to_csv("outputs/tables/SPARC_lambda_quickcheck.csv", index=False)

    print(f"name column: {name_col}")
    print(f"rows: {len(out)}; median λ = {out['lambda'].median():.3e}")
    print("OK: wrote outputs/tables/SPARC_lambda_quickcheck.csv")

if __name__ == "__main__":
    main()
PY
