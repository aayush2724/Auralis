"""
auralis/src/handoff/handoff.py
──────────────────────────────
Handoff evaluation logic for Auralis — determines when to escalate to a
human agent and provides a user-facing handoff message.

Triggers
--------
  LOW_CONFIDENCE   : classifier confidence < 0.40
  ANGRY_CUSTOMER   : negative sentiment with score > 0.88
  USER_REQUESTED   : user explicitly asks for a human

Public API
----------
  evaluate_handoff(state, user_input) -> HandoffDecision
"""

from __future__ import annotations

import logging
from enum import Enum
from typing import Any, TypedDict

logger = logging.getLogger("auralis.handoff")


class HandoffTrigger(str, Enum):
    """Reason for escalating to a human agent."""
    LOW_CONFIDENCE   = "LOW_CONFIDENCE"
    ANGRY_CUSTOMER   = "ANGRY_CUSTOMER"
    USER_REQUESTED   = "USER_REQUESTED"


class HandoffDecision(TypedDict):
    """Result of handoff evaluation."""
    should_handoff:   bool
    trigger:          HandoffTrigger | None
    handoff_message:  str


# ─── Thresholds ───────────────────────────────────────────────────────────────

_LOW_CONFIDENCE_THRESHOLD  = 0.40
_ANGRY_SENTIMENT_THRESHOLD = 0.88

# Phrases that signal the user wants a human
_HUMAN_REQUEST_PHRASES: tuple[str, ...] = (
    "talk to human",
    "talk to a human",
    "real person",
    "speak to someone",
    "speak to a human",
    "human agent",
    "talk to a rep",
    "talk to a sales rep",
    "connect me to",
    "transfer me to",
    "let me talk to",
)


# ─── Handoff messages ─────────────────────────────────────────────────────────

_HANDOFF_MESSAGES: dict[HandoffTrigger, str] = {
    HandoffTrigger.LOW_CONFIDENCE: (
        "I want to make sure I give you accurate information. "
        "Let me connect you with a specialist who can help directly. "
        "[Connecting to human agent...]"
    ),
    HandoffTrigger.ANGRY_CUSTOMER: (
        "I hear you, and I am sorry this has been frustrating. "
        "Let me get someone from our team to assist you right now. "
        "[Escalating...]"
    ),
    HandoffTrigger.USER_REQUESTED: (
        "Absolutely — let me get you connected with a member of our team "
        "who can help you right away. [Connecting to human agent...]"
    ),
}


# ─── Public API ───────────────────────────────────────────────────────────────

def evaluate_handoff(
    state: dict[str, Any],
    user_input: str,
) -> HandoffDecision:
    """
    Evaluate whether this conversation should be escalated to a human agent.

    Checks three trigger conditions in priority order:
      1. USER_REQUESTED  — explicit ask (checked first, highest priority)
      2. ANGRY_CUSTOMER — negative sentiment above threshold
      3. LOW_CONFIDENCE  — classifier unsure

    Parameters
    ----------
    state     : Current GraphState from the conversation graph.
    user_input : The prospect's latest message text.

    Returns
    -------
    HandoffDecision with should_handoff, trigger, and handoff_message.
    """
    # ── Check USER_REQUESTED first (highest priority) ─────────────────────
    user_lower = user_input.lower()
    for phrase in _HUMAN_REQUEST_PHRASES:
        if phrase in user_lower:
            msg = _HANDOFF_MESSAGES[HandoffTrigger.USER_REQUESTED]
            logger.info(
                "[evaluate_handoff] trigger=USER_REQUESTED phrase='%s'", phrase,
            )
            return HandoffDecision(
                should_handoff=True,
                trigger=HandoffTrigger.USER_REQUESTED,
                handoff_message=msg,
            )

    # ── Check ANGRY_CUSTOMER ─────────────────────────────────────────────
    sentiment = state.get("sentiment") or {}
    s_label = sentiment.get("label", "")
    s_score = sentiment.get("score", 0.0)

    if s_label == "negative" and s_score > _ANGRY_SENTIMENT_THRESHOLD:
        msg = _HANDOFF_MESSAGES[HandoffTrigger.ANGRY_CUSTOMER]
        logger.info(
            "[evaluate_handoff] trigger=ANGRY_CUSTOMER score=%.2f", s_score,
        )
        return HandoffDecision(
            should_handoff=True,
            trigger=HandoffTrigger.ANGRY_CUSTOMER,
            handoff_message=msg,
        )

    # ── Check LOW_CONFIDENCE ─────────────────────────────────────────────
    confidence = state.get("confidence", 1.0)

    if confidence < _LOW_CONFIDENCE_THRESHOLD:
        msg = _HANDOFF_MESSAGES[HandoffTrigger.LOW_CONFIDENCE]
        logger.info(
            "[evaluate_handoff] trigger=LOW_CONFIDENCE confidence=%.2f", confidence,
        )
        return HandoffDecision(
            should_handoff=True,
            trigger=HandoffTrigger.LOW_CONFIDENCE,
            handoff_message=msg,
        )

    # ── No trigger — continue conversation ───────────────────────────────
    return HandoffDecision(
        should_handoff=False,
        trigger=None,
        handoff_message="",
    )
