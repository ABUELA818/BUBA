from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID, uuid4
import json


class Session(SQLModel, table=True):
    __tablename__ = "sessions"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    height_cm: float
    status: str = "active"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Frame(SQLModel, table=True):
    __tablename__ = "frames"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    session_id: UUID = Field(foreign_key="sessions.id")
    quality_score: Optional[float] = None
    orientation: Optional[str] = None
    stability_score: Optional[float] = None
    landmark_count: Optional[int] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Reconstruction(SQLModel, table=True):
    __tablename__ = "reconstructions"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    session_id: UUID = Field(foreign_key="sessions.id")
    betas: Optional[str] = None
    scale: Optional[float] = None
    joint_positions: Optional[str] = None
    body_type: Optional[str] = None
    measurements: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Recommendation(SQLModel, table=True):
    __tablename__ = "recommendations"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    session_id: UUID = Field(foreign_key="sessions.id")
    body_type: Optional[str] = None
    size_top: Optional[str] = None
    size_bottom: Optional[str] = None
    recommendations: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)