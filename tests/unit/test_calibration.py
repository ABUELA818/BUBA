import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../apps/api"))

from services.calibration import calibrate, estimate_pixel_height, compute_scale_factor


def make_landmarks(height_ratio=0.8):
    landmarks = [{"x": 0.5, "y": 0.0, "z": 0.0} for _ in range(33)]
    landmarks[0]["y"] = 0.1
    landmarks[27]["y"] = 0.1 + height_ratio
    landmarks[28]["y"] = 0.1 + height_ratio
    return landmarks


def test_estimate_pixel_height():
    landmarks = make_landmarks(height_ratio=0.8)
    height = estimate_pixel_height(landmarks)
    assert height is not None
    assert abs(height - 0.8) < 0.01


def test_scale_factor_170cm():
    landmarks = make_landmarks(height_ratio=0.8)
    scale = compute_scale_factor(landmarks, 170.0)
    assert scale is not None
    assert abs(scale - 170.0 / 0.8) < 1.0


def test_calibrate_success():
    landmarks = make_landmarks(height_ratio=0.8)
    result = calibrate(landmarks, 170.0)
    assert result["success"] is True
    assert result["scale_factor"] is not None
    assert result["scale_factor"] > 0


def test_calibrate_returns_segments():
    landmarks = make_landmarks(height_ratio=0.8)
    result = calibrate(landmarks, 170.0)
    assert "segments" in result
    assert isinstance(result["segments"], dict)


def test_calibrate_invalid_landmarks():
    landmarks = [{"x": 0.5, "y": 0.5, "z": 0.0} for _ in range(5)]
    result = calibrate(landmarks, 170.0)
    assert result["success"] is False