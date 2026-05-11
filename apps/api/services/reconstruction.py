import numpy as np
import torch
import torch.nn as nn
from services.smplx_loader import load_model, is_model_available

MEDIAPIPE_TO_SMPLX = {
    0:  "nose",
    11: "left_shoulder",
    12: "right_shoulder",
    13: "left_elbow",
    14: "right_elbow",
    15: "left_wrist",
    16: "right_wrist",
    23: "left_hip",
    24: "right_hip",
    25: "left_knee",
    26: "right_knee",
    27: "left_ankle",
    28: "right_ankle",
}

SMPLX_JOINT_NAMES = [
    "pelvis", "left_hip", "right_hip", "spine1", "left_knee", "right_knee",
    "spine2", "left_ankle", "right_ankle", "spine3", "left_foot", "right_foot",
    "neck", "left_collar", "right_collar", "head", "left_shoulder", "right_shoulder",
    "left_elbow", "right_elbow", "left_wrist", "right_wrist",
]

MEDIAPIPE_TO_SMPLX_IDX = {
    11: 16,
    12: 17,
    23: 1,
    24: 2,
    25: 4,
    26: 5,
    27: 7,
    28: 8,
}


def landmarks_to_tensor(landmarks: list) -> torch.Tensor:
    pts = [[lm["x"], lm["y"], lm["z"]] for lm in landmarks]
    return torch.tensor(pts, dtype=torch.float32)


def estimate_shape(landmarks: list, height_cm: float, model: dict) -> dict:
    if not is_model_available():
        return {"success": False, "message": "Modelo SMPL-X no disponible"}

    lm_tensor = landmarks_to_tensor(landmarks)

    v_template = torch.tensor(model["v_template"], dtype=torch.float32)
    shapedirs = torch.tensor(model["shapedirs"], dtype=torch.float32)
    J_regressor = torch.tensor(model["J_regressor"], dtype=torch.float32)

    betas = nn.Parameter(torch.zeros(10, dtype=torch.float32))
    optimizer = torch.optim.Adam([betas], lr=0.01)

    mp_indices = list(MEDIAPIPE_TO_SMPLX_IDX.keys())
    smplx_indices = [MEDIAPIPE_TO_SMPLX_IDX[i] for i in mp_indices]

    obs_2d = lm_tensor[mp_indices, :2]

    for _ in range(200):
        optimizer.zero_grad()

        shape_offsets = torch.einsum("vcp,p->vc", shapedirs[:, :, :10], betas)
        v_shaped = v_template + shape_offsets

        joints = torch.matmul(J_regressor, v_shaped)

        pred_joints = joints[smplx_indices, :2]

        pred_min = pred_joints.min(dim=0).values
        pred_max = pred_joints.max(dim=0).values
        obs_min = obs_2d.min(dim=0).values
        obs_max = obs_2d.max(dim=0).values

        pred_norm = (pred_joints - pred_min) / (pred_max - pred_min + 1e-6)
        obs_norm = (obs_2d - obs_min) / (obs_max - obs_min + 1e-6)

        loss = nn.functional.mse_loss(pred_norm, obs_norm)
        loss += 0.01 * (betas ** 2).sum()

        loss.backward()
        optimizer.step()

    with torch.no_grad():
        shape_offsets = torch.einsum("vcp,p->vc", shapedirs[:, :, :10], betas)
        v_shaped = v_template + shape_offsets
        joints = torch.matmul(J_regressor, v_shaped)

        model_height = float((joints[:, 1].max() - joints[:, 1].min()).abs())
        scale = (height_cm / 100.0) / (model_height + 1e-6)

        v_final = v_shaped * scale
        joints_final = joints * scale

    result = {
        "success": True,
        "betas": betas.detach().numpy().tolist(),
        "scale": float(scale),
        "joint_positions": joints_final.detach().numpy().tolist(),
        "vertices": v_final.detach().numpy().tolist(),
        "faces": model["faces"].tolist(),
        "message": "Reconstrucción completada",
    }

    if "vt" in model and "ft" in model:
        result["vt"] = model["vt"].tolist()
        result["ft"] = model["ft"].tolist()

    return result