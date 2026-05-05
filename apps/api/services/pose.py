import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import numpy as np
import cv2
import os

MODEL_PATH = os.path.join(
    os.path.dirname(__file__),
    "../../../assets/body_models/pose_landmarker_full.task"
)

_detector = None

def get_detector():
    global _detector
    if _detector is None:
        base_options = python.BaseOptions(model_asset_path=MODEL_PATH)
        options = vision.PoseLandmarkerOptions(
            base_options=base_options,
            output_segmentation_masks=False,
            num_poses=1,
        )
        _detector = vision.PoseLandmarker.create_from_options(options)
    return _detector


def validate_body_coverage(landmarks: list, visibility: list) -> list:
    issues = []

    REQUIRED = {
        11: "hombro izquierdo",
        12: "hombro derecho",
        23: "cadera izquierda",
        24: "cadera derecha",
        25: "rodilla izquierda",
        26: "rodilla derecha",
    }

    THRESHOLD = 0.5

    for idx, name in REQUIRED.items():
        if idx >= len(visibility) or visibility[idx] < THRESHOLD:
            issues.append(f"{name}")

    return issues


def estimate_orientation(landmarks: list) -> str:
    if len(landmarks) < 17:
        return "unknown"

    left_shoulder = landmarks[11]
    right_shoulder = landmarks[12]

    shoulder_diff = abs(left_shoulder["x"] - right_shoulder["x"])

    if shoulder_diff < 0.1:
        return "profile"
    elif shoulder_diff > 0.2:
        return "front"
    else:
        return "unknown"


def detect_pose(image: np.ndarray) -> dict:
    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)

    detector = get_detector()
    result = detector.detect(mp_image)

    if not result.pose_landmarks:
        return {
            "detected": False,
            "landmarks": [],
            "visibility": [],
            "orientation": "unknown",
            "landmark_count": 0,
            "coverage_issues": [],
        }

    landmarks = []
    visibility = []

    for lm in result.pose_landmarks[0]:
        landmarks.append({"x": lm.x, "y": lm.y, "z": lm.z})
        visibility.append(lm.visibility)

    orientation = estimate_orientation(landmarks)
    coverage_issues = validate_body_coverage(landmarks, visibility)

    return {
        "detected": True,
        "landmarks": landmarks,
        "visibility": visibility,
        "orientation": orientation,
        "landmark_count": len(landmarks),
        "coverage_issues": coverage_issues,
    }