import numpy as np
import pickle
import os

MODEL_PATH_NPZ = os.path.join(
    os.path.dirname(__file__),
    "../../../assets/body_models/SMPLX_NEUTRAL.npz"
)

MODEL_PATH_PKL = os.path.join(
    os.path.dirname(__file__),
    "../../../assets/body_models/SMPLX_NEUTRAL.pkl"
)


def is_model_available() -> bool:
    return os.path.exists(MODEL_PATH_NPZ)


def load_model() -> dict | None:
    if not is_model_available():
        return None

    data = np.load(MODEL_PATH_NPZ, allow_pickle=True)

    model = {
        "v_template": data["v_template"],
        "shapedirs": data["shapedirs"],
        "posedirs": data["posedirs"],
        "J_regressor": data["J_regressor"],
        "kintree_table": data["kintree_table"],
        "faces": data["f"],
        "num_betas": data["shapedirs"].shape[-1],
    }

    if os.path.exists(MODEL_PATH_PKL):
        try:
            with open(MODEL_PATH_PKL, 'rb') as f:
                pkl_data = pickle.load(f, encoding='latin1')
            model["vt"] = np.array(pkl_data["vt"], dtype=np.float32)
            model["ft"] = np.array(pkl_data["ft"], dtype=np.int32)
        except Exception as e:
            print(f"No se pudieron cargar UVs del PKL: {e}")

    return model