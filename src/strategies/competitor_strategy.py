"""
auralis/src/strategies/competitor_strategy.py
───────────────────────────────────────────────
Strategy: Competitive Differentiation
Objection: competitor — "we already use X", "we're evaluating Y", "X is cheaper"

Approach
--------
1. Respect the existing relationship — never disparage the competitor.
2. Pull competitor-specific intel from the vectorstore using the competitor
   name from state.metadata['competitor_mentioned'].
3. Run a feature-level comparison: Auralis vs competitor, point by point.
4. Highlight switching ease (data export, migration support, onboarding time).
5. Propose a side-by-side evaluation / bake-off as the next step.

Features implemented
--------------------
  Feature  2 — Tone Adaptation  (tone_instruction)
  Feature 11 — Source Citations  (citations)
  Feature 13 — Role-Based Pitch  (pitch_angle)
"""

from __future__ import annotations

from src.graph.graph import GraphState


_PROMPT_TEMPLATE = """\
## AURALIS — Competitor Objection Strategy: Differentiation

### Conversation Facts
{memory_context}

### Prospect Message
{user_input}

### Analysis
- Objection          : competitor (confidence {confidence:.0%})
- Competitor detected: {competitor_name}
- Prospect Persona   : {persona_label}
- Sentiment          : {sentiment_label}
- Trigger phrases    : {triggers}

### Role-Based Framing (Feature 13)
{pitch_angle}

### Tone Instruction (Feature 2)
{tone_instruction}

### Retrieved Competitive Intel
{knowledge}

### Strategy Instructions
You are handling a COMPETITOR objection (vs. {competitor_name}).
Follow this exact structure — NEVER badmouth the competitor:

1. **Respect the Relationship** — One sentence acknowledging their investment.
   Example: "A lot of great teams run on {competitor_name} — it makes sense
   you've built workflows around it."

2. **Targeted Feature Comparison** — 3 bullet points, maximum:
   For each, use the format:
     • [Feature Area]: {competitor_name} does X. Auralis does Y → Benefit.
   Draw facts from the retrieved intel above.
   Frame through {pitch_angle}

3. **Switching Ease**
   - Migration timeline (e.g., "most teams are fully live in 2 weeks").
   - Data portability (CSV/API export from {competitor_name}).
   - Dedicated onboarding engineer included.

4. **Evaluation Proposal**
   - Propose a parallel pilot or bake-off: "Run Auralis alongside {competitor_name}
     for 30 days — no disruption to your current workflow."

5. **Soft Close**
   - "What would a fair evaluation look like for your team?"

### Source Citations (Feature 11)
{citations}

Write the complete sales response now, following the structure above.
Keep it under 230 words. Apply {sentiment_label} tone.
"""


def build_prompt(state: GraphState) -> str:
    objection   = state.get("objection")   or {}
    sentiment   = state.get("sentiment")   or {}
    persona     = state.get("persona")     or {}
    metadata    = state.get("metadata")    or {}
    docs        = state.get("retrieved_docs") or []

    # Competitor name — prefer the metadata extracted by strategy_node,
    # then fall back to trigger phrases, then generic.
    competitor_name = (
        metadata.get("competitor_mentioned")
        or metadata.get("competitor_name")
        or (objection.get("triggers") or ["the competitor"])[0]
        or "the incumbent tool"
    )

    knowledge_block = "\n\n".join(
        f"[{i+1}] {d['text'][:400]}" for i, d in enumerate(docs)
    ) or f"No specific intel on {competitor_name} retrieved — use general differentiation messaging."

    return _PROMPT_TEMPLATE.format(
        memory_context  = state.get("memory_context") or "No prior context.",
        user_input      = state.get("user_input", ""),
        confidence      = objection.get("confidence", 0.0),
        competitor_name = competitor_name,
        persona_label   = persona.get("label", "Unknown"),
        sentiment_label = sentiment.get("label", "neutral"),
        triggers        = ", ".join(objection.get("triggers", [])) or "none",
        pitch_angle     = metadata.get("pitch_angle") or persona.get("pitch_angle", ""),
        tone_instruction= metadata.get("tone_instruction") or sentiment.get("tone_instruction", ""),
        knowledge       = knowledge_block,
        citations       = state.get("citations") or "No citations available.",
    )
