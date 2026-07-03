from contextlib import asynccontextmanager
from pathlib import Path
from uuid import uuid4

from fastapi import Depends, FastAPI, File, Form, HTTPException, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, Response

from .audio import ffmpeg_available, inspect_audio, write_demo_wave
from .config import Settings, get_settings
from .engines import AceStepEngine, DemoEngine
from .jobs import JobRunner
from .policy import enforce_prompt_policy, require_rights
from .repository import Repository
from .schemas import GenerateRequest, HealthOut, JobOut, TrackOut, TrackPatch, TransformRequest


def build_services(settings: Settings):
    repository = Repository(settings.database_path)
    engine = (
        AceStepEngine(settings.ace_step_url, settings.ace_step_api_key)
        if settings.engine == "ace_step"
        else DemoEngine()
    )
    runner = JobRunner(repository, engine, settings.storage_dir.resolve(), settings.job_delay_seconds)
    return repository, engine, runner


def seed_demo_library(repository: Repository, storage: Path) -> None:
    if repository.list_tracks():
        return
    storage.mkdir(parents=True, exist_ok=True)
    seeds = [
        ("demo-glass-horizon", "Glass Horizon", "A midnight drive through rain, luminous synths and a weightless chorus", ["Electronic", "Melancholic"], 118, "F minor", "ai_generated", None, 1),
        ("demo-neon-tides", "Neon Tides", "Prismatic future bass with an intimate vocal and tidal drums", ["Future bass", "Dreamy"], 122, "A minor", "ai_generated", None, 1),
        ("demo-echoes-remix", "Echoes in Motion", "A spacious cinematic reinterpretation with glass percussion", ["Cinematic", "Remix"], 110, "D minor", "remix", "demo-glass-horizon", 2),
    ]
    for index, (track_id, title, prompt, tags, bpm, key, provenance, parent, version) in enumerate(seeds):
        audio_path = storage / f"{track_id}.wav"
        write_demo_wave(audio_path, 24 + index * 2, index * 17)
        repository.create_track(
            {"id": track_id, "title": title, "prompt": prompt, "lyrics": None, "tags": tags,
             "duration": 204 - index * 12, "bpm": bpm, "musical_key": key,
             "provenance": provenance, "source_type": "generated", "parent_track_id": parent,
             "favorite": index == 0, "audio_path": str(audio_path), "mime_type": "audio/wav",
             "version": version}
        )


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    repository, engine, runner = build_services(settings)
    seed_demo_library(repository, settings.storage_dir.resolve())
    app.state.settings = settings
    app.state.repository = repository
    app.state.engine = engine
    app.state.runner = runner
    yield


app = FastAPI(
    title="Auralis API", version="0.1.0", description="Original AI music studio control plane", lifespan=lifespan
)
settings = get_settings()
app.add_middleware(
    CORSMiddleware, allow_origins=settings.allowed_origins, allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)


def repository() -> Repository:
    return app.state.repository


def runner() -> JobRunner:
    return app.state.runner


@app.get("/api/health", response_model=HealthOut)
async def health():
    return HealthOut(
        status="ok", engine=app.state.engine.name,
        engine_ready=await app.state.engine.ready(), ffmpeg_available=ffmpeg_available(),
    )


@app.post("/api/generate", response_model=JobOut, status_code=202)
async def generate(payload: GenerateRequest, service: JobRunner = Depends(runner)):
    enforce_prompt_policy(payload.prompt, payload.artist_acknowledgement)
    return service.submit("generate", payload.model_dump())


