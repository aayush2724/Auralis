"""
auralis/src/api/routes/chat.py
───────────────────────────────────
API endpoints for Auralis — POST /chat and GET /session/{session_id}.
"""

from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, HTTPException, Path

from src.api.schemas import (
    ChatRequest,
    ChatResponse,
    ExplanationResponse,
    RetrievedDoc,
    SessionFactsResponse,
)
from src.graph.graph import run_graph
from src.memory.db import load_session, save_session
from src.memory.memory import ConversationMemory
from src.utils.explainability import explain

logger = logging.getLogger("auralis.api.chat")
router = APIRouter()


@router.post(
    "/chat",
    response_model=ChatResponse,
    summary="Process a customer utterance and generate a persona-targeted, citation-honest sales response.",
    description=(
        "Runs the customer utterance through parallel objection, sentiment, and persona classifiers. "
        "Retrieves supporting evidence, selects a specialized negotiation strategy, generates a response, "
        "and logs the decision audit trail."
    ),
)
async def chat(request: ChatRequest) -> ChatResponse:
    session_id = request.session_id.strip()
    message = request.message.strip()

    if not session_id:
        raise HTTPException(status_code=400, detail="`session_id` must be a non-empty string.")
    if not message:
        raise HTTPException(status_code=400, detail="`message` must be a non-empty string.")

    try:
        # 1. Load or create ConversationMemory for the session_id
        memory = await ConversationMemory.from_session(session_id)

        # 2. Call run_graph(message, memory)
        # Note: run_graph is a synchronous function that handles LLM call and classifier execution.
        # We can run it directly as it handles thread pooling internally.
        state = run_graph(message, memory)

        # 3. Call explain(state) and map result
        exp_dict = explain(state)
        explanation = ExplanationResponse(
            objection_reason=exp_dict["objection_reason"],
            persona_reason=exp_dict["persona_reason"],
            sentiment_reason=exp_dict["sentiment_reason"],
            strategy_reason=exp_dict["strategy_reason"],
            trigger_phrases=exp_dict["trigger_phrases"],
            confidence_note=exp_dict["confidence_note"],
            handoff_reason=exp_dict["handoff_reason"],
        )

        # 4. Persist session via save_session()
        # Fetch up-to-date facts from memory
        facts = memory.get_facts()
        # Ensure we capture the final persona label from the graph state
        persona_dict = state.get("persona") or {}
        persona_label = persona_dict.get("label")
        if persona_label:
            facts["persona_label"] = persona_label

        await save_session(session_id, facts)

        # Map retrieved_docs
        retrieved_docs_raw = state.get("retrieved_docs") or []
        retrieved_docs = [
            RetrievedDoc(
                text=d.get("text", ""),
                source_file=d.get("source_file", ""),
                chunk_index=d.get("chunk_index", -1),
                score=d.get("score", 0.0),
            )
            for d in retrieved_docs_raw
        ]

        # 5. Build and return ChatResponse
        objection_dict = state.get("objection") or {}
        sentiment_dict = state.get("sentiment") or {}

        return ChatResponse(
            response=state.get("response", ""),
            objection_label=objection_dict.get("label", "neutral"),
            confidence=state.get("confidence", 1.0),
            sentiment=sentiment_dict.get("label", "neutral"),
            persona=persona_dict.get("label", "Unknown"),
            strategy=state.get("strategy", "discovery_questions"),
            citations=state.get("citations", ""),
            should_handoff=state.get("should_handoff", False),
            explanation=explanation,
            retrieved_docs=retrieved_docs,
            session_id=session_id,
            memory_context=memory.get_context_string(),
        )

    except Exception as exc:
        logger.exception("Error in POST /chat for session %s", session_id)
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while processing your request: {exc}",
        )


@router.get(
    "/session/{session_id}",
    response_model=SessionFactsResponse,
    summary="Retrieve the extracted profile facts for a given customer session from PostgreSQL.",
)
async def get_session_facts(
    session_id: str = Path(..., description="The unique session identifier.")
) -> SessionFactsResponse:
    session_id = session_id.strip()
    if not session_id:
        raise HTTPException(status_code=400, detail="`session_id` must be a non-empty string.")

    try:
        facts = await load_session(session_id)
        if not facts:
            return SessionFactsResponse(
                session_id=session_id,
                company_name=None,
                persona_label=None,
                tools_mentioned=[],
                objections_raised=[],
                budget_signal=None,
                found=False,
            )

        return SessionFactsResponse(
            session_id=session_id,
            company_name=facts.get("company_name"),
            persona_label=facts.get("persona_label"),
            tools_mentioned=facts.get("tools_mentioned") or [],
            objections_raised=facts.get("objections_raised") or [],
            budget_signal=facts.get("budget_signal"),
            found=True,
        )
    except Exception as exc:
        logger.exception("Error in GET /session/%s", session_id)
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while retrieving session facts: {exc}",
        )
