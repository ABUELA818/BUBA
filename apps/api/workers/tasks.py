from workers.celery_app import celery_app
from services.reconstruction import estimate_shape
from services.smplx_loader import load_model
from services.metrics import compute_metrics
from services.recommendation import get_recommendations

_model = None


def get_model():
    global _model
    if _model is None:
        _model = load_model()
    return _model


@celery_app.task(bind=True, name="workers.tasks.run_reconstruction")
def run_reconstruction(self, landmarks: list, height_cm: float, session_id: str):
    self.update_state(state="STARTED", meta={"progress": 0, "session_id": session_id})

    model = get_model()
    if model is None:
        return {"success": False, "message": "Modelo no disponible"}

    self.update_state(state="PROGRESS", meta={"progress": 30, "session_id": session_id})

    result = estimate_shape(landmarks, height_cm, model)

    if not result["success"]:
        return result

    self.update_state(state="PROGRESS", meta={"progress": 70, "session_id": session_id})

    metrics = compute_metrics(result["joint_positions"], result["scale"])

    self.update_state(state="PROGRESS", meta={"progress": 90, "session_id": session_id})

    recommendation = get_recommendations(metrics["body_type"], metrics["measurements"])

    return {
        "success": True,
        "session_id": session_id,
        "reconstruction": result,
        "metrics": metrics,
        "recommendation": recommendation,
    }