import pickle
import numpy as np
import cv2
import base64
import os

PKL_PATH = os.path.join(
    os.path.dirname(__file__),
    "../../../assets/body_models/SMPLX_NEUTRAL.pkl"
)

FACE_UV_BOUNDS = {
    "u_min": 0.05, "u_max": 0.45,
    "v_min": 0.60, "v_max": 1.00,
}

TEXTURE_SIZE = 1024

_uv_data = None


def load_uv_data() -> dict:
    global _uv_data
    if _uv_data is not None:
        return _uv_data

    with open(PKL_PATH, 'rb') as f:
        data = pickle.load(f, encoding='latin1')

    vt = np.array(data['vt'], dtype=np.float32)
    ft = np.array(data['ft'], dtype=np.int32)
    f = np.array(data['f'], dtype=np.int32)

    uv_centers = vt[ft].mean(axis=1)
    b = FACE_UV_BOUNDS
    face_mask = (
        (uv_centers[:, 0] > b["u_min"]) & (uv_centers[:, 0] < b["u_max"]) &
        (uv_centers[:, 1] > b["v_min"]) & (uv_centers[:, 1] < b["v_max"])
    )

    _uv_data = {
        "vt": vt,
        "ft": ft,
        "f": f,
        "face_tri_indices": np.where(face_mask)[0],
    }
    return _uv_data


def bake_face_texture(
    frame: np.ndarray,
    face_landmarks: list,
    atlas_size: int = TEXTURE_SIZE
) -> dict:
    uv_data = load_uv_data()
    vt = uv_data["vt"]
    ft = uv_data["ft"]
    face_tri_indices = uv_data["face_tri_indices"]

    atlas = np.zeros((atlas_size, atlas_size, 3), dtype=np.uint8)
    atlas[:] = [180, 150, 120]

    h, w = frame.shape[:2]

    if not face_landmarks or len(face_landmarks) < 400:
        return {"success": False, "atlas": None, "message": "Landmarks insuficientes"}

    lm_pts = np.array([[lm["x"] * w, lm["y"] * h] for lm in face_landmarks], dtype=np.float32)

    SMPLX_TO_MP = {
        0: 10, 1: 109, 2: 338, 3: 297, 4: 332,
        5: 284, 6: 251, 7: 389, 8: 356, 9: 454,
        10: 323, 11: 361, 12: 288, 13: 397, 14: 365,
        15: 379, 16: 378, 17: 400, 18: 377, 19: 152,
        20: 148, 21: 176, 22: 149, 23: 150, 24: 136,
        25: 172, 26: 58, 27: 132, 28: 93, 29: 234,
        30: 127, 31: 162, 32: 21, 33: 54, 34: 103,
    }

    face_verts_3d = uv_data["f"][ft[face_tri_indices]].reshape(-1)
    unique_verts = np.unique(face_verts_3d)

    vert_to_img = {}
    for v_idx in unique_verts:
        if v_idx in SMPLX_TO_MP:
            mp_idx = SMPLX_TO_MP[v_idx]
            if mp_idx < len(lm_pts):
                vert_to_img[v_idx] = lm_pts[mp_idx]

    for tri_idx in face_tri_indices:
        uv_tri = vt[ft[tri_idx]]

        px = (uv_tri[:, 0] * atlas_size).astype(np.int32)
        py = ((1.0 - uv_tri[:, 1]) * atlas_size).astype(np.int32)
        uv_pixels = np.stack([px, py], axis=1)

        geo_verts = uv_data["f"][tri_idx] if tri_idx < len(uv_data["f"]) else None

        src_pts = []
        has_mapping = False

        if geo_verts is not None:
            for gv in geo_verts:
                if gv in vert_to_img:
                    src_pts.append(vert_to_img[gv])
                    has_mapping = True
                else:
                    uv = vt[ft[tri_idx][list(geo_verts).index(gv)]]
                    img_x = int(uv[0] * w * 2)
                    img_y = int((1.0 - uv[1]) * h * 1.5)
                    src_pts.append([
                        np.clip(img_x, 0, w - 1),
                        np.clip(img_y, 0, h - 1)
                    ])

        if not src_pts or len(src_pts) < 3:
            center_uv = uv_tri.mean(axis=0)
            img_x = int(center_uv[0] * w * 1.5)
            img_y = int(center_uv[1] * h * 1.2)
            img_x = np.clip(img_x, 0, w - 1)
            img_y = np.clip(img_y, 0, h - 1)
            color = frame[img_y, img_x]
            cv2.fillPoly(atlas, [uv_pixels], color.tolist())
            continue

        src_pts = np.array(src_pts[:3], dtype=np.float32)
        dst_pts = uv_pixels.astype(np.float32)

        try:
            M = cv2.getAffineTransform(src_pts, dst_pts)
            warped = cv2.warpAffine(frame, M, (atlas_size, atlas_size))
            mask = np.zeros((atlas_size, atlas_size), dtype=np.uint8)
            cv2.fillPoly(mask, [uv_pixels], 255)
            atlas[mask > 0] = warped[mask > 0]
        except Exception:
            center_uv = uv_tri.mean(axis=0)
            img_x = np.clip(int(center_uv[0] * w), 0, w - 1)
            img_y = np.clip(int(center_uv[1] * h), 0, h - 1)
            color = frame[img_y, img_x]
            cv2.fillPoly(atlas, [uv_pixels], color.tolist())

    atlas_rgb = cv2.cvtColor(atlas, cv2.COLOR_BGR2RGB)
    atlas_smooth = cv2.GaussianBlur(atlas_rgb, (3, 3), 0)

    _, buffer = cv2.imencode(".jpg", atlas_smooth, [cv2.IMWRITE_JPEG_QUALITY, 92])
    atlas_b64 = base64.b64encode(buffer).decode("utf-8")

    return {
        "success": True,
        "atlas": f"data:image/jpeg;base64,{atlas_b64}",
        "face_triangles": len(face_tri_indices),
        "message": "Atlas UV generado correctamente",
    }