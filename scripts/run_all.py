import os
import yaml
import pandas as pd

from src.parse_sparc import parse_table1, parse_massmodels
from src.compute_compactness import compute_lambda

# --- Load config and cast constants to float ---
with open("config.yaml") as f:
    CFG = yaml.safe_load(f)

CONST = CFG.get("constants", {})
G    = float(CONST.get("G_m3kg1s2"))
c    = float(CONST.get("c_ms"))
Msun = float(CONST.get("Msun_kg"))
kpc  = float(CONST.get("kpc_m"))

# --- Parse SPARC tables ---
tab1 = parse_table1("data/raw/SPARC_Lelli2016c.mrt.txt")
mm   = parse_massmodels("data/raw/MassModels_Lelli2016c.mrt.txt")

# --- Compute lambda with explicit numeric types ---
tab1 = compute_lambda(tab1, G=G, c=c, Msun=Msun, kpc=kpc)

# Minimal save to prove run completes
os.makedirs("outputs/tables", exist_ok=True)
tab1[["galaxy","lambda"]].to_csv("outputs/tables/SPARC_lambda_quickcheck.csv", index=False)

print("OK: wrote outputs/tables/SPARC_lambda_quickcheck.csv")
