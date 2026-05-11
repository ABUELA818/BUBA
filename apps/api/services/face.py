import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import numpy as np
import cv2
import os

MODEL_PATH = os.path.join(
    os.path.dirname(__file__),
    "../../../assets/body_models/face_landmarker.task"
)

_detector = None


def get_detector():
    global _detector
    if _detector is None:
        base_options = python.BaseOptions(model_asset_path=MODEL_PATH)
        options = vision.FaceLandmarkerOptions(
            base_options=base_options,
            output_face_blendshapes=True,
            output_facial_transformation_matrixes=True,
            num_faces=1,
        )
        _detector = vision.FaceLandmarker.create_from_options(options)
    return _detector


def detect_face(image: np.ndarray) -> dict:
    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)

    detector = get_detector()
    result = detector.detect(mp_image)

    if not result.face_landmarks:
        return {"detected": False, "landmarks": [], "blendshapes": {}}

    landmarks = []
    for lm in result.face_landmarks[0]:
        landmarks.append({"x": lm.x, "y": lm.y, "z": lm.z})

    blendshapes = {}
    if result.face_blendshapes:
        for bs in result.face_blendshapes[0]:
            blendshapes[bs.category_name] = round(bs.score, 4)

    face_metrics = extract_face_metrics(landmarks)

    return {
        "detected": True,
        "landmarks": landmarks,
        "blendshapes": blendshapes,
        "face_metrics": face_metrics,
        "landmark_count": len(landmarks),
    }


def extract_face_metrics(landmarks: list) -> dict:
    if len(landmarks) < 400:
        return {}

    FACE_INDICES = {
        "left_eye": 33,
        "right_eye": 263,
        "nose_tip": 4,
        "mouth_left": 61,
        "mouth_right": 291,
        "chin": 152,
        "forehead": 10,
        "left_cheek": 234,
        "right_cheek": 454,
    }

    points = {}
    for name, idx in FACE_INDICES.items():
        points[name] = np.array([landmarks[idx]["x"], landmarks[idx]["y"]])

    metrics = {}

    face_width = float(np.linalg.norm(points["left_cheek"] - points["right_cheek"]))
    face_height = float(np.linalg.norm(points["forehead"] - points["chin"]))

    if face_width > 0:
        metrics["face_ratio"] = round(face_height / face_width, 3)

    eye_width = float(np.linalg.norm(points["left_eye"] - points["right_eye"]))
    if face_width > 0:
        metrics["eye_spacing_ratio"] = round(eye_width / face_width, 3)

    mouth_width = float(np.linalg.norm(points["mouth_left"] - points["mouth_right"]))
    if face_width > 0:
        metrics["mouth_width_ratio"] = round(mouth_width / face_width, 3)

    ratio = metrics.get("face_ratio", 1.3)
    if ratio > 1.5:
        metrics["face_shape"] = "oval"
    elif ratio > 1.3:
        metrics["face_shape"] = "oblong"
    elif ratio < 1.1:
        metrics["face_shape"] = "round"
    else:
        metrics["face_shape"] = "square"

    return metrics