import pandas as pd

def compute_A(mm_df):
    # SPARC defaults: disk at M/L_3.6 = 0.5, bulge at 0.7; we adopt SPARC provided velocities as-is.
    df = mm_df.copy()
    df["Vbary2"] = df["Vgas"]**2 + df["Vdisk"]**2 + df["Vbul"]**2
    df = df[df["Vbary2"]>0]
    df["A"] = (df["Vobs"]**2) / df["Vbary2"]
    return df
