import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../apps/api"))

import numpy as np
import cv2
from routers.capture import analyze_image_quality
from pydantic import BaseModel


class QualityIssue(BaseModel):
    code: str
    message: str
    severity: str


def make_image(brightness: int, blur: bool = False, size=(640, 480)) -> np.ndarray:
    image = np.full((size[1], size[0], 3), brightness, dtype=np.uint8)
    if blur:
        image = cv2.GaussianBlur(image, (21, 21), 0)
    return image


def test_bright_image_passes():
    image = make_image(brightness=120)
    noise = np.random.randint(0, 30, image.shape, dtype=np.uint8)
    image = cv2.add(image, noise)
    score, issues = analyze_image_quality(image)
    codes = [i.code for i in issues]
    assert "LOW_BRIGHTNESS" not in codes
    assert "HIGH_BRIGHTNESS" not in codes
    assert score >= 0.7


def test_dark_image_fails():
    image = make_image(brightness=20)
    score, issues = analyze_image_quality(image)
    codes = [i.code for i in issues]
    assert "LOW_BRIGHTNESS" in codes
    assert score < 0.7


def test_bright_overexposed_image_warns():
    image = make_image(brightness=230)
    score, issues = analyze_image_quality(image)
    codes = [i.code for i in issues]
    assert "HIGH_BRIGHTNESS" in codes


def test_blurry_image_fails():
    image = make_image(brightness=120, blur=True)
    score, issues = analyze_image_quality(image)
    codes = [i.code for i in issues]
    assert "BLURRY" in codes


def test_low_resolution_fails():
    image = make_image(brightness=120, size=(100, 80))
    score, issues = analyze_image_quality(image)
    codes = [i.code for i in issues]
    assert "LOW_RESOLUTION" in codes


def test_score_range():
    image = make_image(brightness=120)
    score, _ = analyze_image_quality(image)
    assert 0.0 <= score <= 1.0