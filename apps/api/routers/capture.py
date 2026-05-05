from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import base64
import numpy as np
import cv2
from services.pose import detect_pose
from services.stability import compute_stability

router = APIRouter(prefix="/capture", tags=["capture"])


class AnalyzeFrameRequest(BaseModel):
    image_data: str
    height_cm: float


class QualityIssue(BaseModel):
    code: str
    message: str
    severity: str


class LandmarkPoint(BaseModel):
    x: float
    y: float
    z: float


class AnalyzeFrameResponse(BaseModel):
    score: float
    accepted: bool
    issues: list[QualityIssue]
    orientation: str
    pose_detected: bool
    landmarks: list[LandmarkPoint]
    landmark_count: int
    stability_score: float


def decode_image(image_data: str) -> np.ndarray:
    if "," in image_data:
        image_data = image_data.split(",")[1]
    image_bytes = base64.b64decode(image_data)
    image_array = np.frombuffer(image_bytes, dtype=np.uint8)
    return cv2.imdecode(image_array, cv2.IMREAD_COLOR)


def analyze_image_quality(image: np.ndarray) -> tuple[float, list[QualityIssue]]:
    issues = []
    score = 1.0

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    brightness = float(np.mean(gray))
    if brightness < 50:
        issues.append(QualityIssue(
            code="LOW_BRIGHTNESS",
            message="La imagen está muy oscura. Busca mejor iluminación.",
            severity="error"
        ))
        score -= 0.4
    elif brightness > 220:
        issues.append(QualityIssue(
            code="HIGH_BRIGHTNESS",
            message="La imagen está sobreexpuesta. Reduce la luz directa.",
            severity="warning"
        ))
        score -= 0.2

    laplacian = cv2.Laplacian(gray, cv2.CV_64F).var()
    if laplacian < 50:
        issues.append(QualityIssue(
            code="BLURRY",
            message="La imagen está borrosa. Mantente quieto.",
            severity="error"
        ))
        score -= 0.3

    h, w = image.shape[:2]
    if w < 320 or h < 240:
        issues.append(QualityIssue(
            code="LOW_RESOLUTION",
            message="Resolución insuficiente.",
            severity="error"
        ))
        score -= 0.3

    return max(0.0, round(score, 2)), issues


@router.post("/analyze", response_model=AnalyzeFrameResponse)
async def analyze_frame(request: AnalyzeFrameRequest):
    try:
        image = decode_image(request.image_data)
    except Exception:
        raise HTTPException(status_code=400, detail="No se pudo decodificar la imagen")

    score, issues = analyze_image_quality(image)
    pose_result = detect_pose(image)

    if not pose_result["detected"]:
        issues.append(QualityIssue(
            code="NO_POSE",
            message="No se detectó una persona. Asegúrate de estar completamente visible.",
            severity="error"
        ))
        score -= 0.4

    if pose_result["coverage_issues"]:
        missing = ", ".join(pose_result["coverage_issues"])
        issues.append(QualityIssue(
            code="INCOMPLETE_BODY",
            message=f"Cuerpo incompleto. No se ve: {missing}. Aléjate de la cámara.",
            severity="error"
        ))
        score -= 0.3

    stability_score, stable = compute_stability(pose_result.get("landmarks", []))

    if pose_result["detected"] and not stable:
        issues.append(QualityIssue(
            code="UNSTABLE",
            message="Demasiado movimiento. Mantente quieto unos segundos.",
            severity="warning"
        ))
        score -= 0.2

    score = max(0.0, round(score, 2))
    accepted = score >= 0.6 and not any(i.severity == "error" for i in issues)

    return AnalyzeFrameResponse(
        score=score,
        accepted=accepted,
        issues=issues,
        orientation=pose_result.get("orientation", "unknown"),
        pose_detected=pose_result["detected"],
        landmarks=pose_result.get("landmarks", []),
        landmark_count=pose_result.get("landmark_count", 0),
        stability_score=stability_score,
    )