@app.post("/api/upload", response_model=TrackOut, status_code=201)
async def upload(
    file: UploadFile = File(...), rights_confirmed: bool = Form(...),
    title: str | None = Form(default=None), repo: Repository = Depends(repository),
):
    require_rights(rights_confirmed)
    config: Settings = app.state.settings
    content_type = file.content_type or "application/octet-stream"
    allowed = {"audio/wav", "audio/x-wav", "audio/mpeg", "audio/mp4", "audio/flac", "audio/ogg"}
    if content_type not in allowed:
        raise HTTPException(status_code=415, detail="Upload WAV, MP3, M4A, FLAC, or OGG audio.")
    suffix = Path(file.filename or "upload.wav").suffix.lower() or ".wav"
    track_id = str(uuid4())
    destination = config.storage_dir.resolve() / f"{track_id}{suffix}"
    destination.parent.mkdir(parents=True, exist_ok=True)
    size = 0
    with destination.open("wb") as output:
        while chunk := await file.read(1024 * 1024):
            size += len(chunk)
            if size > config.max_upload_mb * 1024 * 1024:
                destination.unlink(missing_ok=True)
                raise HTTPException(status_code=413, detail="Audio file exceeds the upload limit.")
            output.write(chunk)
    duration, bpm, musical_key = inspect_audio(destination)
    return repo.create_track(
        {"id": track_id, "title": title or Path(file.filename or "Uploaded audio").stem,
         "prompt": "", "lyrics": None, "tags": ["Uploaded"], "duration": duration,
         "bpm": bpm, "musical_key": musical_key, "provenance": "uploaded",
         "source_type": "uploaded", "parent_track_id": None, "favorite": False,
         "audio_path": str(destination), "mime_type": content_type, "version": 1}
    )


async def submit_transform(kind: str, payload: TransformRequest, repo: Repository, service: JobRunner):
    require_rights(payload.rights_confirmed)
    parent = repo.get_track(payload.track_id)
    if not parent:
        raise HTTPException(status_code=404, detail="Track not found")
    enforce_prompt_policy(payload.prompt)
    return service.submit(kind, payload.model_dump(), parent)


@app.post("/api/cover", response_model=JobOut, status_code=202)
async def cover(payload: TransformRequest, repo: Repository = Depends(repository), service: JobRunner = Depends(runner)):
    return await submit_transform("cover", payload, repo, service)


@app.post("/api/repaint", response_model=JobOut, status_code=202)
async def repaint(payload: TransformRequest, repo: Repository = Depends(repository), service: JobRunner = Depends(runner)):
    return await submit_transform("repaint", payload, repo, service)


@app.post("/api/stems", response_model=JobOut, status_code=202)
async def stems(payload: TransformRequest, repo: Repository = Depends(repository), service: JobRunner = Depends(runner)):
    return await submit_transform("stems", payload, repo, service)


@app.post("/api/vocal-to-bgm", response_model=JobOut, status_code=202)
async def vocal_to_bgm(payload: TransformRequest, repo: Repository = Depends(repository), service: JobRunner = Depends(runner)):
    return await submit_transform("vocal-to-bgm", payload, repo, service)


@app.post("/api/remix", response_model=JobOut, status_code=202)
async def remix(payload: TransformRequest, repo: Repository = Depends(repository), service: JobRunner = Depends(runner)):
    return await submit_transform("style-remix", payload, repo, service)


@app.get("/api/jobs/{job_id}", response_model=JobOut)
def get_job(job_id: str, repo: Repository = Depends(repository)):
    job = repo.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@app.get("/api/tracks", response_model=list[TrackOut])
def list_tracks(
    q: str = Query(default="", max_length=120), provenance: str | None = None,
    repo: Repository = Depends(repository),
):
    return repo.list_tracks(q, provenance)


@app.get("/api/tracks/{track_id}", response_model=TrackOut)
def get_track(track_id: str, repo: Repository = Depends(repository)):
    track = repo.get_track(track_id)
    if not track:
        raise HTTPException(status_code=404, detail="Track not found")
    return track


@app.patch("/api/tracks/{track_id}", response_model=TrackOut)
def patch_track(track_id: str, payload: TrackPatch, repo: Repository = Depends(repository)):
    track = repo.update_track(track_id, payload.model_dump(exclude_unset=True))
    if not track:
        raise HTTPException(status_code=404, detail="Track not found")
    return track


@app.delete("/api/tracks/{track_id}", status_code=204)
def delete_track(track_id: str, repo: Repository = Depends(repository)):
    audio_path = repo.delete_track(track_id)
    if audio_path is None:
        raise HTTPException(status_code=404, detail="Track not found")
    if audio_path:
        Path(audio_path).unlink(missing_ok=True)
    return Response(status_code=204)


@app.get("/api/audio/{track_id}")
def audio(track_id: str, download: bool = False, repo: Repository = Depends(repository)):
    result = repo.get_audio(track_id)
    if not result or not Path(result[0]).exists():
        raise HTTPException(status_code=404, detail="Audio not found")
    return FileResponse(
        result[0], media_type=result[1], filename=Path(result[0]).name if download else None,
        content_disposition_type="attachment" if download else "inline",
    )
