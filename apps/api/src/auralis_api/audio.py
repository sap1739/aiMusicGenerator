import math
import shutil
import struct
import wave
from pathlib import Path


def ffmpeg_available() -> bool:
    return shutil.which("ffmpeg") is not None


def inspect_audio(path: Path) -> tuple[float, int | None, str | None]:
    if path.suffix.lower() == ".wav":
        try:
            with wave.open(str(path), "rb") as source:
                return source.getnframes() / source.getframerate(), None, None
        except wave.Error:
            pass
    return 0.0, None, None


def write_demo_wave(path: Path, duration: float, seed: int = 0) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    sample_rate = 22_050
    safe_duration = max(8.0, min(duration, 28.0))
    frequencies = (110 + seed % 80, 164 + seed % 70, 220 + seed % 50)
    with wave.open(str(path), "wb") as output:
        output.setnchannels(2)
        output.setsampwidth(2)
        output.setframerate(sample_rate)
        frames = bytearray()
        for index in range(int(sample_rate * safe_duration)):
            time = index / sample_rate
            envelope = min(1.0, time / 0.8, (safe_duration - time) / 1.2)
            pulse = 0.65 + 0.35 * math.sin(2 * math.pi * 0.5 * time)
            value = sum(math.sin(2 * math.pi * frequency * time) for frequency in frequencies)
            sample = int(5_600 * envelope * pulse * value / len(frequencies))
            frames.extend(struct.pack("<hh", sample, sample))
        output.writeframes(frames)
