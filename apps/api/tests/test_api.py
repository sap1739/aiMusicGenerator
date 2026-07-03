import io
import time
import wave


def wav_bytes() -> bytes:
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as output:
        output.setnchannels(1)
        output.setsampwidth(2)
        output.setframerate(8000)
        output.writeframes(b"\x00\x00" * 8000)
    return buffer.getvalue()


def test_health(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["engine"] == "demo"


def test_generation_completes_and_enters_library(client):
    response = client.post("/api/generate", json={"prompt": "Dreamy analogue synth horizon", "title": "Glass Horizon", "duration": 10})
    assert response.status_code == 202
    job_id = response.json()["id"]
    for _ in range(80):
        job = client.get(f"/api/jobs/{job_id}").json()
        if job["status"] == "completed":
            break
        time.sleep(0.01)
    assert job["status"] == "completed"
    tracks = client.get("/api/tracks").json()
    assert tracks[0]["title"] == "Glass Horizon"
    assert client.get(f"/api/audio/{tracks[0]['id']}").status_code == 200


def test_upload_requires_rights(client):
    response = client.post(
        "/api/upload", data={"rights_confirmed": "false"},
        files={"file": ("source.wav", wav_bytes(), "audio/wav")},
    )
    assert response.status_code == 422


def test_exact_artist_policy(client):
    response = client.post("/api/generate", json={"prompt": "Make this sound exactly like a living star"})
    assert response.status_code == 422
