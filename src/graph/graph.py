"""
auralis/src/graph/graph.py
───────────────────────────
LangGraph conversation graph for Auralis.

Flow
----
START → classify_node → retrieve_node → strategy_node
      → generate_node → [conditional] → handoff_node → END
                                       ↘ END

Nodes
-----
  classify_node  — runs objection / sentiment / persona classifiers in parallel
  retrieve_node  — semantic retrieval + citation formatting
  strategy_node  — maps (objection × persona) → named strategy
  generate_node  — builds prompt and calls OpenAI
  handoff_node   — flags human escalation (Feature 7)

Exposed API
-----------
  run_graph(user_input: str, memory: ConversationMemory) -> GraphState
"""

from __future__ import annotations

import logging
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, TypedDict

# pyrefly: ignore [missing-import]
from langchain_openai import ChatOpenAI
# pyrefly: ignore [missing-import]
from langgraph.graph import END, START, StateGraph

from src.classifier.objection import ObjectionResult, classify
from src.classifier.persona import PersonaResult, detect
from src.classifier.sentiment import SentimentResult, analyze
from src.memory.memory import ConversationMemory
from src.rag.retriever import format_citations, retrieve

# ─── Logging ──────────────────────────────────────────────────────────────────

logger = logging.getLogger("auralis.graph")

# ─── LLM (lazy singleton) ─────────────────────────────────────────────────────

_llm: ChatOpenAI | None = None


def _get_llm() -> ChatOpenAI:
    global _llm
    if _llm is None:
        _llm = ChatOpenAI(
            model=os.getenv("LLM_MODEL", "gpt-4o"),
            temperature=float(os.getenv("LLM_TEMPERATURE", "0.2")),
            max_tokens=int(os.getenv("LLM_MAX_TOKENS", "1024")),
        )
    return _llm


# ─── Strategy map ─────────────────────────────────────────────────────────────
# Primary key: objection label.  Secondary key: persona label (optional override).
# Values are human-readable strategy module names used by generate_node.

_STRATEGY_MAP: dict[str, dict[str, str]] = {
    "price": {
        "_default": "value_reframe",
        "CEO":      "roi_business_case",
        "Founder":  "roi_business_case",
        "CTO":      "value_reframe",
    },
    "trust": {
        "_default": "social_proof",
        "CTO":      "technical_proof",
        "Developer": "technical_proof",
    },
    "timing": {
        "_default": "urgency_creation",
        "CEO":      "strategic_timing",
        "Founder":  "strategic_timing",
    },
    "competitor": {
        "_default": "competitive_differentiation",
        "Developer": "technical_differentiation",
        "CTO":       "technical_differentiation",
    },
    "fit": {
        "_default": "needs_discovery",
        "Product_Manager": "use_case_mapping",
    },
    "buying_signal": {
        "_default": "closing_accelerator",
    },
    "neutral": {
        "_default": "discovery_questions",
    },
}

# Handoff thresholds (Feature 7)
_HANDOFF_LOW_CONFIDENCE = 0.40
_HANDOFF_NEGATIVE_SCORE = 0.85


# ─── GraphState ───────────────────────────────────────────────────────────────

class GraphState(TypedDict, total=False):
    """Shared mutable state passed between every node in the graph."""
    user_input:     str
    objection:      ObjectionResult
    sentiment:      SentimentResult
    persona:        PersonaResult
    retrieved_docs: list[dict]
    citations:      str
    memory_context: str
    strategy:       str
    response:       str
    confidence:     float
    should_handoff: bool
    metadata:       dict[str, Any]


# ─── Node: classify ───────────────────────────────────────────────────────────

