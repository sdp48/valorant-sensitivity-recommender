from fastapi import FastAPI
from pathlib import Path
from typing import List, Optional

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

    return {**base, "current": current_block}


@app.post("/similar", response_model=List[SimilarPlayer])
def similar(req: SimilarRequest):
    # returns a dataframe; convert to records
    df = nearest_pro_examples(DF, target_edpi=req.edpi, k=req.k)
    records = df.to_dict(orient="records")
    return records