"""
auralis/src/api/routes/chat.py
───────────────────────────────────
Route handlers for POST /chat and GET /session/{session_id}.

Authorization
-------------
  POST /chat               → requires role: sales_rep | admin
  GET  /session/{id}       → requires role: admin

POST /chat
----------
  Request  : ChatRequest(session_id, message)
  Response : ChatResponse

  Handler steps (per spec):
    1. Load or create ConversationMemory for session_id.
    2. Call run_graph(message, memory)  →  GraphState.
    3. Call explain(state)              →  ExplanationResult; attach to response.
    4. Persist session via save_session().
    5. Build and return ChatResponse.

GET /session/{session_id}
--------------------------
  Returns all persisted facts for the session from PostgreSQL as
  SessionFactsResponse. Returns found=False (HTTP 200) if no session exists.

OpenAPI docs
------------
  Both endpoints are fully documented and visible at /docs (Feature 14).
  The Authorize button in Swagger UI accepts the JWT issued by POST /auth/token.
"""

from __future__ import annotations

import asyncio
import logging

from fastapi import APIRouter, HTTPException, Path

from src.ab.ab_test import ABVariant, assign_variant, static_response
from src.analytics.tracker import log_event
from src.api.auth import User, require_roles
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


# ─── POST /chat ───────────────────────────────────────────────────────────────

@router.post(
    "/chat",
    response_model=ChatResponse,
    summary="Process a customer utterance and generate a sales response.",
    description=(
        "Runs the utterance through parallel objection / sentiment / persona "
        "classifiers, retrieves supporting evidence from the knowledge base, "
        "selects a negotiation strategy, generates a persona-targeted response, "
        "and returns a full decision audit trail.\n\n"
        "**Required role**: `sales_rep` or `admin`.\n\n"
        "**Session memory** is loaded from PostgreSQL on each request and "
        "persisted after the graph completes (Feature 10)."
    ),
    responses={
        400: {"description": "Invalid request — empty session_id or message."},
        401: {"description": "Missing or invalid Bearer token."},
        403: {"description": "Insufficient role. Requires sales_rep or admin."},
        500: {"description": "Internal server error during graph execution."},
    },
)
async def chat(
    request: ChatRequest,
    current_user: User = require_roles("sales_rep", "admin"),
) -> ChatResponse:
    session_id = request.session_id.strip()
    message    = request.message.strip()

    if not session_id:
        raise HTTPException(status_code=400, detail="`session_id` must be a non-empty string.")
    if not message:
        raise HTTPException(status_code=400, detail="`message` must be a non-empty string.")

    logger.info(
        "POST /chat | user=%s role=%s session=%s",
        current_user.email, current_user.role, session_id,
    )

    try:
        # ── Step 0: Determine A/B variant ──────────────────────────────────────
        variant = await assign_variant(session_id)

        # ── Step 1: Load or create ConversationMemory ─────────────────────────
        memory = await ConversationMemory.from_session(session_id)

        if variant == ABVariant.STATIC:
            # ── STATIC branch: return canned pitch, skip the graph ────────────
            response_text = static_response(message)

            # Build a minimal state dict for logging
            state = {
                "user_input":      message,
                "response":        response_text,
                "confidence":      0.0,
                "objection":       {"label": "neutral", "confidence": 0.0, "triggers": []},
                "sentiment":       {"label": "neutral", "score": 0.0, "tone_instruction": ""},
                "persona":         {"label": "Unknown", "pitch_angle": ""},
                "strategy":        "static_pitch",
                "citations":       "",
                "should_handoff":  False,
                "handoff_trigger": "",
                "handoff_message": "",
                "retrieved_docs":  [],
                "variant":         "STATIC",
            }

            memory.add(role="user", content=message)
            memory.add(role="assistant", content=response_text)

            facts = memory.get_facts()
            await save_session(session_id, facts)

            explanation = ExplanationResponse(
                objection_reason="A/B test: STATIC variant — graph skipped.",
                persona_reason="A/B test: STATIC variant — graph skipped.",
                sentiment_reason="A/B test: STATIC variant — graph skipped.",
                strategy_reason="A/B test: STATIC variant — fixed pitch returned.",
                trigger_phrases=[],
                confidence_note="N/A for STATIC variant.",
                handoff_reason=None,
            )

            response = ChatResponse(
                response        = response_text,
                objection_label = "neutral",
                confidence      = 0.0,
                sentiment       = "neutral",
                persona         = "Unknown",
                strategy        = "static_pitch",
                citations       = "",
                should_handoff  = False,
                explanation     = explanation,
                retrieved_docs  = [],
                session_id      = session_id,
                memory_context  = memory.get_context_string(),
            )
        else:
            # ── ADAPTIVE branch: run the full graph pipeline ───────────────────
            state = run_graph(message, memory)
            state["variant"] = "ADAPTIVE"

            # When handoff triggered, use the handoff_message as the response.
            do_handoff = bool(state.get("should_handoff", False))
            if do_handoff:
                response_text = state.get("handoff_message") or state.get("response", "")
            else:
                response_text = state.get("response", "")

            exp_dict = explain(state)
            explanation = ExplanationResponse(
                objection_reason = exp_dict["objection_reason"],
                persona_reason   = exp_dict["persona_reason"],
                sentiment_reason = exp_dict["sentiment_reason"],
                strategy_reason  = exp_dict["strategy_reason"],
                trigger_phrases  = exp_dict["trigger_phrases"],
                confidence_note  = exp_dict["confidence_note"],
                handoff_reason   = exp_dict["handoff_reason"],
            )

            facts = memory.get_facts()
            persona_dict  = state.get("persona") or {}
            persona_label = persona_dict.get("label")
            if persona_label:
                facts["persona_label"] = persona_label

            await save_session(session_id, facts)

            objection_dict = state.get("objection") or {}
            sentiment_dict = state.get("sentiment") or {}

            retrieved_docs = [
                RetrievedDoc(
                    text        = d.get("text", ""),
                    source_file = d.get("source_file", ""),
                    chunk_index = d.get("chunk_index", -1),
                    score       = d.get("score", 0.0),
                )
                for d in (state.get("retrieved_docs") or [])
            ]

            response = ChatResponse(
                response        = response_text,
                objection_label = objection_dict.get("label", "neutral"),
                confidence      = float(state.get("confidence", 1.0)),
                sentiment       = sentiment_dict.get("label", "neutral"),
                persona         = persona_dict.get("label", "Unknown"),
                strategy        = state.get("strategy", "discovery_questions"),
                citations       = state.get("citations", ""),
                should_handoff  = do_handoff,
                explanation     = explanation,
                retrieved_docs  = retrieved_docs,
                session_id      = session_id,
                memory_context  = memory.get_context_string(),
            )

        # ── Log analytics event (fire-and-forget) ─────────────────────────────
        asyncio.create_task(
            log_event(session_id=session_id, state=state, did_convert=False)
        )

        return response

    except HTTPException:
        raise  # Re-raise 400/401/403 unchanged
    except Exception as exc:
        logger.exception("Error in POST /chat for session %s", session_id)
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while processing your request: {exc}",
        )


