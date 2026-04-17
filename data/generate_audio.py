#!/usr/bin/env python3
"""Generate sample WAV audio files for Activity 6 — Voice of the City.

Uses Azure Text-to-Speech to create realistic 311 call recordings
in multiple languages for the speech pipeline.

Prerequisites:
    - AZURE_SPEECH_KEY and AZURE_SPEECH_REGION environment variables
    - azure-cognitiveservices-speech package installed

Usage:
    python data/generate_audio.py
"""

import json
import os
import sys
from pathlib import Path

try:
    import azure.cognitiveservices.speech as speechsdk
except ImportError:
    print("ERROR: azure-cognitiveservices-speech not installed.")
    print("Run: pip install azure-cognitiveservices-speech")
    sys.exit(1)

from dotenv import load_dotenv

# Load .env from activity root
load_dotenv(Path(__file__).parent.parent / ".env")


def generate_audio():
    """Generate all audio files from the manifest."""
    speech_key = os.environ.get("AZURE_SPEECH_KEY")
    speech_region = os.environ.get("AZURE_SPEECH_REGION")

    if not speech_key or not speech_region:
        print("ERROR: AZURE_SPEECH_KEY and AZURE_SPEECH_REGION must be set.")
        print("Copy .env.example to .env and fill in your credentials.")
        sys.exit(1)

    # Load manifest
    manifest_path = Path(__file__).parent / "audio_manifest.json"
    with open(manifest_path, encoding="utf-8") as f:
        manifest = json.load(f)

    # Create output directory
    audio_dir = Path(__file__).parent / "audio"
    audio_dir.mkdir(exist_ok=True)

    speech_config = speechsdk.SpeechConfig(
        subscription=speech_key,
        region=speech_region,
    )

    print(f"Generating {len(manifest['files'])} audio files...")
    print(f"Output directory: {audio_dir}\n")

    success_count = 0
    for file_info in manifest["files"]:
        filename = file_info["filename"]
        voice = file_info["voice"]
        text = file_info["text"]
        output_path = str(audio_dir / filename)

        print(f"  [{file_info['language']}] {filename}")
        print(f"    Voice: {voice}")
        print(f"    Text: {text[:60]}...")

        speech_config.speech_synthesis_voice_name = voice
        audio_config = speechsdk.audio.AudioOutputConfig(filename=output_path)
        synthesizer = speechsdk.SpeechSynthesizer(
            speech_config=speech_config,
            audio_config=audio_config,
        )

        result = synthesizer.speak_text_async(text).get()

        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            file_size = Path(output_path).stat().st_size
            print(f"    \u2713 Generated ({file_size:,} bytes)")
            success_count += 1
        elif result.reason == speechsdk.ResultReason.Canceled:
            details = result.cancellation_details
            print(f"    \u2717 Failed: {details.reason}")
            if details.error_details:
                print(f"      Error: {details.error_details}")

    print(f"\nDone! Generated {success_count}/{len(manifest['files'])} audio files.")
    if success_count < len(manifest["files"]):
        print("Some files failed \u2014 check your Azure Speech credentials and quota.")


if __name__ == "__main__":
    generate_audio()
