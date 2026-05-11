from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import base64
import numpy as np
import cv2
from services.face import detect_face

router = APIRouter(prefix="/face", tags=["face"])


class AnalyzeFaceRequest(BaseModel):
    image_data: str


class LandmarkPoint(BaseModel):
    x: float
    y: float
    z: float


class FaceResponse(BaseModel):
    detected: bool
    landmarks: list[LandmarkPoint]
    blendshapes: dict
    face_metrics: dict
    landmark_count: int


def decode_image(image_data: str) -> np.ndarray:
    if "," in image_data:
        image_data = image_data.split(",")[1]
    image_bytes = base64.b64decode(image_data)
    image_array = np.frombuffer(image_bytes, dtype=np.uint8)
    return cv2.imdecode(image_array, cv2.IMREAD_COLOR)


@router.post("/analyze", response_model=FaceResponse)
def analyze_face(request: AnalyzeFaceRequest):
    try:
        image = decode_image(request.image_data)
    except Exception:
        raise HTTPException(status_code=400, detail="No se pudo decodificar la imagen")

    result = detect_face(image)

    return FaceResponse(
        detected=result["detected"],
        landmarks=result.get("landmarks", []),
        blendshapes=result.get("blendshapes", {}),
        face_metrics=result.get("face_metrics", {}),
        landmark_count=result.get("landmark_count", 0),
    )