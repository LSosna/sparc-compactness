import pandas as pd

def parse_table1(path):
    rows = []
    with open(path, "r") as f:
        for line in f:
            tok = line.strip().split()
            if len(tok) < 18:
                continue
            # crude header/line guard: attempt to parse key columns
            try:
                int(tok[1]); float(tok[2]); float(tok[3]); int(tok[4])
                float(tok[5]); float(tok[6]); float(tok[7]); float(tok[8])
                float(tok[9]); float(tok[10]); float(tok[11]); float(tok[12])
                float(tok[13]); float(tok[14]); float(tok[15]); float(tok[16])
                int(tok[17])
            except Exception:
                continue
            rows.append(tok[:18])
    cols = ["Galaxy","T","D_Mpc","e_D","f_D","Inc","e_Inc","L36_1e9Lsun","e_L36",
            "Reff_kpc","SBeff","Rdisk_kpc","SBdisk","MHI_1e9Msun","RHI_kpc",
            "Vflat_kms","e_Vflat","Q"]
    df = pd.DataFrame(rows, columns=cols)
    for c in cols[1:]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    return df

def parse_massmodels(path, use_ids=None):
    rows = []
    with open(path, "r") as f:
        for line in f:
            tok = line.strip().split()
            if len(tok) < 8:
                continue
            gid = tok[0]
            if use_ids and gid not in use_ids:
                continue
            try:
                D, R, Vobs, eV, Vgas, Vdisk, Vbul = map(float, tok[1:8])
            except Exception:
                continue
            rows.append([gid, D, R, Vobs, eV, Vgas, Vdisk, Vbul])
    return pd.DataFrame(rows, columns=["ID","D_Mpc","R_kpc","Vobs","e_Vobs","Vgas","Vdisk","Vbul"])
