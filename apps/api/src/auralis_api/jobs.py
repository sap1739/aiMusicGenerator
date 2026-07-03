import asyncio
from pathlib import Path
from uuid import uuid4

from .repository import Repository


class JobRunner:
    def __init__(self, repository: Repository, engine, storage: Path, delay: float = 1.0):
        self.repository = repository
        self.engine = engine
        self.storage = storage
        self.delay = delay
        storage.mkdir(parents=True, exist_ok=True)

    def submit(self, kind: str, payload: dict, parent_track: dict | None = None) -> dict:
        job_id = str(uuid4())
        job = self.repository.create_job(
            {"id": job_id, "kind": kind, "status": "queued", "progress": 4,
             "message": "Waiting for an available audio worker", "payload": payload}
        )
        asyncio.create_task(self._run(job_id, kind, payload, parent_track))
        return job

    async def _run(self, job_id: str, kind: str, payload: dict, parent_track: dict | None) -> None:
        try:
            self.repository.update_job(job_id, status="processing", progress=18, message="Planning the arrangement")
            await asyncio.sleep(self.delay)
            self.repository.update_job(job_id, progress=52, message="Rendering audio layers")
            track_id = str(uuid4())
            output_path = self.storage / f"{track_id}.wav"
            if kind == "generate":
                await self.engine.generate(payload, output_path)
                provenance = "ai_generated"
            else:
                source = self.repository.get_audio(payload["track_id"])
                if not source:
                    raise RuntimeError("Source track has no audio")
                await self.engine.transform(kind, payload, Path(source[0]), output_path)
                provenance = {"style-remix": "remix", "vocal-to-bgm": "vocal_to_bgm"}.get(kind, kind)
            self.repository.update_job(job_id, progress=86, message="Finalizing metadata and provenance")
            await asyncio.sleep(self.delay / 2)
            parent_id = parent_track["id"] if parent_track else None
            base_version = parent_track["version"] if parent_track else 0
            track = self.repository.create_track(
                {
                    "id": track_id,
                    "title": payload.get("title") or f"{parent_track['title']} · {kind.title()}",
                    "prompt": payload.get("prompt", ""), "lyrics": payload.get("lyrics"),
                    "tags": [*payload.get("genre", []), *payload.get("mood", [])],
                    "duration": payload.get("duration") or (parent_track or {}).get("duration", 24),
                    "bpm": payload.get("bpm") or (parent_track or {}).get("bpm") or 118,
                    "musical_key": payload.get("musical_key") or (parent_track or {}).get("musical_key") or "F minor",
                    "provenance": provenance, "source_type": "generated" if kind == "generate" else "derived",
                    "parent_track_id": parent_id, "favorite": False, "audio_path": str(output_path),
                    "mime_type": "audio/wav", "version": base_version + 1,
                }
            )
            self.repository.update_job(
                job_id, status="completed", progress=100, message="Ready to play", track_id=track["id"]
            )
        except Exception as error:  # Worker boundary: surface safe message through job status.
            self.repository.update_job(
                job_id, status="failed", progress=100, message="Generation failed", error=str(error)
            )
