"""
auralis/src/utils/explainability.py
─────────────────────────────────────
Explainability layer for Auralis — Feature 9.

Builds a human-readable audit trail of every model decision from the
GraphState, so sales reps (and QA engineers) can understand *why* Auralis
chose a particular strategy and response tone.

Public API
──────────
  explain(state: GraphState) -> ExplanationResult

ExplanationResult TypedDict fields
────────────────────────────────────
  objection_reason  : str          why this objection class was chosen
  persona_reason    : str          why this persona was identified
  sentiment_reason  : str          what the detected tone implies
  strategy_reason   : str          why this strategy was selected
  trigger_phrases   : list[str]    raw phrases that fired the objection class
  confidence_note   : str          warning if confidence is low
  handoff_reason    : str | None   why handoff was triggered (if applicable)
"""

from __future__ import annotations

from typing import TypedDict

from src.graph.graph import GraphState

# ─── Strategy explanations ────────────────────────────────────────────────────
# Describes the (objection × persona) → strategy decision in plain English.

_STRATEGY_EXPLANATIONS: dict[str, dict[str, str]] = {
    "price": {
        "CEO":      "price + CEO = ROI business case is more persuasive than discounting; executives respond to financial impact, not feature lists.",
        "Founder":  "price + Founder = ROI and unit economics framing; founders need to see payback period, not just list price.",
        "CTO":      "price + CTO = value reframe with architecture context; CTOs justify cost through technical capability, not headline price.",
        "_default": "price objection requires reframing cost as investment; generic value reframe applied.",
    },
    "trust": {
        "CTO":       "price + CTO = technical proof (benchmarks, SLAs, security docs) is more credible to engineers than testimonials.",
        "Developer": "trust + Developer = technical proof including API uptime, docs quality, and open-source contributions.",
        "_default":  "trust objection requires social proof (case studies, references, guarantees); applied social proof strategy.",
    },
    "timing": {
        "CEO":      "timing + CEO = strategic timing framing; connecting delay cost to board-level metrics and planning cycles.",
        "Founder":  "timing + Founder = market-window urgency; first-mover advantage and competitive risk of waiting.",
        "_default": "timing objection requires urgency creation with a low-friction next step to fit their current window.",
    },
    "competitor": {
        "Developer":  "competitor + Developer = technical differentiation; API quality, SDK maturity, and developer experience are the battleground.",
        "CTO":        "competitor + CTO = technical differentiation; architecture, scalability, and integration depth.",
        "_default":   "competitor objection requires respectful differentiation and a parallel pilot proposal.",
    },
    "fit": {
        "Product_Manager": "fit + PM = use-case mapping; PMs respond to feature-to-outcome alignment on their specific roadmap.",
        "_default":        "fit objection requires discovery questions to surface the real gap before proposing solutions.",
    },
    "buying_signal": {
        "_default": "buying signal detected; applied closing accelerator to remove friction and accelerate commitment.",
    },
    "neutral": {
        "_default": "no clear objection detected; applied discovery questions to surface underlying concerns.",
    },
}

# ─── Sentiment explanations ────────────────────────────────────────────────────

_SENTIMENT_EXPLANATIONS: dict[str, str] = {
    "positive":  "Customer appears engaged and receptive. {tone} Energy-matching tone applied to maintain momentum.",
    "neutral":   "Customer tone is measured and factual. {tone} Professional, informative tone applied.",
    "negative":  "Customer appears frustrated or resistant. {tone} Empathetic, slow-paced tone applied; response prioritises acknowledgement over persuasion.",
}

# ─── Confidence thresholds ────────────────────────────────────────────────────

_LOW_CONFIDENCE  = 0.50
_VERY_LOW_CONF   = 0.35


# ─── TypedDict ────────────────────────────────────────────────────────────────

class ExplanationResult(TypedDict):
    """Human-readable audit trail of every model decision in the graph."""
    objection_reason: str          # why this objection class was chosen
    persona_reason:   str          # why this persona was identified
    sentiment_reason: str          # what the detected tone implies
    strategy_reason:  str          # why this strategy was selected
    trigger_phrases:  list[str]    # raw phrases from ObjectionResult.triggers
    confidence_note:  str          # warning if confidence is low / empty if fine
    handoff_reason:   str | None   # why handoff was triggered (None if not triggered)


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _objection_reason(objection: dict) -> str:
    """
    Build a sentence explaining why the objection classifier chose this label.

    Example
    -------
    'Detected price objection (confidence 94%) because the customer said:
     ["too expensive", "out of budget"].'
    """
    label      = objection.get("label", "unknown")
    confidence = objection.get("confidence", 0.0)
    triggers   = objection.get("triggers", [])

    trigger_str = (
        f': ["{chr(34).join(f"{t}" for t in triggers[:5])}"]'
        if triggers
        else " with no explicit trigger phrases captured"
    )

    # Format trigger list cleanly
    if triggers:
        quoted = ", ".join(f'"{t}"' for t in triggers[:5])
        trigger_str = f": [{quoted}]"
    else:
        trigger_str = " with no explicit trigger phrases captured"

    return (
        f'Detected {label} objection (confidence {confidence:.0%}) '
        f'because the customer said{trigger_str}.'
    )


