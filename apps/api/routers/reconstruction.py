from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.reconstruction import estimate_shape
from services.smplx_loader import load_model, is_model_available
from workers.tasks import run_reconstruction
import uuid

router = APIRouter(prefix="/reconstruction", tags=["reconstruction"])

_model = None


def get_model():
    global _model
    if _model is None and is_model_available():
        _model = load_model()
    return _model


class LandmarkPoint(BaseModel):
    x: float
    y: float
    z: float


class ReconstructRequest(BaseModel):
    landmarks: list[LandmarkPoint]
    height_cm: float
    session_id: str | None = None
    async_mode: bool = False


class ReconstructResponse(BaseModel):
    success: bool
    message: str
    betas: list[float] | None = None
    scale: float | None = None
    joint_positions: list[list[float]] | None = None
    vertices: list[list[float]] | None = None
    faces: list[list[int]] | None = None


class AsyncReconstructResponse(BaseModel):
    task_id: str
    message: str


@router.get("/status")
def model_status():
    return {
        "model_available": is_model_available(),
        "message": "Modelo listo" if is_model_available() else "Modelo SMPL-X no encontrado",
    }


@router.get("/task/{task_id}")
def get_task_status(task_id: str):
    task = run_reconstruction.AsyncResult(task_id)
    if task.state == "PENDING":
        return {"state": "pending", "progress": 0}
    elif task.state == "PROGRESS":
        return {"state": "processing", "progress": task.info.get("progress", 0)}
    elif task.state == "SUCCESS":
        return {"state": "done", "progress": 100, "result": task.result}
    elif task.state == "FAILURE":
        return {"state": "error", "message": str(task.info)}
    return {"state": task.state.lower()}


@router.post("/compute", response_model=ReconstructResponse)
def compute_reconstruction(request: ReconstructRequest):
    model = get_model()

    if model is None:
        raise HTTPException(status_code=503, detail="Modelo SMPL-X no disponible")

    if len(request.landmarks) < 29:
        raise HTTPException(status_code=400, detail="Se necesitan al menos 29 landmarks")

    landmarks = [{"x": lm.x, "y": lm.y, "z": lm.z} for lm in request.landmarks]
    result = estimate_shape(landmarks, request.height_cm, model)

    return ReconstructResponse(**result)


@router.post("/compute/async", response_model=AsyncReconstructResponse)
def compute_reconstruction_async(request: ReconstructRequest):
    if not is_model_available():
        raise HTTPException(status_code=503, detail="Modelo SMPL-X no disponible")

    if len(request.landmarks) < 29:
        raise HTTPException(status_code=400, detail="Se necesitan al menos 29 landmarks")

    landmarks = [{"x": lm.x, "y": lm.y, "z": lm.z} for lm in request.landmarks]
    session_id = request.session_id or str(uuid.uuid4())

    task = run_reconstruction.delay(landmarks, request.height_cm, session_id)

    return AsyncReconstructResponse(
        task_id=task.id,
        message="Reconstrucción iniciada en background",
    )