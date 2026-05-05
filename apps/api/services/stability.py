import numpy as np
from collections import deque

MAX_HISTORY = 5
MOVEMENT_THRESHOLD = 0.03

_landmark_history: deque = deque(maxlen=MAX_HISTORY)


def compute_stability(landmarks: list) -> tuple[float, bool]:
    if not landmarks:
        return 0.0, False

    current = np.array([[lm["x"], lm["y"]] for lm in landmarks])

    if len(_landmark_history) == 0:
        _landmark_history.append(current)
        return 1.0, True

    prev = _landmark_history[-1]

    if prev.shape != current.shape:
        _landmark_history.clear()
        _landmark_history.append(current)
        return 1.0, True

    movement = float(np.mean(np.linalg.norm(current - prev, axis=1)))

    if movement < MOVEMENT_THRESHOLD:
        score = 1.0
    elif movement < MOVEMENT_THRESHOLD * 2:
        score = 0.7
    elif movement < MOVEMENT_THRESHOLD * 4:
        score = 0.4
    else:
        score = 0.0

    _landmark_history.append(current)

    return round(score, 2), score >= 0.4


def reset_history():
    _landmark_history.clear()