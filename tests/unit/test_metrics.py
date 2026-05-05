import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../apps/api"))

from services.metrics import compute_metrics, classify_body_type, extract_measurements


def make_joints():
    joints = [[0.0, 0.0, 0.0]] * 22
    joints[16] = [-0.2, 1.4, 0.0]
    joints[17] = [0.2, 1.4, 0.0]
    joints[1] = [-0.15, 0.9, 0.0]
    joints[2] = [0.15, 0.9, 0.0]
    joints[4] = [-0.15, 0.5, 0.0]
    joints[5] = [0.15, 0.5, 0.0]
    joints[7] = [-0.15, 0.0, 0.0]
    joints[8] = [0.15, 0.0, 0.0]
    return joints


def test_extract_measurements():
    joints = make_joints()
    measurements = extract_measurements(joints, scale=1.0)
    assert "shoulder_width" in measurements
    assert "hip_width" in measurements
    assert measurements["shoulder_width"] > 0
    assert measurements["hip_width"] > 0


def test_classify_inverted_triangle():
    measurements = {"shoulder_width": 50.0, "hip_width": 40.0}
    body_type = classify_body_type(measurements)
    assert body_type == "inverted_triangle"


def test_classify_pear():
    measurements = {"shoulder_width": 35.0, "hip_width": 45.0}
    body_type = classify_body_type(measurements)
    assert body_type == "pear"


def test_classify_rectangle():
    measurements = {"shoulder_width": 42.0, "hip_width": 42.0}
    body_type = classify_body_type(measurements)
    assert body_type in ["rectangle", "hourglass"]


def test_compute_metrics_returns_body_type():
    joints = make_joints()
    result = compute_metrics(joints, scale=1.0)
    assert "body_type" in result
    assert "measurements" in result
    assert result["body_type"] != ""


def test_missing_measurements_returns_unknown():
    body_type = classify_body_type({})
    assert body_type == "unknown"