# ─── GET /session/{session_id} ────────────────────────────────────────────────

@router.get(
    "/session/{session_id}",
    response_model=SessionFactsResponse,
    summary="Retrieve the full persisted session facts for a customer from PostgreSQL.",
    description=(
        "Returns all extracted profile facts (company, persona, tools, objection "
        "history, budget signal) for the given session_id.\n\n"
        "**Required role**: `admin`.\n\n"
        "Returns `found=false` (HTTP 200) rather than 404 if no session exists, "
        "so callers can distinguish 'no data yet' from a genuine error."
    ),
    responses={
        400: {"description": "Invalid request — empty session_id."},
        401: {"description": "Missing or invalid Bearer token."},
        403: {"description": "Insufficient role. Requires admin."},
        500: {"description": "Internal server error during DB lookup."},
    },
)
async def get_session_facts(
    session_id: str = Path(
        ...,
        description="The unique session identifier used in POST /chat.",
        examples=["user_abc123", "conv_2024_001"],
    ),
    current_user: User = require_roles("admin"),
) -> SessionFactsResponse:
    session_id = session_id.strip()
    if not session_id:
        raise HTTPException(status_code=400, detail="`session_id` must be a non-empty string.")

    logger.info(
        "GET /session/%s | user=%s role=%s",
        session_id, current_user.email, current_user.role,
    )

    try:
        facts = await load_session(session_id)

        if not facts:
            # Session not found — return a valid response with found=False
            return SessionFactsResponse(
                session_id        = session_id,
                company_name      = None,
                persona_label     = None,
                tools_mentioned   = [],
                objections_raised = [],
                budget_signal     = None,
                found             = False,
            )

        return SessionFactsResponse(
            session_id        = session_id,
            company_name      = facts.get("company_name"),
            persona_label     = facts.get("persona_label"),
            tools_mentioned   = facts.get("tools_mentioned") or [],
            objections_raised = facts.get("objections_raised") or [],
            budget_signal     = facts.get("budget_signal"),
            found             = True,
        )

    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Error in GET /session/%s", session_id)
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while retrieving session facts: {exc}",
        )
