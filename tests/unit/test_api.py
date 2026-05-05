import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../apps/api"))

import pytest
from fastapi.testclient import TestClient
from main import app
import base64
import numpy as np
import cv2

client = TestClient(app)


def make_frame_base64(brightness=120, size=(640, 480)) -> str:
    image = np.full((size[1], size[0], 3), brightness, dtype=np.uint8)
    _, buffer = cv2.imencode(".jpg", image)
    b64 = base64.b64encode(buffer).decode("utf-8")
    return f"data:image/jpeg;base64,{b64}"


def test_health():
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"


def test_reconstruction_status():
    res = client.get("/reconstruction/status")
    assert res.status_code == 200
    assert "model_available" in res.json()


def test_analyze_frame_bright():
    image_data = make_frame_base64(brightness=120)
    res = client.post("/capture/analyze", json={
        "image_data": image_data,
        "height_cm": 170.0,
    })
    assert res.status_code == 200
    data = res.json()
    assert "score" in data
    assert "accepted" in data
    assert "pose_detected" in data
    assert 0.0 <= data["score"] <= 1.0


def test_analyze_frame_dark():
    image_data = make_frame_base64(brightness=20)
    res = client.post("/capture/analyze", json={
        "image_data": image_data,
        "height_cm": 170.0,
    })
    assert res.status_code == 200
    data = res.json()
    assert data["accepted"] is False
    codes = [i["code"] for i in data["issues"]]
    assert "LOW_BRIGHTNESS" in codes


def test_create_session():
    res = client.post("/sessions", json={"height_cm": 175.0})
    assert res.status_code == 200
    data = res.json()
    assert "session_id" in data
    assert data["height_cm"] == 175.0


def test_calibrate_valid_landmarks():
    landmarks = [{"x": 0.5, "y": float(i) * 0.03, "z": 0.0} for i in range(33)]
    landmarks[0]["y"] = 0.1
    landmarks[27]["y"] = 0.9
    landmarks[28]["y"] = 0.9
    res = client.post("/calibration/compute", json={
        "landmarks": landmarks,
        "height_cm": 170.0,
    })
    assert res.status_code == 200
    data = res.json()
    assert "success" in data
    assert "scale_factor" in data


def test_metrics_compute():
    joints = [[0.0, 0.0, 0.0]] * 22
    joints[16] = [-0.2, 1.4, 0.0]
    joints[17] = [0.2, 1.4, 0.0]
    joints[1] = [-0.15, 0.9, 0.0]
    joints[2] = [0.15, 0.9, 0.0]
    joints[4] = [-0.15, 0.5, 0.0]
    joints[5] = [0.15, 0.5, 0.0]
    joints[7] = [-0.15, 0.0, 0.0]
    joints[8] = [0.15, 0.0, 0.0]
    res = client.post("/metrics/compute", json={
        "joint_positions": joints,
        "scale": 1.0,
    })
    assert res.status_code == 200
    data = res.json()
    assert "body_type" in data
    assert "measurements" in data


def test_recommendation_compute():
    res = client.post("/recommendation/compute", json={
        "body_type": "inverted_triangle",
        "measurements": {"shoulder_width": 48.0, "hip_width": 38.0},
    })
    assert res.status_code == 200
    data = res.json()
    assert data["body_type"] == "inverted_triangle"
    assert "recommendations" in data
    assert "size_estimate" in data