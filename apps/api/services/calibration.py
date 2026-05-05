import numpy as np

REFERENCE_LANDMARKS = {
    "head_top": 0,
    "left_shoulder": 11,
    "right_shoulder": 12,
    "left_hip": 23,
    "right_hip": 24,
    "left_knee": 25,
    "right_knee": 26,
    "left_ankle": 27,
    "right_ankle": 28,
}


def estimate_pixel_height(landmarks: list) -> float | None:
    required = [0, 27, 28]
    for idx in required:
        if idx >= len(landmarks):
            return None

    head_y = landmarks[0]["y"]
    left_ankle_y = landmarks[27]["y"]
    right_ankle_y = landmarks[28]["y"]
    ankle_y = (left_ankle_y + right_ankle_y) / 2

    pixel_height = abs(ankle_y - head_y)
    return pixel_height if pixel_height > 0.1 else None


def compute_scale_factor(landmarks: list, real_height_cm: float) -> float | None:
    pixel_height = estimate_pixel_height(landmarks)
    if pixel_height is None:
        return None
    return real_height_cm / pixel_height


def compute_segment_lengths(landmarks: list, scale: float) -> dict:
    def dist(a, b):
        return float(np.linalg.norm([
            (landmarks[a]["x"] - landmarks[b]["x"]) * scale,
            (landmarks[a]["y"] - landmarks[b]["y"]) * scale,
        ]))

    segments = {}

    if all(i < len(landmarks) for i in [11, 12]):
        segments["shoulder_width"] = round(dist(11, 12), 1)

    if all(i < len(landmarks) for i in [23, 24]):
        segments["hip_width"] = round(dist(23, 24), 1)

    if all(i < len(landmarks) for i in [11, 23]):
        segments["torso_length"] = round(dist(11, 23), 1)

    if all(i < len(landmarks) for i in [23, 25, 27]):
        thigh = dist(23, 25)
        shin = dist(25, 27)
        segments["leg_length"] = round(thigh + shin, 1)

    return segments


def calibrate(landmarks: list, real_height_cm: float) -> dict:
    scale = compute_scale_factor(landmarks, real_height_cm)

    if scale is None:
        return {
            "success": False,
            "scale_factor": None,
            "segments": {},
            "message": "No se pudo calcular la escala. Asegúrate de que la cabeza y los tobillos sean visibles.",
        }

    segments = compute_segment_lengths(landmarks, scale)

    return {
        "success": True,
        "scale_factor": round(scale, 4),
        "segments": segments,
        "message": "Calibración exitosa.",
    }