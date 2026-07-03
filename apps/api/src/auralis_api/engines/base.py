from pathlib import Path
from typing import Protocol


class MusicEngine(Protocol):
    name: str

    async def ready(self) -> bool: ...

    async def generate(self, payload: dict, output_path: Path) -> Path: ...

    async def transform(self, kind: str, payload: dict, source_path: Path, output_path: Path) -> Path: ...
