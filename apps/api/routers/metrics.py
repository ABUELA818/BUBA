from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.metrics import compute_metrics

router = APIRouter(prefix="/metrics", tags=["metrics"])


class MetricsRequest(BaseModel):
    joint_positions: list[list[float]]
    scale: float


class MetricsResponse(BaseModel):
    measurements: dict
    body_type: str
    confidence: str


@router.post("/compute", response_model=MetricsResponse)
def compute_body_metrics(request: MetricsRequest):
    if not request.joint_positions:
        raise HTTPException(status_code=400, detail="No se recibieron joint positions")

    result = compute_metrics(request.joint_positions, request.scale)
    return MetricsResponse(**result)