"""Activity 6 — Voice of the City: Shared utilities."""

import json
import os
from pathlib import Path


def load_json(path: str | Path) -> dict | list:
    """Load a JSON file and return its contents."""
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_json(data: dict | list, path: str | Path) -> None:
    """Save data to a JSON file with pretty formatting."""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def get_audio_dir() -> Path:
    """Return the path to the audio data directory, creating it if needed."""
    audio_dir = Path(__file__).parent.parent / "data" / "audio"
    audio_dir.mkdir(parents=True, exist_ok=True)
    return audio_dir


def get_output_dir() -> Path:
    """Return the path to the output directory, creating it if needed."""
    output_dir = Path(__file__).parent.parent / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir
