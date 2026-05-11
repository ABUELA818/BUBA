from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import capture, sessions, calibration, reconstruction, metrics, recommendation, face, texture
from database import create_tables
import os

app = FastAPI(
    title="BUBA API",
    description="Backend para captura y reconstrucción corporal 3D",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(capture.router)
app.include_router(sessions.router)
app.include_router(calibration.router)
app.include_router(reconstruction.router)
app.include_router(metrics.router)
app.include_router(recommendation.router)
app.include_router(face.router)
app.include_router(texture.router)

@app.on_event("startup")
def on_startup():
    db_url = os.getenv("DATABASE_URL", "")
    if db_url:
        try:
            create_tables()
            print("Tablas creadas correctamente")
        except Exception as e:
            print(f"DB no disponible en startup: {e}")

@app.get("/health")
def health():
    return {"status": "ok", "version": "0.1.0"}