import numpy as np
import cv2
import base64


def extract_face_texture(image: np.ndarray, face_landmarks: list) -> dict:
    if not face_landmarks or len(face_landmarks) < 400:
        return {"success": False, "message": "Landmarks insuficientes"}

    h, w = image.shape[:2]

    points = np.array([[int(lm["x"] * w), int(lm["y"] * h)] for lm in face_landmarks])

    x, y, fw, fh = cv2.boundingRect(points)
    padding = int(max(fw, fh) * 0.2)
    x1 = max(0, x - padding)
    y1 = max(0, y - padding)
    x2 = min(w, x + fw + padding)
    y2 = min(h, y + fh + padding)

    face_crop = image[y1:y2, x1:x2]

    face_resized = cv2.resize(face_crop, (512, 512))

    face_rgb = cv2.cvtColor(face_resized, cv2.COLOR_BGR2RGB)

    _, buffer = cv2.imencode(".jpg", face_rgb, [cv2.IMWRITE_JPEG_QUALITY, 90])
    texture_b64 = base64.b64encode(buffer).decode("utf-8")

    return {
        "success": True,
        "texture": f"data:image/jpeg;base64,{texture_b64}",
        "face_bounds": {"x": x1, "y": y1, "w": x2 - x1, "h": y2 - y1},
    }


def extract_hair_color(image: np.ndarray, face_landmarks: list) -> dict:
    if not face_landmarks or len(face_landmarks) < 10:
        return {"success": False, "color_hex": "#1a0a00"}

    h, w = image.shape[:2]

    forehead_idx = 10
    top_idx = 151

    if top_idx >= len(face_landmarks):
        return {"success": False, "color_hex": "#1a0a00"}

    forehead_y = int(face_landmarks[forehead_idx]["y"] * h)
    forehead_x = int(face_landmarks[forehead_idx]["x"] * w)

    sample_y1 = max(0, forehead_y - 80)
    sample_y2 = max(0, forehead_y - 10)
    sample_x1 = max(0, forehead_x - 40)
    sample_x2 = min(w, forehead_x + 40)

    if sample_y2 <= sample_y1 or sample_x2 <= sample_x1:
        return {"success": False, "color_hex": "#1a0a00"}

    hair_region = image[sample_y1:sample_y2, sample_x1:sample_x2]

    if hair_region.size == 0:
        return {"success": False, "color_hex": "#1a0a00"}

    hair_rgb = cv2.cvtColor(hair_region, cv2.COLOR_BGR2RGB)

    pixels = hair_rgb.reshape(-1, 3).astype(np.float32)

    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
    k = min(3, len(pixels))
    _, labels, centers = cv2.kmeans(pixels, k, None, criteria, 3, cv2.KMEANS_RANDOM_CENTERS)

    counts = np.bincount(labels.flatten())
    dominant = centers[np.argmax(counts)].astype(int)

    color_hex = "#{:02x}{:02x}{:02x}".format(dominant[0], dominant[1], dominant[2])

    return {
        "success": True,
        "color_hex": color_hex,
        "rgb": dominant.tolist(),
    }


def estimate_hair_style(image: np.ndarray, face_landmarks: list) -> str:
    if not face_landmarks or len(face_landmarks) < 10:
        return "short"

    h, w = image.shape[:2]

    forehead_y = int(face_landmarks[10]["y"] * h)
    chin_y = int(face_landmarks[152]["y"] * h) if len(face_landmarks) > 152 else forehead_y + 100
    face_height = chin_y - forehead_y

    top_of_head_y = max(0, forehead_y - int(face_height * 0.3))
    hair_region_height = forehead_y - top_of_head_y

    center_x = int(face_landmarks[10]["x"] * w)
    x1 = max(0, center_x - 60)
    x2 = min(w, center_x + 60)

    if top_of_head_y >= forehead_y or x2 <= x1:
        return "short"

    hair_region = image[top_of_head_y:forehead_y, x1:x2]

    if hair_region.size == 0:
        return "short"

    gray = cv2.cvtColor(hair_region, cv2.COLOR_BGR2GRAY)
    hair_pixels = np.sum(gray < 200)
    total_pixels = gray.size

    hair_density = hair_pixels / total_pixels if total_pixels > 0 else 0

    chin_x = int(face_landmarks[152]["x"] * w) if len(face_landmarks) > 152 else center_x
    shoulder_y = min(h - 1, chin_y + int(face_height * 1.0))

    x1s = max(0, chin_x - 80)
    x2s = min(w, chin_x + 80)

    if shoulder_y > chin_y and x2s > x1s:
        shoulder_region = image[chin_y:shoulder_y, x1s:x2s]
        if shoulder_region.size > 0:
            gray_s = cv2.cvtColor(shoulder_region, cv2.COLOR_BGR2GRAY)
            shoulder_hair = np.sum(gray_s < 180) / gray_s.size

            if shoulder_hair > 0.3:
                return "long"

    if hair_density > 0.6:
        return "curly"
    elif hair_region_height < 20:
        return "short"
    else:
        return "medium"