def classify_node(state: GraphState) -> dict[str, Any]:
    """
    Run objection, sentiment, and persona classifiers in parallel.
    Returns partial state update.
    """
    text = state["user_input"]
    logger.info("[classify_node] text='%s'", text[:80])

    results: dict[str, Any] = {}

    # Run three independent classifiers concurrently
    with ThreadPoolExecutor(max_workers=3, thread_name_prefix="auralis-clf") as pool:
        futures = {
            pool.submit(classify, text): "objection",
            pool.submit(analyze,  text): "sentiment",
            pool.submit(detect,   text): "persona",
        }
        for future in as_completed(futures):
            key = futures[future]
            try:
                results[key] = future.result()
            except Exception as exc:
                logger.error("[classify_node] %s classifier failed: %s", key, exc, exc_info=True)
                raise

    objection: ObjectionResult = results["objection"]
    sentiment: SentimentResult = results["sentiment"]
    persona:   PersonaResult   = results["persona"]

    logger.info(
        "[classify_node] objection=%s(%.2f) sentiment=%s persona=%s",
        objection["label"], objection["confidence"],
        sentiment["label"], persona["label"],
    )

    return {
        "objection":  objection,
        "sentiment":  sentiment,
        "persona":    persona,
        "confidence": objection["confidence"],
        "metadata": {
            "pitch_angle":      persona["pitch_angle"],
            "objection_triggers": objection["triggers"],
            "tone_instruction": sentiment["tone_instruction"],
        },
    }


# ─── Node: retrieve ───────────────────────────────────────────────────────────

def retrieve_node(state: GraphState) -> dict[str, Any]:
    """
    Build a targeted query from user_input + objection label, then retrieve
    matching docs from the FAISS knowledge base.
    """
    user_input = state["user_input"]
    objection  = state.get("objection", {})
    obj_label  = objection.get("label", "")

    # Enrich query with the objection class for better retrieval precision
    query = f"{user_input} {obj_label} objection handling" if obj_label else user_input
    logger.info("[retrieve_node] query='%s'", query[:100])

    try:
        docs     = retrieve(query, top_k=5)
        citations = format_citations(docs)
    except FileNotFoundError:
        logger.warning("[retrieve_node] FAISS index not found — proceeding without retrieval.")
        docs      = []
        citations = ""

    logger.info("[retrieve_node] %d docs retrieved", len(docs))
    return {
        "retrieved_docs": docs,
        "citations":      citations,
    }


# ─── Node: strategy ───────────────────────────────────────────────────────────

def strategy_node(state: GraphState) -> dict[str, Any]:
    """
    Select the named strategy module based on (objection × persona).

    Falls back to the objection-level default if no persona override exists.
    """
    obj_label    = state.get("objection", {}).get("label", "neutral")
    persona_label = state.get("persona",   {}).get("label", "Unknown")

    persona_map = _STRATEGY_MAP.get(obj_label, {"_default": "discovery_questions"})
    strategy    = persona_map.get(persona_label) or persona_map.get("_default", "discovery_questions")

    logger.info(
        "[strategy_node] objection=%s persona=%s → strategy=%s",
        obj_label, persona_label, strategy,
    )

    # Merge competitor name into metadata if applicable
    meta_update: dict[str, Any] = {}
    if obj_label == "competitor":
        triggers = state.get("objection", {}).get("triggers", [])
        meta_update["competitor_mentioned"] = triggers[0] if triggers else "unknown"

    current_meta = dict(state.get("metadata") or {})
    current_meta.update(meta_update)

    return {
        "strategy": strategy,
        "metadata": current_meta,
    }


# ─── Node: generate ───────────────────────────────────────────────────────────

_SYSTEM_PROMPT = """\
You are Auralis, an adaptive AI sales assistant. Your role is to help sales
representatives handle prospect objections intelligently and close more deals.

Guidelines:
- Be concise, confident, and empathetic.
- Never fabricate statistics; cite only information from the retrieved context.
- Always match the tone instruction provided.
- Tailor your pitch angle to the prospect's role.
- End with a soft, open-ended follow-up question to keep the conversation going.
"""


def generate_node(state: GraphState) -> dict[str, Any]:
    """
    Dispatch to the strategy router to build a specialised prompt, then call
    the LLM. Citations are appended if not already embedded in the response.

    The router maps state.objection.label → strategy module → build_prompt(),
    so each objection class gets its own carefully structured prompt rather
    than a single generic template.
    """
    # Late import avoids circular dependency at module load time
    # (strategies import GraphState from this module).
    from src.strategies.router import get_strategy_prompt  # noqa: PLC0415

    citations = state.get("citations") or ""

    logger.info(
        "[generate_node] strategy=%s | label=%s",
        state.get("strategy"),
        (state.get("objection") or {}).get("label", "?"),
    )

    # Build the specialised user-turn prompt via the strategy router
    user_prompt = get_strategy_prompt(state)

    llm = _get_llm()
    # pyrefly: ignore [missing-import]
    from langchain_core.messages import HumanMessage, SystemMessage  # noqa: PLC0415
    messages = [
        SystemMessage(content=_SYSTEM_PROMPT),
        HumanMessage(content=user_prompt),
    ]
    ai_msg = llm.invoke(messages)
    response_text: str = ai_msg.content

    # Append citations block if the strategy prompt didn't embed them
    if citations and citations not in response_text:
        response_text = response_text.rstrip() + f"\n\n---\n**Sources**\n{citations}"

    logger.info("[generate_node] response length=%d chars", len(response_text))
    return {"response": response_text}


