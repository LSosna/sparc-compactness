import pandas as pd

def apply_cuts(df: pd.DataFrame, inc_min: float, inc_max: float, q_max: int) -> pd.DataFrame:
    out = df.copy()
    # force numeric where it matters
    for col in ["Inc","Q","Reff_kpc","lambda"]:
        out[col] = pd.to_numeric(out[col], errors="coerce")
    mask = (
        (out["Q"] <= q_max) &
        # STRICT inequalities to match paper: inc_min < Inc < inc_max
        (out["Inc"] > inc_min) & (out["Inc"] < inc_max) &
        (out["Reff_kpc"] > 0) &
        out["lambda"].notna()
    )
    return out.loc[mask].reset_index(drop=True)
