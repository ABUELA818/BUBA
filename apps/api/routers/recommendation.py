from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.recommendation import get_recommendations

router = APIRouter(prefix="/recommendation", tags=["recommendation"])


class RecommendationRequest(BaseModel):
    body_type: str
    measurements: dict


class RecommendationResponse(BaseModel):
    body_type: str
    description: str
    recommendations: dict
    size_estimate: dict


@router.post("/compute", response_model=RecommendationResponse)
def compute_recommendation(request: RecommendationRequest):
    if not request.body_type:
        raise HTTPException(status_code=400, detail="body_type es requerido")

    result = get_recommendations(request.body_type, request.measurements)
    return RecommendationResponse(**result)