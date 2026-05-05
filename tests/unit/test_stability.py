import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../apps/api"))

from services.stability import compute_stability, reset_history


def make_landmarks(offset_x=0.0, offset_y=0.0):
    return [{"x": 0.5 + offset_x, "y": 0.5 + offset_y, "z": 0.0} for _ in range(33)]


def test_first_frame_is_stable():
    reset_history()
    score, stable = compute_stability(make_landmarks())
    assert score == 1.0
    assert stable is True


def test_static_body_is_stable():
    reset_history()
    for _ in range(3):
        score, stable = compute_stability(make_landmarks())
    assert score == 1.0
    assert stable is True


def test_large_movement_is_unstable():
    reset_history()
    compute_stability(make_landmarks(0.0, 0.0))
    score, stable = compute_stability(make_landmarks(0.5, 0.5))
    assert stable is False
    assert score < 0.5


def test_small_movement_is_acceptable():
    reset_history()
    compute_stability(make_landmarks(0.0, 0.0))
    score, stable = compute_stability(make_landmarks(0.01, 0.01))
    assert stable is True


def test_empty_landmarks_returns_zero():
    reset_history()
    score, stable = compute_stability([])
    assert score == 0.0
    assert stable is False