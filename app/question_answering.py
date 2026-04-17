"""Activity 6 — Voice of the City: Custom Question Answering module.

Answers citizen FAQs using a pre-deployed Custom Question Answering
knowledge base about Memphis 311 services.

Azure Services: Azure AI Language — Custom Question Answering
Exam Objectives: D5.3 — Implement question answering solutions
"""

import os

# ── Lazy client ──────────────────────────────────────────────────────────

_qa_client = None


def _get_qa_client():
    """Lazy-initialize the QuestionAnsweringClient."""
    global _qa_client
    if _qa_client is None:
        from azure.ai.language.questionanswering import QuestionAnsweringClient
        from azure.core.credentials import AzureKeyCredential

        _qa_client = QuestionAnsweringClient(
            endpoint=os.environ["AZURE_AI_LANGUAGE_ENDPOINT"],
            credential=AzureKeyCredential(os.environ["AZURE_AI_LANGUAGE_KEY"]),
        )
    return _qa_client


# ── Fallback answers ─────────────────────────────────────────────────────

_FALLBACK_ANSWERS = {
    "hours": {
        "answer": "Memphis 311 is available 24/7 for phone calls. Online services are available at memphistn.gov/311.",
        "source": "fallback",
        "confidence": 0.5,
    },
    "report": {
        "answer": "You can report issues by calling 311, visiting memphistn.gov/311, or using the Memphis 311 app.",
        "source": "fallback",
        "confidence": 0.5,
    },
    "status": {
        "answer": "Check your request status at memphistn.gov/311 using your case number, or call 311 for updates.",
        "source": "fallback",
        "confidence": 0.5,
    },
}


def _fallback_answer(question: str) -> dict:
    """Simple keyword fallback when QA service is unavailable."""
    q_lower = question.lower()
    for keyword, answer_data in _FALLBACK_ANSWERS.items():
        if keyword in q_lower:
            return {
                "answer": answer_data["answer"],
                "confidence": answer_data["confidence"],
                "source": answer_data["source"],
                "follow_up_prompts": [],
            }
    return {
        "answer": "I don't have information about that. Please call 311 for assistance.",
        "confidence": 0.0,
        "source": "fallback",
        "follow_up_prompts": [],
    }


# ── Step 4: Question Answering ───────────────────────────────────────────


def answer_question(question: str) -> dict:
    """Answer a citizen FAQ using the Custom Question Answering knowledge base.

    Queries the pre-deployed QA project. Falls back to keyword matching
    if environment variables are not configured.

    Args:
        question: The citizen's question about Memphis 311 services.

    Returns:
        dict with keys: answer, confidence, source, follow_up_prompts

    TODO: Students implement the QA API call.
    Hints:
        1. Check if QA_PROJECT_NAME and QA_DEPLOYMENT_NAME are set
        2. If not, return _fallback_answer(question)
        3. Get the QA client via _get_qa_client()
        4. Call client.get_answers() with:
           - question=question
           - project_name=os.environ["QA_PROJECT_NAME"]
           - deployment_name=os.environ["QA_DEPLOYMENT_NAME"]
        5. Extract the top answer from response.answers[0]
        6. Return answer text, confidence, source, and follow_up_prompts
    """
    project = os.environ.get("QA_PROJECT_NAME")
    deployment = os.environ.get("QA_DEPLOYMENT_NAME")

    if not project or not deployment:
        return _fallback_answer(question)

    # TODO: Implement QA API call
    # For now, fall back to keyword matching
    return _fallback_answer(question)
