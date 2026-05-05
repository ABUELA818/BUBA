from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.calibration import calibrate

router = APIRouter(prefix="/calibration", tags=["calibration"])


class LandmarkPoint(BaseModel):
    x: float
    y: float
    z: float


class CalibrateRequest(BaseModel):
    landmarks: list[LandmarkPoint]
    height_cm: float


class CalibrateResponse(BaseModel):
    success: bool
    scale_factor: float | None
    segments: dict
    message: str


@router.post("/compute", response_model=CalibrateResponse)
def compute_calibration(request: CalibrateRequest):
    if not request.landmarks:
        raise HTTPException(status_code=400, detail="No se recibieron landmarks")

    landmarks = [{"x": lm.x, "y": lm.y, "z": lm.z} for lm in request.landmarks]
    result = calibrate(landmarks, request.height_cm)

    return CalibrateResponse(**result)