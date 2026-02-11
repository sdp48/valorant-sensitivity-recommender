from __future__ import annotations
import pandas as pd

VALORANT_YAW = 0.07

def compute_edpi(dpi: float, sens: float) -> float:
    return dpi * sens

def compute_cm360(dpi: float, sens: float, yaw: float = VALORANT_YAW) -> float:
    denom = dpi * sens * yaw
    if denom <= 0:
        return float("inf")
    return (360.0 * 2.54) / denom

def sens_from_cm360(dpi: float, target_cm360: float, yaw: float = VALORANT_YAW) -> float:
    denom = dpi * yaw * target_cm360
    if denom <= 0:
        return 0.0
    return (360.0 * 2.54) / denom

def choose_target_cm360(aim_style: str, goal: str, pad: str) -> tuple[float, float]:
    style = aim_style.lower()
    if style == "wrist":
        low, high = 22.0, 35.0
    elif style == "hybrid":
        low, high = 30.0, 45.0
    else:  # arm
        low, high = 40.0, 65.0

    g = goal.lower()
    if g == "precision":
        low *= 1.10
        high *= 1.15
    elif g == "speed":
        low *= 0.90
        high *= 0.90

    p = pad.lower()
    if p == "small":
        low *= 0.90
        high *= 0.90
    elif p == "large":
        low *= 1.05
        high *= 1.05

    low = max(15.0, min(low, 90.0))
    high = max(low + 1.0, min(high, 120.0))
    return round(low, 1), round(high, 1)

def load_pro_csv(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)

    if "player" not in df.columns:
        raise ValueError("pro_sens.csv must include a 'player' column")

    # New format: player, sens, edpi (from Liquipedia)
    if {"sens", "edpi"}.issubset(df.columns):
        return df.copy()

    # Old format: player, dpi, sens
    if {"dpi", "sens"}.issubset(df.columns):
        df = df.copy()
        df["edpi"] = df["dpi"] * df["sens"]
        df["cm360"] = (360.0 * 2.54) / (df["dpi"] * df["sens"] * VALORANT_YAW)
        return df

    raise ValueError("pro_sens.csv must have either (player,sens,edpi) or (player,dpi,sens)")

def nearest_pro_examples(df: pd.DataFrame, target_edpi: float, k: int = 10) -> pd.DataFrame:
    tmp = df.copy()
    tmp["dist"] = (tmp["edpi"] - target_edpi).abs()
    cols = [c for c in ["player", "edpi", "sens", "dpi", "cm360"] if c in tmp.columns]
    return tmp.sort_values("dist").head(k)[cols]

def recommend_sensitivity(dpi: float, aim_style: str, goal: str, pad: str) -> dict:
    """
    Returns a recommendation bundle computed from your existing cm/360 rules.
    Designed to be used by BOTH Streamlit (client) and FastAPI (server).
    """
    low_cm, high_cm = choose_target_cm360(aim_style, goal, pad)
    mid_cm = (low_cm + high_cm) / 2.0

    # lower cm/360 => faster => higher sens
    rec_low_sens = sens_from_cm360(dpi, high_cm)  # slower end
    rec_high_sens = sens_from_cm360(dpi, low_cm)  # faster end

    mid_sens = sens_from_cm360(dpi, mid_cm)
    mid_edpi = compute_edpi(dpi, mid_sens)

    return {
        "dpi": int(dpi),
        "target_cm360": {"low": low_cm, "high": high_cm, "mid": round(mid_cm, 1)},
        "suggested_sens": {
            "low": round(rec_low_sens, 3),
            "high": round(rec_high_sens, 3),
            "mid": round(mid_sens, 3),
        },
        "mid_edpi": round(mid_edpi, 0),
    }