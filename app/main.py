"""Activity 6 — Voice of the City: Pipeline Orchestrator.

Orchestrates the 5-step Memphis 311 voice pipeline:
  Step 1: Transcribe 311 call recordings (Speech-to-Text)
  Step 2: Translate non-English calls (Speech Translation)
  Step 3: Classify intent with CLU (Conversational Language Understanding)
  Step 4: Answer citizen FAQs (Custom Question Answering)
  Step 5: Synthesize voice responses (Text-to-Speech + SSML)

Memphis Scenario:
  Citizens call Memphis 311 to report issues, check status, and ask questions.
  Some callers speak Spanish, Vietnamese, or other languages. This pipeline
  processes those calls end-to-end: transcribe → translate → classify → answer → respond.

Usage:
    python -m app.main

Output:
    result.json — Pipeline results following the standard output contract
"""

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app import speech, clu, question_answering
from app.utils import get_audio_dir, get_output_dir, load_json, save_json


def run_pipeline() -> dict:
    """Run the complete 5-step voice pipeline.

    Returns:
        dict: The complete result following the output contract.
    """
    audio_dir = get_audio_dir()
    output_dir = get_output_dir()
    manifest_path = Path(__file__).parent.parent / "data" / "audio_manifest.json"

    # Load audio manifest
    if manifest_path.exists():
        manifest = load_json(manifest_path)
    else:
        print("[WARN] audio_manifest.json not found. Using default test inputs.")
        manifest = {
            "files": [
                {
                    "filename": "pothole_report_en.wav",
                    "language": "en-US",
                    "description": "English pothole report",
                    "expected_intent": "ReportIssue",
                },
                {
                    "filename": "trash_complaint_es.wav",
                    "language": "es-MX",
                    "description": "Spanish trash complaint",
                    "expected_intent": "ReportIssue",
                },
                {
                    "filename": "status_check_en.wav",
                    "language": "en-US",
                    "description": "English status check",
                    "expected_intent": "CheckStatus",
                },
            ]
        }

    # ── Step 1: Transcribe 311 Calls ─────────────────────────────────────
    print("\n[Step 1] Transcribing 311 call recordings...")
    transcriptions = []
    english_files = [f for f in manifest["files"] if f["language"].startswith("en")]

    for file_info in english_files:
        audio_path = str(audio_dir / file_info["filename"])
        if not Path(audio_path).exists():
            print(f"  [SKIP] {file_info['filename']} not found — run data/generate_audio.py first")
            transcriptions.append({
                "file": file_info["filename"],
                "text": "",
                "confidence": 0.0,
                "duration_seconds": 0.0,
                "language": file_info["language"],
                "status": "skipped",
            })
            continue

        print(f"  Transcribing: {file_info['filename']}...")
        result = speech.transcribe_audio(audio_path)
        result["file"] = file_info["filename"]
        result["status"] = "success" if result.get("text") else "error"
        transcriptions.append(result)
        print(f"  → {result.get('text', '(no text)')[:80]}...")

    # ── Step 2: Translate Non-English Calls ──────────────────────────────
    print("\n[Step 2] Translating non-English calls...")
    translations = []
    non_english_files = [f for f in manifest["files"] if not f["language"].startswith("en")]

    for file_info in non_english_files:
        audio_path = str(audio_dir / file_info["filename"])
        if not Path(audio_path).exists():
            print(f"  [SKIP] {file_info['filename']} not found — run data/generate_audio.py first")
            translations.append({
                "file": file_info["filename"],
                "source_language": file_info["language"],
                "translations": {},
                "duration_seconds": 0.0,
                "status": "skipped",
            })
            continue

        print(f"  Translating: {file_info['filename']}...")
        result = speech.translate_speech(audio_path, target_languages=["en"])
        result["file"] = file_info["filename"]
        result["status"] = "success" if result.get("translations") else "error"
        translations.append(result)
        en_text = result.get("translations", {}).get("en", "(no translation)")
        print(f"  → EN: {en_text[:80]}...")

    # ── Step 3: Classify Intent ──────────────────────────────────────────
    print("\n[Step 3] Classifying intent with CLU...")
    intent_results = []

    # Classify all transcribed/translated texts
    all_texts = []
    for t in transcriptions:
        if t.get("text"):
            all_texts.append({"text": t["text"], "source": t["file"]})
    for t in translations:
        en_text = t.get("translations", {}).get("en", "")
        if en_text:
            all_texts.append({"text": en_text, "source": t["file"]})

    for item in all_texts:
        print(f"  Classifying: {item['text'][:60]}...")
        result = clu.classify_intent(item["text"])
        result["source_file"] = item["source"]
        result["input_text"] = item["text"]
        intent_results.append(result)
        print(f"  → Intent: {result.get('top_intent')} (confidence: {result.get('confidence', 0):.2f})")

    # ── Step 4: Answer FAQs ──────────────────────────────────────────────
    print("\n[Step 4] Answering citizen FAQs...")
    faq_questions = [
        "What are the operating hours for Memphis 311?",
        "How do I report a pothole in my neighborhood?",
        "Can I check the status of my service request online?",
    ]

    qa_results = []
    for question in faq_questions:
        print(f"  Q: {question}")
        result = question_answering.answer_question(question)
        result["question"] = question
        qa_results.append(result)
        print(f"  A: {result.get('answer', '(no answer)')[:80]}...")

    # ── Step 5: Synthesize Responses ─────────────────────────────────────
    print("\n[Step 5] Synthesizing voice responses...")
    speech_responses = []

    # Plain text response
    confirmation = "Your pothole report for Poplar Avenue has been received. Case number 3-1-1-4-5-6-7. You will receive an update within 48 hours."
    plain_path = str(output_dir / "response_plain.wav")
    print(f"  Synthesizing plain text response...")
    plain_result = speech.synthesize_response(confirmation, plain_path)
    plain_result["type"] = "plain_text"
    speech_responses.append(plain_result)

    # SSML response
    ssml = speech.build_ssml(
        text=confirmation,
        voice="en-US-JennyNeural",
        rate="medium",
        pitch="default",
    )
    if ssml:
        ssml_path = str(output_dir / "response_ssml.wav")
        print(f"  Synthesizing SSML response...")
        ssml_result = speech.synthesize_ssml(ssml, ssml_path)
        ssml_result["type"] = "ssml"
        ssml_result["ssml_content"] = ssml
        speech_responses.append(ssml_result)
    else:
        print("  [SKIP] SSML not built — build_ssml() returned empty string")

    # ── Assemble result ──────────────────────────────────────────────────
    # Determine overall status
    has_transcription = any(t.get("text") for t in transcriptions)
    has_intent = any(i.get("top_intent") and i["top_intent"] != "None" for i in intent_results)
    has_qa = any(q.get("answer") for q in qa_results)

    if has_transcription and has_intent and has_qa:
        status = "success"
    elif has_transcription or has_intent or has_qa:
        status = "partial"
    else:
        status = "error"

    result = {
        "task": "voice_of_the_city",
        "status": status,
        "outputs": {
            "transcriptions": transcriptions,
            "translations": translations,
            "intent_results": intent_results,
            "qa_results": qa_results,
            "speech_responses": speech_responses,
        },
        "metadata": {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "model": "azure-speech",
            "sdk_version": "1.35.0",
            "pipeline_steps": 5,
            "summary": {
                "files_transcribed": len([t for t in transcriptions if t.get("text")]),
                "files_translated": len([t for t in translations if t.get("translations")]),
                "intents_classified": len(intent_results),
                "questions_answered": len(qa_results),
                "responses_synthesized": len(speech_responses),
            },
        },
    }

    # Save output
    output_path = Path(__file__).parent.parent / "result.json"
    save_json(result, output_path)
    print(f"\n{'='*60}")
    print(f"Pipeline complete! Status: {status}")
    print(f"Result saved to: {output_path}")
    print(f"{'='*60}")

    return result


if __name__ == "__main__":
    run_pipeline()
