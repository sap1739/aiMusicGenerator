from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, model_validator

Provenance = Literal[
    "ai_generated", "uploaded", "remix", "cover", "repaint", "stems", "vocal_to_bgm"
]


class GenerateRequest(BaseModel):
    prompt: str = Field(min_length=3, max_length=1200)
    title: str = Field(default="Untitled signal", min_length=1, max_length=120)
    lyrics: str | None = Field(default=None, max_length=12_000)
    genre: list[str] = Field(default_factory=list, max_length=8)
    mood: list[str] = Field(default_factory=list, max_length=8)
    instruments: list[str] = Field(default_factory=list, max_length=12)
    duration: int = Field(default=180, ge=10, le=600)
    bpm: int | None = Field(default=None, ge=40, le=240)
    musical_key: str | None = Field(default=None, max_length=24)
    instrumental: bool = False
    artist_acknowledgement: bool = False


class TransformRequest(BaseModel):
    track_id: str
    title: str | None = Field(default=None, max_length=120)
    prompt: str = Field(default="", max_length=1200)
    rights_confirmed: bool
    voice_consent_confirmed: bool = False
    start_seconds: float | None = Field(default=None, ge=0)
    end_seconds: float | None = Field(default=None, ge=0)

    @model_validator(mode="after")
    def validate_range(self):
        if self.end_seconds is not None and self.start_seconds is not None:
            if self.end_seconds <= self.start_seconds:
                raise ValueError("end_seconds must be greater than start_seconds")
        return self


class TrackPatch(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=120)
    tags: list[str] | None = Field(default=None, max_length=20)
    favorite: bool | None = None


class TrackOut(BaseModel):
    id: str
    title: str
    prompt: str
    lyrics: str | None
    tags: list[str]
    duration: float
    bpm: int | None
    musical_key: str | None
    created_at: datetime
    provenance: Provenance
    source_type: str
    parent_track_id: str | None
    favorite: bool
    has_audio: bool
    version: int
    versions: list["TrackOut"] = Field(default_factory=list)


class JobOut(BaseModel):
    id: str
    kind: str
    status: Literal["queued", "processing", "completed", "failed"]
    progress: int
    message: str
    track_id: str | None
    error: str | None
    created_at: datetime
    updated_at: datetime


class HealthOut(BaseModel):
    status: str
    engine: str
    engine_ready: bool
    ffmpeg_available: bool