def _persona_reason(persona: dict, objection: dict) -> str:
    """
    Build a sentence explaining why this persona was identified.

    Example
    -------
    'Identified CTO (confidence 82%) because of technical framing:
     ["integration", "architecture"].'
    """
    label      = persona.get("label", "Unknown")
    confidence = persona.get("confidence", 0.0)

    # Surface objection trigger phrases as evidence for persona, since they
    # often contain role-specific vocabulary ("integration", "API", "board").
    triggers   = objection.get("triggers", [])

    if triggers:
        quoted = ", ".join(f'"{t}"' for t in triggers[:4])
        phrase_str = f" because of domain-specific framing: [{quoted}]"
    else:
        phrase_str = " based on the overall linguistic pattern of the message"

    pitch = persona.get("pitch_angle", "")
    pitch_note = f" Recommended pitch angle: {pitch}" if pitch else ""

    return (
        f'Identified {label} persona (confidence {confidence:.0%})'
        f'{phrase_str}.{pitch_note}'
    )


def _sentiment_reason(sentiment: dict) -> str:
    """
    Build a sentence explaining what the detected sentiment implies.

    Example
    -------
    'Customer appears frustrated because sentiment score is 0.91 negative.
     Empathetic tone applied.'
    """
    label = sentiment.get("label", "neutral")
    score = sentiment.get("score", 0.0)
    tone  = sentiment.get("tone_instruction", "")

    template = _SENTIMENT_EXPLANATIONS.get(label, _SENTIMENT_EXPLANATIONS["neutral"])
    return template.format(tone=f'Tone instruction: "{tone}".' if tone else "")


def _strategy_reason(objection: dict, persona: dict, strategy: str) -> str:
    """
    Build a sentence explaining why this strategy was chosen for
    the (objection × persona) combination.

    Example
    -------
    'Applied trust strategy because price + CTO = ROI framing is more
     effective than discounting.'
    """
    obj_label     = objection.get("label", "neutral")
    persona_label = persona.get("label", "Unknown")

    persona_map    = _STRATEGY_EXPLANATIONS.get(obj_label, {})
    explanation    = (
        persona_map.get(persona_label)
        or persona_map.get("_default")
        or f"Applied {strategy} for {obj_label} objection."
    )

    return f'Applied {strategy} because {explanation}'


def _confidence_note(objection: dict, sentiment: dict) -> str:
    """Return a warning string if any score is below safe thresholds."""
    obj_conf = objection.get("confidence", 1.0)
    notes: list[str] = []

    if obj_conf < _VERY_LOW_CONF:
        notes.append(
            f"⚠ Very low objection confidence ({obj_conf:.0%}) — "
            "classification is uncertain. Human review recommended."
        )
    elif obj_conf < _LOW_CONFIDENCE:
        notes.append(
            f"⚡ Low objection confidence ({obj_conf:.0%}) — "
            "response may not be optimally targeted."
        )

    s_label = sentiment.get("label", "neutral")
    s_score = sentiment.get("score", 0.0)
    if s_label == "negative" and s_score > 0.85:
        notes.append(
            f"⚠ High-frustration signal (negative sentiment score {s_score:.0%}) — "
            "escalation may be appropriate."
        )

    return " ".join(notes)


def _handoff_reason(state: GraphState) -> str | None:
    """Return a human-readable handoff explanation, or None."""
    if not state.get("should_handoff"):
        return None

    obj_conf  = (state.get("objection") or {}).get("confidence", 1.0)
    sentiment = state.get("sentiment") or {}
    s_label   = sentiment.get("label", "")
    s_score   = sentiment.get("score", 0.0)

    reasons: list[str] = []
    if obj_conf < 0.40:
        reasons.append(f"low classifier confidence ({obj_conf:.0%})")
    if s_label == "negative" and s_score > 0.85:
        reasons.append(f"high frustration signal ({s_score:.0%} negative sentiment)")

    if reasons:
        return f"Human handoff triggered due to: {' and '.join(reasons)}."
    return "Human handoff triggered (threshold condition met)."


# ─── Public API ───────────────────────────────────────────────────────────────

def explain(state: GraphState) -> ExplanationResult:
    """
    Build a human-readable audit trail for every model decision in the graph.

    Parameters
    ----------
    state : Completed GraphState (after all nodes have run).

    Returns
    -------
    ExplanationResult with a plain-English explanation for each decision.
    """
    objection = state.get("objection") or {}
    sentiment = state.get("sentiment") or {}
    persona   = state.get("persona")   or {}
    strategy  = state.get("strategy")  or "unknown"

    return ExplanationResult(
        objection_reason = _objection_reason(objection),
        persona_reason   = _persona_reason(persona, objection),
        sentiment_reason = _sentiment_reason(sentiment),
        strategy_reason  = _strategy_reason(objection, persona, strategy),
        trigger_phrases  = list(objection.get("triggers", [])),
        confidence_note  = _confidence_note(objection, sentiment),
        handoff_reason   = _handoff_reason(state),
    )