# ─── Node: handoff ────────────────────────────────────────────────────────────

def handoff_node(state: GraphState) -> dict[str, Any]:
    """
    Feature 7 — Human Handoff trigger.

    Fires when:
      - objection confidence < 0.40 (model is unsure, safer to escalate), OR
      - sentiment is negative with score > 0.85 (highly frustrated prospect)

    Sets should_handoff=True and appends a handoff notice to the response.
    """
    logger.info("[handoff_node] escalating to human agent.")
    current_response = state.get("response", "")
    notice = (
        "\n\n---\n"
        "⚠️  **Escalation notice**: This conversation has been flagged for "
        "human review. A senior sales representative will follow up shortly."
    )
    return {
        "should_handoff": True,
        "response": current_response + notice,
    }


# ─── Conditional router ───────────────────────────────────────────────────────

def _should_handoff(state: GraphState) -> str:
    """
    Router called after generate_node.
    Returns 'handoff' or 'end' to control the conditional edge.
    """
    confidence = state.get("confidence", 1.0)
    sentiment  = state.get("sentiment") or {}
    s_label    = sentiment.get("label", "")
    s_score    = sentiment.get("score", 0.0)

    if confidence < _HANDOFF_LOW_CONFIDENCE:
        logger.info("[router] handoff: low confidence %.2f", confidence)
        return "handoff"

    if s_label == "negative" and s_score > _HANDOFF_NEGATIVE_SCORE:
        logger.info("[router] handoff: high-negative sentiment %.2f", s_score)
        return "handoff"

    return "end"


# ─── Graph compilation ────────────────────────────────────────────────────────

def _build_graph() -> StateGraph:
    builder = StateGraph(GraphState)

    # Register nodes
    builder.add_node("classify_node",  classify_node)
    builder.add_node("retrieve_node",  retrieve_node)
    builder.add_node("strategy_node",  strategy_node)
    builder.add_node("generate_node",  generate_node)
    builder.add_node("handoff_node",   handoff_node)

    # Linear backbone
    builder.add_edge(START,           "classify_node")
    builder.add_edge("classify_node", "retrieve_node")
    builder.add_edge("retrieve_node", "strategy_node")
    builder.add_edge("strategy_node", "generate_node")

    # Conditional branch after generation
    builder.add_conditional_edges(
        "generate_node",
        _should_handoff,
        {
            "handoff": "handoff_node",
            "end":     END,
        },
    )

    # Handoff always terminates
    builder.add_edge("handoff_node", END)

    return builder


# Compiled graph (module-level singleton)
_graph = _build_graph().compile()


# ─── Public API ───────────────────────────────────────────────────────────────

def run_graph(user_input: str, memory: ConversationMemory) -> GraphState:
    """
    Execute the full Auralis conversation graph for a single user turn.

    Parameters
    ----------
    user_input : The prospect's latest message.
    memory     : Live ConversationMemory instance for this session.

    Returns
    -------
    Final GraphState after all nodes have executed.

    Side-effects
    ------------
    - Adds the user turn + objection metadata to *memory*.
    - Adds the assistant response to *memory*.
    """
    if not user_input or not user_input.strip():
        raise ValueError("`user_input` must be a non-empty string.")

    # Seed the initial state
    initial_state: GraphState = {
        "user_input":     user_input.strip(),
        "memory_context": memory.get_context_string(),
        "should_handoff": False,
        "metadata":       {},
    }

    logger.info("run_graph | input='%s'", user_input[:80])

    final_state: GraphState = _graph.invoke(initial_state)

    # Persist this turn into memory (with objection metadata for fact extraction)
    memory.add(
        role="user",
        content=user_input,
        metadata={"objection": final_state.get("objection")},
    )
    memory.add(
        role="assistant",
        content=final_state.get("response", ""),
    )

    return final_state
