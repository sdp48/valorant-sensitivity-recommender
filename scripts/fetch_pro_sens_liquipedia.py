# scripts/fetch_pro_sens_liquipedia.py
from __future__ import annotations

import re
import time
import requests
import pandas as pd
from typing import Optional

LIQUIPEDIA_API = "https://liquipedia.net/valorant/api.php"
PAGE = "List_of_player_mouse_settings"

HEADERS = {
    "User-Agent": "ValorantRecommender/1.0 (https://github.com/shiv48/valorant-recommender; contact: shiv382005@yahoo.com)",
    "Accept-Encoding": "gzip",
}

def fetch_table_html() -> str:
    """
    Uses Liquipedia MediaWiki API (allowed) to parse the page into HTML.
    Note: action=parse is heavier, so don't spam it.
    """
    params = {
        "action": "parse",
        "page": PAGE,
        "prop": "text",
        "format": "json",
    }
    r = requests.get(LIQUIPEDIA_API, params=params, headers=HEADERS, timeout=20)
    r.raise_for_status()
    data = r.json()
    return data["parse"]["text"]["*"]

def clean_number(x) -> Optional[float]:
    if x is None:
        return None
    s = str(x).strip()
    # Keep digits + dot only (handles "0.35", "800", etc.)
    m = re.search(r"(\d+(\.\d+)?)", s)
    return float(m.group(1)) if m else None

def main():
    html = fetch_table_html()

    # Parse all tables from the HTML; pick the one that includes "Sensitivity" & "DPI"
    from io import StringIO
    tables = pd.read_html(StringIO(html))
    target = None
    for t in tables:
        cols = [c.lower() for c in t.columns.astype(str).tolist()]
        if any("dpi" in c for c in cols) and any("sens" in c or "sensitivity" in c for c in cols):
            target = t
            break

    if target is None:
        raise RuntimeError("Couldn't find the mouse settings table. Page structure may have changed.")

    # Try to standardize column names
    df = target.copy()
    df.columns = [str(c).strip() for c in df.columns]

    # Common columns on that page are like: Player, DPI, Sensitivity (and others)
    # We only need: player, dpi, sens
    # Find best matches:
    player_col = next((c for c in df.columns if "player" in c.lower()), None)
    dpi_col = next((c for c in df.columns if "dpi" in c.lower()), None)
    edpi_col = next((c for c in df.columns if c.lower() == "edpi"), None)
    if edpi_col is None:
        raise RuntimeError(f"Could not find eDPI column. Columns found: {df.columns.tolist()}")

    def find_sens_column(columns):
        preferred = [
            "sensitivity",
            "in-game sensitivity",
            "ingame sensitivity",
            "valorant sensitivity"
        ]
        cols_lower = {c.lower(): c for c in columns}
        for p in preferred:
            for k, v in cols_lower.items():
                if p == k:
                    return v
        return None

    sens_col = find_sens_column(df.columns)
    if sens_col is None:
        raise RuntimeError(f"Could not find in-game sensitivity column. Columns found: {df.columns.tolist()}")

    if not (player_col and sens_col and edpi_col):
        raise RuntimeError(f"Missing expected columns. Found: {df.columns.tolist()}")

    out = pd.DataFrame({
        "player": df[player_col].astype(str).str.strip(),
        "sens": df[sens_col].apply(clean_number),
        "edpi": df[edpi_col].apply(clean_number),
    })

    tmp = out.dropna(subset=["sens", "edpi"]).copy()

    out = out.dropna(subset=["player", "sens", "edpi"])

    before = len(out)

    out = out[
        (out["sens"] >= 0.05) & (out["sens"] <= 2.0) &
        (out["edpi"] >= 120) & (out["edpi"] <= 800)
    ]

    after = len(out)
    print(f"[Sanity filter] Dropped {before - after} rows, kept {after}")

    # Optional: remove duplicates (keep first)
    out = out.drop_duplicates(subset=["player"], keep="first")

    out.to_csv("data/pro_sens.csv", index=False)
    print(f"Saved {len(out)} rows to data/pro_sens.csv")

if __name__ == "__main__":
    # Liquipedia API guideline: don't hammer parse endpoints.
    # We only do 1 request, so we're fine.
    main()
