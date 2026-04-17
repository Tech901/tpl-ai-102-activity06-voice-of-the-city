"""Activity 6 — Voice of the City: Conversational Language Understanding module.

Classifies citizen intent from transcribed 311 calls using a pre-trained
CLU model, with keyword fallback for local development.

Azure Services: Azure AI Language — Conversational Language Understanding
Exam Objectives: D5.3 — Implement CLU lifecycle
"""

import os
import re

# ── Lazy client ──────────────────────────────────────────────────────────

_clu_client = None


def _get_clu_client():
    """Lazy-initialize the ConversationAnalysisClient."""
    global _clu_client
    if _clu_client is None:
        from azure.ai.language.conversations import ConversationAnalysisClient
        from azure.core.credentials import AzureKeyCredential

        _clu_client = ConversationAnalysisClient(
            endpoint=os.environ["AZURE_AI_LANGUAGE_ENDPOINT"],
            credential=AzureKeyCredential(os.environ["AZURE_AI_LANGUAGE_KEY"]),
        )
    return _clu_client


# ── Keyword fallback ─────────────────────────────────────────────────────

# Simple keyword-based fallback for when CLU is not configured
_KEYWORD_INTENTS = {
    "ReportIssue": [
        r"pothole", r"broken", r"damaged", r"trash", r"garbage",
        r"graffiti", r"flooding", r"water\s+leak", r"streetlight",
        r"sidewalk", r"report", r"complaint",
    ],
    "CheckStatus": [
        r"status", r"update", r"case\s+number", r"check\s+on",
        r"follow\s+up", r"tracking", r"when\s+will",
    ],
    "GetInformation": [
        r"hours", r"where\s+is", r"how\s+do\s+i", r"what\s+is",
        r"phone\s+number", r"address", r"schedule", r"recycling",
        r"pickup", r"holiday",
    ],
}


def _keyword_classify(text: str) -> dict:
    """Classify intent using keyword matching (fallback when CLU unavailable)."""
    text_lower = text.lower()
    best_intent = "None"
    best_score = 0.0

    for intent, patterns in _KEYWORD_INTENTS.items():
        matches = sum(1 for p in patterns if re.search(p, text_lower))
        score = min(matches / 3.0, 0.95)  # Cap at 0.95
        if score > best_score:
            best_score = score
            best_intent = intent

    # Simple entity extraction
    entities = []
    location_patterns = [
        r"(?:on|at|near)\s+([\w\s]+(?:Street|Ave|Blvd|Road|Dr|Lane|Pkwy|Memphis))",
        r"(downtown|midtown|east\s+memphis|south\s+memphis|north\s+memphis|whitehaven|cordova|bartlett|germantown)",
    ]
    for pattern in location_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            entities.append({
                "category": "Location",
                "text": match.group(1).strip(),
                "confidence": 0.7,
            })

    case_match = re.search(r"(?:case|ticket|request)\s*#?\s*(\d+)", text, re.IGNORECASE)
    if case_match:
        entities.append({
            "category": "CaseNumber",
            "text": case_match.group(1),
            "confidence": 0.9,
        })

    return {
        "top_intent": best_intent,
        "confidence": best_score,
        "entities": entities,
        "method": "keyword_fallback",
    }


# ── Step 3: Intent Classification ────────────────────────────────────────


def classify_intent(text: str) -> dict:
    """Classify the intent of a transcribed 311 call using CLU.

    Attempts to use the Azure CLU model first. Falls back to keyword
    matching if CLU environment variables are not configured.

    Args:
        text: Transcribed text from a 311 call.

    Returns:
        dict with keys: top_intent, confidence, entities (list of
        {category, text, confidence}), method ("clu" or "keyword_fallback")

    TODO: Students implement the CLU API call portion.
    Hints:
        1. Check if CLU_PROJECT_NAME and CLU_DEPLOYMENT_NAME are set
        2. If not, return _keyword_classify(text) as fallback
        3. Get the CLU client via _get_clu_client()
        4. Build the request body with analyze_conversation():
           - kind: "Conversation"
           - analysisInput.conversationItem: {id: "1", text: text, participantId: "caller"}
           - parameters: {projectName, deploymentName}
        5. Extract the top intent and entities from the response
        6. Return structured result with method="clu"
    """
    # Check if CLU is configured
    project = os.environ.get("CLU_PROJECT_NAME")
    deployment = os.environ.get("CLU_DEPLOYMENT_NAME")

    if not project or not deployment:
        return _keyword_classify(text)

    # TODO: Implement CLU API call
    # For now, fall back to keyword matching
    return _keyword_classify(text)
