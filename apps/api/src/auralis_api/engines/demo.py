import asyncio
from pathlib import Path

from ..audio import write_demo_wave


class DemoEngine:
    name = "demo"

    async def ready(self) -> bool:
        return True

    async def generate(self, payload: dict, output_path: Path) -> Path:
        await asyncio.to_thread(
            write_demo_wave, output_path, payload.get("duration", 24), hash(payload.get("prompt", ""))
        )
        return output_path

    async def transform(self, kind: str, payload: dict, source_path: Path, output_path: Path) -> Path:
        await asyncio.to_thread(
            write_demo_wave, output_path, payload.get("duration", 24), hash(kind + str(source_path))
        )
        return output_path
