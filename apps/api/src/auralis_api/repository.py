import json
import sqlite3
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Iterator


def now() -> str:
    return datetime.now(UTC).isoformat()


class Repository:
    def __init__(self, database_path: Path):
        self.database_path = database_path
        database_path.parent.mkdir(parents=True, exist_ok=True)
        self._migrate()

    @contextmanager
    def connect(self) -> Iterator[sqlite3.Connection]:
        connection = sqlite3.connect(self.database_path, check_same_thread=False)
        connection.row_factory = sqlite3.Row
        try:
            yield connection
            connection.commit()
        finally:
            connection.close()

    def _migrate(self) -> None:
        with self.connect() as db:
            db.executescript(
                """
                CREATE TABLE IF NOT EXISTS tracks (
                  id TEXT PRIMARY KEY, title TEXT NOT NULL, prompt TEXT NOT NULL DEFAULT '',
                  lyrics TEXT, tags TEXT NOT NULL DEFAULT '[]', duration REAL NOT NULL DEFAULT 0,
                  bpm INTEGER, musical_key TEXT, created_at TEXT NOT NULL,
                  provenance TEXT NOT NULL, source_type TEXT NOT NULL,
                  parent_track_id TEXT, favorite INTEGER NOT NULL DEFAULT 0,
                  audio_path TEXT, mime_type TEXT, version INTEGER NOT NULL DEFAULT 1,
                  FOREIGN KEY(parent_track_id) REFERENCES tracks(id)
                );
                CREATE TABLE IF NOT EXISTS jobs (
                  id TEXT PRIMARY KEY, kind TEXT NOT NULL, status TEXT NOT NULL,
                  progress INTEGER NOT NULL DEFAULT 0, message TEXT NOT NULL,
                  track_id TEXT, error TEXT, payload TEXT NOT NULL DEFAULT '{}',
                  created_at TEXT NOT NULL, updated_at TEXT NOT NULL
                );
                """
            )

    @staticmethod
    def _track(row: sqlite3.Row, versions: list[dict[str, Any]] | None = None) -> dict[str, Any]:
        data = dict(row)
        data["tags"] = json.loads(data["tags"] or "[]")
        data["favorite"] = bool(data["favorite"])
        data["has_audio"] = bool(data.pop("audio_path"))
        data.pop("mime_type", None)
        data["versions"] = versions or []
        return data

    def create_track(self, values: dict[str, Any]) -> dict[str, Any]:
        fields = [
            "id", "title", "prompt", "lyrics", "tags", "duration", "bpm", "musical_key",
            "created_at", "provenance", "source_type", "parent_track_id", "favorite",
            "audio_path", "mime_type", "version",
        ]
        payload = {**values, "created_at": values.get("created_at", now())}
        payload["tags"] = json.dumps(payload.get("tags", []))
        payload["favorite"] = int(payload.get("favorite", False))
        with self.connect() as db:
            db.execute(
                f"INSERT INTO tracks ({','.join(fields)}) VALUES ({','.join('?' for _ in fields)})",
                [payload.get(field) for field in fields],
            )
        return self.get_track(payload["id"])

    def get_track(self, track_id: str, include_versions: bool = True) -> dict[str, Any] | None:
        with self.connect() as db:
            row = db.execute("SELECT * FROM tracks WHERE id = ?", (track_id,)).fetchone()
            if not row:
                return None
            versions: list[dict[str, Any]] = []
            if include_versions:
                children = db.execute(
                    "SELECT * FROM tracks WHERE parent_track_id = ? ORDER BY version DESC", (track_id,)
                ).fetchall()
                versions = [self._track(child) for child in children]
            return self._track(row, versions)

    def get_audio(self, track_id: str) -> tuple[str, str] | None:
        with self.connect() as db:
            row = db.execute(
                "SELECT audio_path, mime_type FROM tracks WHERE id = ?", (track_id,)
            ).fetchone()
            if not row or not row["audio_path"]:
                return None
            return row["audio_path"], row["mime_type"] or "application/octet-stream"

    def list_tracks(self, query: str = "", provenance: str | None = None) -> list[dict[str, Any]]:
        clauses, params = [], []
        if query:
            clauses.append("(title LIKE ? OR prompt LIKE ? OR tags LIKE ?)")
            token = f"%{query}%"
            params.extend([token, token, token])
        if provenance:
            clauses.append("provenance = ?")
            params.append(provenance)
        where = f" WHERE {' AND '.join(clauses)}" if clauses else ""
        with self.connect() as db:
            rows = db.execute(f"SELECT * FROM tracks{where} ORDER BY created_at DESC", params).fetchall()
            return [self._track(row) for row in rows]

    def update_track(self, track_id: str, changes: dict[str, Any]) -> dict[str, Any] | None:
        allowed = {"title", "tags", "favorite"}
        values = {key: value for key, value in changes.items() if key in allowed and value is not None}
        if not values:
            return self.get_track(track_id)
        if "tags" in values:
            values["tags"] = json.dumps(values["tags"])
        if "favorite" in values:
            values["favorite"] = int(values["favorite"])
        with self.connect() as db:
            cursor = db.execute(
                f"UPDATE tracks SET {','.join(f'{key} = ?' for key in values)} WHERE id = ?",
                [*values.values(), track_id],
            )
        return self.get_track(track_id) if cursor.rowcount else None

    def delete_track(self, track_id: str) -> str | None:
        with self.connect() as db:
            row = db.execute("SELECT audio_path FROM tracks WHERE id = ?", (track_id,)).fetchone()
            if not row:
                return None
            db.execute("DELETE FROM tracks WHERE id = ?", (track_id,))
            return row["audio_path"]

    def create_job(self, values: dict[str, Any]) -> dict[str, Any]:
        stamp = now()
        payload = {**values, "created_at": stamp, "updated_at": stamp}
        fields = ["id", "kind", "status", "progress", "message", "track_id", "error", "payload", "created_at", "updated_at"]
        payload["payload"] = json.dumps(payload.get("payload", {}))
        with self.connect() as db:
            db.execute(
                f"INSERT INTO jobs ({','.join(fields)}) VALUES ({','.join('?' for _ in fields)})",
                [payload.get(field) for field in fields],
            )
        return self.get_job(payload["id"])

    def update_job(self, job_id: str, **changes: Any) -> dict[str, Any] | None:
        values = {**changes, "updated_at": now()}
        with self.connect() as db:
            cursor = db.execute(
                f"UPDATE jobs SET {','.join(f'{key} = ?' for key in values)} WHERE id = ?",
                [*values.values(), job_id],
            )
        return self.get_job(job_id) if cursor.rowcount else None

    def get_job(self, job_id: str) -> dict[str, Any] | None:
        with self.connect() as db:
            row = db.execute("SELECT * FROM jobs WHERE id = ?", (job_id,)).fetchone()
            if not row:
                return None
            data = dict(row)
            data.pop("payload", None)
            return data
