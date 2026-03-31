"""Activity 6 — Voice of the City: Speech Services module.

Handles speech-to-text transcription, speech translation,
text-to-speech synthesis, and SSML generation for the Memphis 311
voice pipeline.

Azure Services: Azure Speech (STT, TTS, Speech Translation)
Exam Objectives: D5.2 — Implement speech solutions
"""

import os

# ── Lazy client helpers ──────────────────────────────────────────────────

_speech_config = None
_translation_config = None


def _get_speech_config():
    """Lazy-initialize the SpeechConfig for STT and TTS."""
    global _speech_config
    if _speech_config is None:
        import azure.cognitiveservices.speech as speechsdk

        _speech_config = speechsdk.SpeechConfig(
            subscription=os.environ["AZURE_SPEECH_KEY"],
            region=os.environ["AZURE_SPEECH_REGION"],
        )
    return _speech_config


def _get_translation_config(target_languages: list[str]):
    """Lazy-initialize the SpeechTranslationConfig.

    Args:
        target_languages: List of target language codes (e.g., ["en", "es"]).
    """
    import azure.cognitiveservices.speech as speechsdk

    config = speechsdk.translation.SpeechTranslationConfig(
        subscription=os.environ["AZURE_SPEECH_KEY"],
        region=os.environ["AZURE_SPEECH_REGION"],
    )
    for lang in target_languages:
        config.add_target_language(lang)
    return config


# ── Step 1: Speech-to-Text ───────────────────────────────────────────────


def transcribe_audio(audio_path: str) -> dict:
    """Transcribe a WAV audio file using Azure Speech-to-Text.

    Uses SpeechRecognizer with AudioConfig(filename=audio_path)
    and recognize_once() for single-utterance recognition.

    Args:
        audio_path: Path to a WAV audio file.

    Returns:
        dict with keys: text, confidence, duration_seconds, language
        On failure: dict with text="" and confidence=0.0

    TODO: Students implement this function.
    Hints:
        1. Import azure.cognitiveservices.speech as speechsdk
        2. Create AudioConfig from the WAV file path
        3. Create SpeechRecognizer with the speech config and audio config
        4. Call recognize_once() to get the result
        5. Check result.reason == speechsdk.ResultReason.RecognizedSpeech
        6. Return the transcription text, confidence, and duration
    """
    # TODO: Implement speech-to-text transcription
    return {"text": "", "confidence": 0.0, "duration_seconds": 0.0, "language": ""}


# ── Step 2: Speech Translation ───────────────────────────────────────────


def translate_speech(audio_path: str, target_languages: list[str] = None) -> dict:
    """Translate speech from a WAV audio file to target languages.

    Uses TranslationRecognizer with SpeechTranslationConfig for
    real-time speech translation.

    Args:
        audio_path: Path to a WAV audio file.
        target_languages: Target language codes (default: ["en"]).

    Returns:
        dict with keys: source_language, translations (dict of lang->text),
                        duration_seconds
        On failure: dict with empty translations

    TODO: Students implement this function.
    Hints:
        1. Import azure.cognitiveservices.speech as speechsdk
        2. Use _get_translation_config() with target languages
        3. Create AudioConfig from the WAV file path
        4. Create TranslationRecognizer with translation config and audio config
        5. Call recognize_once() to get the result
        6. Check result.reason == speechsdk.ResultReason.TranslatedSpeech
        7. Extract translations from result.translations dictionary
    """
    if target_languages is None:
        target_languages = ["en"]

    # TODO: Implement speech translation
    return {
        "source_language": "",
        "translations": {},
        "duration_seconds": 0.0,
    }


# ── Step 5: Text-to-Speech ───────────────────────────────────────────────


def synthesize_response(text: str, output_path: str) -> dict:
    """Synthesize speech from plain text using Azure TTS.

    Uses SpeechSynthesizer with AudioConfig to produce a WAV file.

    Args:
        text: The text to synthesize.
        output_path: Path for the output WAV file.

    Returns:
        dict with keys: output_path, duration_seconds, voice_name, used_ssml

    TODO: Students implement this function.
    Hints:
        1. Import azure.cognitiveservices.speech as speechsdk
        2. Get speech config via _get_speech_config()
        3. Set the voice: config.speech_synthesis_voice_name = "en-US-JennyNeural"
        4. Create AudioConfig.from_wav_file_output(output_path)
        5. Create SpeechSynthesizer with both configs
        6. Call speak_text_async(text).get() to synthesize
        7. Check result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted
    """
    # TODO: Implement text-to-speech synthesis
    return {
        "output_path": output_path,
        "duration_seconds": 0.0,
        "voice_name": "",
        "used_ssml": False,
    }


def build_ssml(
    text: str,
    voice: str = "en-US-JennyNeural",
    rate: str = "medium",
    pitch: str = "default",
) -> str:
    """Build an SSML document for fine-grained speech synthesis control.

    Must include: <speak>, <voice>, <prosody>, at least one <break>,
    and at least one <say-as> element.

    Args:
        text: The text content to synthesize.
        voice: Azure Neural voice name.
        rate: Speech rate (e.g., "slow", "medium", "fast").
        pitch: Speech pitch (e.g., "low", "default", "high").

    Returns:
        A valid SSML XML string.

    TODO: Students implement this function.
    Hints:
        1. Start with <speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis"
           xml:lang="en-US">
        2. Add <voice name="..."> wrapper
        3. Add <prosody rate="..." pitch="..."> for speech control
        4. Include at least one <break time="500ms"/> for natural pauses
        5. Use <say-as interpret-as="..."> for numbers, dates, or phone numbers
        6. Close all tags properly
    """
    # TODO: Build SSML document
    return ""


def synthesize_ssml(ssml: str, output_path: str) -> dict:
    """Synthesize speech from an SSML document.

    Args:
        ssml: A valid SSML XML string.
        output_path: Path for the output WAV file.

    Returns:
        dict with keys: output_path, duration_seconds, voice_name, used_ssml

    TODO: Students implement this function.
    Hints:
        1. Get speech config via _get_speech_config()
        2. Create AudioConfig.from_wav_file_output(output_path)
        3. Create SpeechSynthesizer
        4. Call speak_ssml_async(ssml).get() instead of speak_text_async
        5. Check result.reason
    """
    # TODO: Implement SSML synthesis
    return {
        "output_path": output_path,
        "duration_seconds": 0.0,
        "voice_name": "",
        "used_ssml": True,
    }
