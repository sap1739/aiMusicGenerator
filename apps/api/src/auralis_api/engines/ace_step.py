from pathlib import Path

import httpx


class AceStepEngine:
    """Thin adapter for the official ACE-Step 1.5 REST server.

    ACE-Step owns inference and model lifecycle. Auralis sends portable JSON/multipart
    requests and downloads completed audio, avoiding copied upstream implementation code.
    """

    name = "ace_step"

    def __init__(self, base_url: str, api_key: str | None = None):
        self.base_url = base_url.rstrip("/")
        self.headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}

    async def ready(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=4) as client:
                response = await client.get(f"{self.base_url}/health", headers=self.headers)
                return response.is_success
        except httpx.HTTPError:
            return False

    async def _submit_and_download(self, endpoint: str, payload: dict, output_path: Path) -> Path:
        async with httpx.AsyncClient(timeout=600) as client:
            response = await client.post(
                f"{self.base_url}{endpoint}", json=payload, headers=self.headers
            )
            response.raise_for_status()
            result = response.json()
            audio_url = result.get("audio_url") or result.get("output_url")
            if not audio_url:
                raise RuntimeError("ACE-Step response did not include an audio URL")
            audio = await client.get(audio_url, headers=self.headers)
            audio.raise_for_status()
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_bytes(audio.content)
            return output_path

    async def generate(self, payload: dict, output_path: Path) -> Path:
        return await self._submit_and_download("/generate", payload, output_path)

    async def transform(self, kind: str, payload: dict, source_path: Path, output_path: Path) -> Path:
        request = {**payload, "source_audio_path": str(source_path)}
        return await self._submit_and_download(f"/{kind}", request, output_path)
