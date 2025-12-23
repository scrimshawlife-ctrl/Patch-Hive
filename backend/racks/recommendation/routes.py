"""Routes for rack layout recommendations."""

from __future__ import annotations

from fastapi import APIRouter

from .models import RackRecommendationRequest, RackRecommendationResponse
from .recommend import recommend_layouts

router = APIRouter()


@router.post("/recommend-layout", response_model=RackRecommendationResponse)
def recommend_rack_layout(payload: RackRecommendationRequest) -> RackRecommendationResponse:
    return recommend_layouts(
        rack_hp=payload.rack_hp,
        modules=payload.modules,
        connections=payload.connection_frequencies,
    )
