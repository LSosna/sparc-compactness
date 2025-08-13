import os, yaml
from src.parse_sparc import parse_table1
from src.compute_compactness import compute_lambda

def main():
    C = yaml.safe_load(open("config.yaml"))["constants"]
    G=float(C["G_m3kg1s2"]); c=float(C["c_ms"]); Msun=float(C["Msun_kg"]); kpc=float(C["kpc_m"])

    tab1 = compute_lambda(
        parse_table1("data/raw/SPARC_Lelli2016c.mrt.txt"),
        G=G, c=c, Msun=Msun, kpc=kpc
    )

    os.makedirs("outputs/tables", exist_ok=True)
    tab1[["Galaxy","Mbar_Msun","Reff_kpc","lambda"]].to_csv(
        "outputs/tables/SPARC_lambda_quickcheck.csv", index=False
    )

if __name__ == "__main__":
    main()
