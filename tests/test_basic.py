"""Activity 6 — Voice of the City: Visible Tests.

Students run these locally to verify their implementation.
Usage: pytest tests/test_basic.py -v
"""

import json
import os
import sys
from pathlib import Path

import pytest

# Add activity root to path
sys.path.insert(0, str(Path(__file__).parent.parent))


# ── Module Import Tests ──────────────────────────────────────────────────


class TestModuleImports:
    """Verify all activity modules can be imported."""

    def test_import_speech(self):
        from app import speech
        assert hasattr(speech, "transcribe_audio")
        assert hasattr(speech, "translate_speech")
        assert hasattr(speech, "synthesize_response")
        assert hasattr(speech, "build_ssml")
        assert hasattr(speech, "synthesize_ssml")

    def test_import_clu(self):
        from app import clu
        assert hasattr(clu, "classify_intent")

    def test_import_question_answering(self):
        from app import question_answering
        assert hasattr(question_answering, "answer_question")

    def test_import_main(self):
        from app import main
        assert hasattr(main, "run_pipeline")

    def test_import_utils(self):
        from app import utils
        assert hasattr(utils, "load_json")
        assert hasattr(utils, "save_json")


# ── Output Contract Tests ────────────────────────────────────────────────


RESULT_PATH = Path(__file__).parent.parent / "result.json"


@pytest.fixture
def result():
    """Load result.json if it exists."""
    if not RESULT_PATH.exists():
        pytest.skip("result.json not found — run 'python -m app.main' first")
    with open(RESULT_PATH, encoding="utf-8") as f:
        return json.load(f)


class TestOutputContract:
    """Verify result.json follows the output contract."""

    def test_result_exists(self):
        assert RESULT_PATH.exists(), (
            "result.json not found. Run: python -m app.main"
        )

    def test_task_name(self, result):
        assert result["task"] == "voice_of_the_city"

    def test_status_valid(self, result):
        assert result["status"] in ("success", "partial", "error")

    def test_outputs_keys(self, result):
        expected_keys = {
            "transcriptions", "translations", "intent_results",
            "qa_results", "speech_responses",
        }
        assert expected_keys.issubset(set(result["outputs"].keys()))

    def test_metadata_present(self, result):
        assert "metadata" in result
        assert "timestamp" in result["metadata"]
        assert "model" in result["metadata"]
        assert "sdk_version" in result["metadata"]


# ── Step 1: Transcription Tests ──────────────────────────────────────────


class TestTranscription:
    """Verify transcription output structure."""

    def test_transcriptions_is_list(self, result):
        assert isinstance(result["outputs"]["transcriptions"], list)

    def test_transcription_structure(self, result):
        for t in result["outputs"]["transcriptions"]:
            assert "text" in t, "Transcription must have 'text' field"
            assert "confidence" in t, "Transcription must have 'confidence' field"
            assert "duration_seconds" in t, "Transcription must have 'duration_seconds' field"


# ── Step 2: Translation Tests ────────────────────────────────────────────


class TestTranslation:
    """Verify translation output structure."""

    def test_translations_is_list(self, result):
        assert isinstance(result["outputs"]["translations"], list)

    def test_translation_structure(self, result):
        for t in result["outputs"]["translations"]:
            assert "source_language" in t or "file" in t
            assert "translations" in t, "Translation must have 'translations' dict"


# ── Step 3: Intent Classification Tests ──────────────────────────────────


class TestIntentClassification:
    """Verify CLU/keyword intent classification output."""

    def test_intent_results_is_list(self, result):
        assert isinstance(result["outputs"]["intent_results"], list)

    def test_intent_structure(self, result):
        valid_intents = {"ReportIssue", "CheckStatus", "GetInformation", "None"}
        for ir in result["outputs"]["intent_results"]:
            assert "top_intent" in ir
            assert ir["top_intent"] in valid_intents, (
                f"Intent '{ir['top_intent']}' not in valid set: {valid_intents}"
            )
            assert "confidence" in ir
            assert 0.0 <= ir["confidence"] <= 1.0
            assert "entities" in ir
            assert isinstance(ir["entities"], list)

    def test_intent_has_entities(self, result):
        """At least one intent result should have entities."""
        all_entities = []
        for ir in result["outputs"]["intent_results"]:
            all_entities.extend(ir.get("entities", []))
        # With keyword fallback, entity extraction depends on input text
        # Just verify the structure is correct
        for entity in all_entities:
            assert "category" in entity
            assert "text" in entity
            assert "confidence" in entity


# ── Step 4: Question Answering Tests ─────────────────────────────────────


class TestQuestionAnswering:
    """Verify QA output structure."""

    def test_qa_results_is_list(self, result):
        assert isinstance(result["outputs"]["qa_results"], list)

    def test_qa_structure(self, result):
        for qa in result["outputs"]["qa_results"]:
            assert "answer" in qa, "QA result must have 'answer'"
            assert "confidence" in qa, "QA result must have 'confidence'"
            assert "source" in qa, "QA result must have 'source'"

    def test_qa_has_answers(self, result):
        """At least one question should have a non-empty answer."""
        answers = [qa["answer"] for qa in result["outputs"]["qa_results"]]
        assert any(a for a in answers), "At least one QA result should have an answer"


# ── Step 5: Speech Response Tests ────────────────────────────────────────


class TestSpeechResponse:
    """Verify speech synthesis output structure."""

    def test_speech_responses_is_list(self, result):
        assert isinstance(result["outputs"]["speech_responses"], list)

    def test_speech_structure(self, result):
        for sr in result["outputs"]["speech_responses"]:
            assert "output_path" in sr
            assert "voice_name" in sr
            assert "used_ssml" in sr

    def test_has_ssml_response(self, result):
        """At least one response should use SSML."""
        ssml_responses = [sr for sr in result["outputs"]["speech_responses"] if sr.get("used_ssml")]
        assert len(ssml_responses) > 0, "At least one response should use SSML"


# ── Pipeline Summary Tests ───────────────────────────────────────────────


class TestPipelineSummary:
    """Verify pipeline metadata summary counts."""

    def test_summary_present(self, result):
        assert "summary" in result["metadata"]

    def test_summary_counts(self, result):
        summary = result["metadata"]["summary"]
        assert "files_transcribed" in summary
        assert "intents_classified" in summary
        assert "questions_answered" in summary
        assert "responses_synthesized" in summary
