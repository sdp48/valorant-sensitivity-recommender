from fastapi import FastAPI
from pathlib import Path
from typing import List
from datetime import datetime

from api.db import init_db, insert_request, fetch_recent

from api.schemas import (
    RecommendRequest,
    RecommendResponse,
    SimilarRequest,
    SimilarPlayer,
)
from recommender.sens import (
    load_pro_csv,
    nearest_pro_examples,
    recommend_sensitivity,
    compute_edpi,
    compute_cm360,
)

app = FastAPI(title="Valorant Sensitivity API", version="1.0.0")
init_db()

# Load dataset once at startup
ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "pro_sens.csv"
DF = load_pro_csv(str(DATA_PATH))


@app.get("/health")
def health():
    return {"status": "ok", "players": int(len(DF))}


@app.post("/recommend", response_model=RecommendResponse)
def recommend(req: RecommendRequest):
    base = recommend_sensitivity(req.dpi, req.aim_style, req.goal, req.pad)

    current_block = None
    if req.current_sensitivity is not None:
        cur_edpi = compute_edpi(req.dpi, req.current_sensitivity)
        cur_cm = compute_cm360(req.dpi, req.current_sensitivity)
        current_block = {
            "sensitivity": round(req.current_sensitivity, 3),
            "edpi": round(cur_edpi, 0),
            "cm360": round(cur_cm, 1),
        }

    insert_request(
        dpi=req.dpi,
        aim_style=req.aim_style,
        goal=req.goal,
        pad=req.pad,
        mid_sens=base["suggested_sens"]["mid"],
        mid_edpi=base["mid_edpi"],
        created_at=datetime.utcnow().isoformat(),
    )

    return {**base, "current": current_block}


@app.post("/similar", response_model=List[SimilarPlayer])
def similar(req: SimilarRequest):
    # returns a dataframe; convert to records
    df = nearest_pro_examples(DF, target_edpi=req.edpi, k=req.k)
    records = df.to_dict(orient="records")
    return records


@app.get("/history")
def history(limit: int = 20):
    """
    Returns the most recent recommendation requests stored by the backend.
    """
    limit = max(1, min(limit, 200))
    return fetch_recent(limit=limit)