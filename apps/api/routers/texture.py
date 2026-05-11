from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import base64
import numpy as np
import cv2
from services.texture import extract_hair_color, estimate_hair_style
from services.face import detect_face
from services.uv_baker import bake_face_texture

router = APIRouter(prefix="/texture", tags=["texture"])


class TextureRequest(BaseModel):
    image_data: str


class TextureResponse(BaseModel):
    success: bool
    face_texture: str | None = None
    hair_color: str | None = None
    hair_style: str | None = None
    message: str = ""


def decode_image(image_data: str) -> np.ndarray:
    if "," in image_data:
        image_data = image_data.split(",")[1]
    image_bytes = base64.b64decode(image_data)
    image_array = np.frombuffer(image_bytes, dtype=np.uint8)
    return cv2.imdecode(image_array, cv2.IMREAD_COLOR)


@router.post("/extract", response_model=TextureResponse)
def extract_texture(request: TextureRequest):
    try:
        image = decode_image(request.image_data)
    except Exception:
        raise HTTPException(status_code=400, detail="No se pudo decodificar la imagen")

    face_result = detect_face(image)

    if not face_result["detected"]:
        return TextureResponse(
            success=False,
            message="No se detectó cara en la imagen",
        )

    landmarks = face_result["landmarks"]

    bake_result = bake_face_texture(image, landmarks)
    hair_color_result = extract_hair_color(image, landmarks)
    hair_style = estimate_hair_style(image, landmarks)

    return TextureResponse(
        success=bake_result["success"],
        face_texture=bake_result.get("atlas"),
        hair_color=hair_color_result.get("color_hex", "#1a0a00"),
        hair_style=hair_style,
        message=bake_result.get("message", ""),
    )