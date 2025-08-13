import os, yaml
from src.parse_sparc import parse_table1
from src.compute_compactness import compute_lambda

def main():
    # Load constants from config.yaml
    C = yaml.safe_load(open("config.yaml"))["constants"]
    G    = float(C["G_m3kg1s2"])
    c    = float(C["c_ms"])
    Msun = float(C["Msun_kg"])
    kpc  = float(C["kpc_m"])

    # Parse SPARC + compute compactness λ
    tab1 = compute_lambda(parse_table1("data/raw/SPARC_Lelli2016c.mrt.txt"),
                          G=G, c=c, Msun=Msun, kpc=kpc)

    # Reviewer-facing quick table
    os.makedirs("outputs/tables", exist_ok=True)
    cols = ["Galaxy", "Mbar_Msun", "Reff_kpc", "lambda"]
    tab1[cols].to_csv("outputs/tables/SPARC_lambda_quickcheck.csv", index=False)

    print(f"rows={len(tab1)}; median λ={tab1['lambda'].median():.3e}; "
          "wrote outputs/tables/SPARC_lambda_quickcheck.csv")

if __name__ == "__main__":
    main()
