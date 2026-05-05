import numpy as np


JOINT_SEGMENTS = {
    "shoulder_width": (16, 17),
    "hip_width": (1, 2),
    "torso_length": (16, 1),
    "left_leg": [(1, 4), (4, 7)],
    "right_leg": [(2, 5), (5, 8)],
}


def compute_distance(j1: np.ndarray, j2: np.ndarray) -> float:
    return float(np.linalg.norm(j1 - j2))


def extract_measurements(joint_positions: list, scale: float) -> dict:
    joints = np.array(joint_positions)

    measurements = {}

    for name, indices in JOINT_SEGMENTS.items():
        if isinstance(indices, list):
            total = 0.0
            valid = True
            for a, b in indices:
                if a >= len(joints) or b >= len(joints):
                    valid = False
                    break
                total += compute_distance(joints[a], joints[b])
            if valid:
                measurements[name] = round(total * 100, 1)
        else:
            a, b = indices
            if a < len(joints) and b < len(joints):
                measurements[name] = round(
                    compute_distance(joints[a], joints[b]) * 100, 1
                )

    if "left_leg" in measurements and "right_leg" in measurements:
        measurements["avg_leg_length"] = round(
            (measurements["left_leg"] + measurements["right_leg"]) / 2, 1
        )

    return measurements


def classify_body_type(measurements: dict) -> str:
    shoulder = measurements.get("shoulder_width")
    hip = measurements.get("hip_width")

    if shoulder is None or hip is None:
        return "unknown"

    ratio = shoulder / hip

    if ratio > 1.15:
        return "inverted_triangle"
    elif ratio < 0.85:
        return "pear"
    elif 0.85 <= ratio <= 1.15:
        torso = measurements.get("torso_length", 0)
        leg = measurements.get("avg_leg_length", 0)
        if torso > 0 and leg > 0 and abs(torso - leg * 0.6) < 5:
            return "hourglass"
        return "rectangle"
    return "unknown"


def compute_metrics(joint_positions: list, scale: float) -> dict:
    measurements = extract_measurements(joint_positions, scale)
    body_type = classify_body_type(measurements)

    return {
        "measurements": measurements,
        "body_type": body_type,
        "confidence": "medium",
    }