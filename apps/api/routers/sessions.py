from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlmodel import Session, select
from database import get_session
from models import Session as SessionModel, Frame
from uuid import UUID
from datetime import datetime

router = APIRouter(prefix="/sessions", tags=["sessions"])


class CreateSessionRequest(BaseModel):
    height_cm: float


class SessionResponse(BaseModel):
    session_id: str
    height_cm: float
    created_at: str
    frame_count: int
    status: str


class AddFrameRequest(BaseModel):
    session_id: str
    quality_score: float
    orientation: str
    stability_score: float
    landmark_count: int


@router.post("", response_model=SessionResponse)
def create_session(request: CreateSessionRequest, db: Session = Depends(get_session)):
    session = SessionModel(height_cm=request.height_cm)
    db.add(session)
    db.commit()
    db.refresh(session)

    return SessionResponse(
        session_id=str(session.id),
        height_cm=session.height_cm,
        created_at=session.created_at.isoformat(),
        frame_count=0,
        status=session.status,
    )


@router.post("/{session_id}/frames", response_model=SessionResponse)
def add_frame(session_id: str, request: AddFrameRequest, db: Session = Depends(get_session)):
    session = db.get(SessionModel, UUID(session_id))
    if not session:
        raise HTTPException(status_code=404, detail="Sesión no encontrada")

    frame = Frame(
        session_id=UUID(session_id),
        quality_score=request.quality_score,
        orientation=request.orientation,
        stability_score=request.stability_score,
        landmark_count=request.landmark_count,
    )
    db.add(frame)
    session.updated_at = datetime.utcnow()
    db.commit()

    frame_count = db.exec(
        select(Frame).where(Frame.session_id == UUID(session_id))
    ).all()

    return SessionResponse(
        session_id=str(session.id),
        height_cm=session.height_cm,
        created_at=session.created_at.isoformat(),
        frame_count=len(frame_count),
        status=session.status,
    )


@router.get("/{session_id}", response_model=SessionResponse)
def get_session(session_id: str, db: Session = Depends(get_session)):
    session = db.get(SessionModel, UUID(session_id))
    if not session:
        raise HTTPException(status_code=404, detail="Sesión no encontrada")

    frame_count = db.exec(
        select(Frame).where(Frame.session_id == UUID(session_id))
    ).all()

    return SessionResponse(
        session_id=str(session.id),
        height_cm=session.height_cm,
        created_at=session.created_at.isoformat(),
        frame_count=len(frame_count),
        status=session.status,
    )