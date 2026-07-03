import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient


@pytest.fixture()
def client(tmp_path: Path):
    os.environ["AURALIS_DATABASE_URL"] = f"sqlite:///{tmp_path / 'test.db'}"
    os.environ["AURALIS_STORAGE_DIR"] = str(tmp_path / "storage")
    os.environ["AURALIS_JOB_DELAY_SECONDS"] = "0.01"
    from auralis_api.config import get_settings
    get_settings.cache_clear()
    from auralis_api.main import app
    with TestClient(app) as test_client:
        yield test_client
