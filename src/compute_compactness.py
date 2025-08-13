import pandas as pd

def compute_lambda(df, G, c, Msun, kpc):
    df = df.copy()

    # Coerce SPARC columns to numeric to avoid '<U10' strings
    for col in ["L36_1e9Lsun", "MHI_1e9Msun", "Reff_kpc"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Masses in solar units
    Mstar = 0.5  * df["L36_1e9Lsun"] * 1e9   # Msun
    Mgas  = 1.33 * df["MHI_1e9Msun"] * 1e9   # Msun
    Mbar  = Mstar + Mgas                     # Msun

    # Convert to kg when forming λ
    lam = (G * (Mbar * Msun)) / (df["Reff_kpc"] * kpc * c**2)

    out = df.copy()
    out["Mbar_Msun"] = Mbar
    out["lambda"]    = lam
    return out
