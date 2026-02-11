from pydantic import BaseModel
from typing import Literal, Optional, List


AimStyle = Literal["wrist", "hybrid", "arm"]
Goal = Literal["balanced", "precision", "speed"]
Pad = Literal["small", "medium", "large"]


class RecommendRequest(BaseModel):
    dpi: int
    aim_style: AimStyle
    goal: Goal
    pad: Pad
    current_sensitivity: Optional[float] = None


class RecommendResponse(BaseModel):
    dpi: int
    target_cm360: dict
    suggested_sens: dict
    mid_edpi: float
    current: Optional[dict] = None


class SimilarRequest(BaseModel):
    edpi: float
    k: int = 10


class SimilarPlayer(BaseModel):
    player: str
    edpi: float
    sens: Optional[float] = None
    dpi: Optional[float] = None
    cm360: Optional[float] = None