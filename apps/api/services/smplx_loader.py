import numpy as np
import os

MODEL_PATH = os.path.join(
    os.path.dirname(__file__),
    "../../../assets/body_models/SMPLX_NEUTRAL.npz"
)


def is_model_available() -> bool:
    return os.path.exists(MODEL_PATH)


def load_model() -> dict | None:
    if not is_model_available():
        return None

    data = np.load(MODEL_PATH, allow_pickle=True)

    return {
        "v_template": data["v_template"],
        "shapedirs": data["shapedirs"],
        "posedirs": data["posedirs"],
        "J_regressor": data["J_regressor"],
        "kintree_table": data["kintree_table"],
        "faces": data["f"],
        "num_betas": data["shapedirs"].shape[-1],
    }