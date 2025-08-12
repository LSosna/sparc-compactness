import numpy as np
import pandas as pd

def compute_lambda(df, G, c, Msun, kpc):
    Mstar = 0.5 * df["L36_1e9Lsun"] * 1e9    # Msun
    Mgas  = 1.33 * df["MHI_1e9Msun"] * 1e9   # Msun
    Mbar  = Mstar + Mgas
    lam = (G * (Mbar * Msun)) / (df["Reff_kpc"] * kpc * c**2)
    out = df.copy()
    out["Mbar_Msun"] = Mbar
    out["lambda"] = lam
    return out

def select_samples(df, Q_max, inc_min, inc_max):
    sel = df.dropna(subset=["lambda","Reff_kpc","Inc","Q"]).copy()
    sel = sel[sel["Reff_kpc"]>0]
    strict = sel[(sel["Q"]<=Q_max) & (sel["Inc"]>inc_min) & (sel["Inc"]<inc_max)].copy()
    return strict
