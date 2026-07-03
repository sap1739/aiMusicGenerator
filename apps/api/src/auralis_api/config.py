from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=(".env", "../../.env"), env_prefix="AURALIS_")

    database_url: str = "sqlite:///./data/auralis.db"
    storage_dir: Path = Path("./storage")
    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000"
    engine: str = "demo"
    ace_step_url: str = "http://localhost:8001"
    ace_step_api_key: str | None = None
    job_delay_seconds: float = 1.25
    max_upload_mb: int = 100

    @property
    def database_path(self) -> Path:
        value = self.database_url.removeprefix("sqlite:///")
        return Path(value).expanduser().resolve()

    @property
    def allowed_origins(self) -> list[str]:
        return [item.strip() for item in self.cors_origins.split(",") if item.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
