"""
auralis/src/classifier/sentiment.py
──────────────────────────────────────
Sentiment classifier using DistilBERT fine-tuned on SST-2.

Model : distilbert-base-uncased-finetuned-sst-2-english
Labels: POSITIVE / NEGATIVE → mapped to positive / negative / neutral
         (neutral is inferred when the model's positive-score sits in the
          ambiguous band [0.40, 0.60], meaning it is uncertain either way)

Public API
----------
  analyze(text: str) -> SentimentResult

CLI smoke-test
--------------
  python -m src.classifier.sentiment "I love the product but it's a bit pricey"
"""

from __future__ import annotations

import logging
import sys
from functools import lru_cache
from typing import Literal, TypedDict

from transformers import pipeline

# ─── Logging ──────────────────────────────────────────────────────────────────

logger = logging.getLogger("auralis.classifier.sentiment")

# ─── Constants ────────────────────────────────────────────────────────────────

MODEL_NAME = "distilbert-base-uncased-finetuned-sst-2-english"

# If the POSITIVE score falls inside this band the utterance is treated as neutral.
_NEUTRAL_LOW  = 0.40
_NEUTRAL_HIGH = 0.60

# Tone instructions appended to the generation prompt downstream.
_TONE_INSTRUCTIONS: dict[str, str] = {
    "positive": "Match the customer energy, be enthusiastic.",
    "neutral":  "Stay professional and informative.",
    "negative": "Be empathetic, slow down, acknowledge frustration first.",
}


# ─── TypedDict ────────────────────────────────────────────────────────────────

class SentimentResult(TypedDict):
    """Return type of analyze()."""
    label:            Literal["positive", "neutral", "negative"]
    score:            float   # confidence of the mapped label (0.0–1.0)
    tone_instruction: str     # prompt suffix for the generation node


# ─── Model (lazy-loaded singleton) ────────────────────────────────────────────

@lru_cache(maxsize=1)
def _get_pipeline():
    """Load the DistilBERT SST-2 pipeline once and cache it."""
    logger.info("Loading sentiment model: %s", MODEL_NAME)
    return pipeline(
        "sentiment-analysis",
        model=MODEL_NAME,

        truncation=True,
        max_length=512,
    )


# ─── Mapping helper ───────────────────────────────────────────────────────────

def _map_to_sentiment(
    raw_label: str, positive_score: float
) -> tuple[Literal["positive", "neutral", "negative"], float]:
    """
    Map the binary SST-2 output to a three-way sentiment label.

    Logic
    -----
    - If positive_score ∈ [_NEUTRAL_LOW, _NEUTRAL_HIGH] → neutral
      score = distance from the mid-point (0.5), converted to a certainty signal
    - Else if raw_label == "POSITIVE" → positive, score = positive_score
    - Else                            → negative, score = 1 - positive_score
    """
    if _NEUTRAL_LOW <= positive_score <= _NEUTRAL_HIGH:
        # Certainty of "neutralness": how close to 0.5 (max certainty) the score is.
        certainty = 1.0 - abs(positive_score - 0.5) * 2  # 1.0 at 0.5, 0.0 at boundary
        return "neutral", round(certainty, 4)

    if raw_label.upper() == "POSITIVE":
        return "positive", round(positive_score, 4)

    return "negative", round(1.0 - positive_score, 4)


# ─── Public API ───────────────────────────────────────────────────────────────

def analyze(text: str) -> SentimentResult:
    """
    Analyze the sentiment of a sales utterance.

    Parameters
    ----------
    text : Prospect or sales-rep utterance to analyze.

    Returns
    -------
    SentimentResult with label, score, and tone_instruction.

    Raises
    ------
    ValueError : if *text* is empty or whitespace-only.
    """
    text = text.strip()
    if not text:
        raise ValueError("`text` must be a non-empty string.")

    clf = _get_pipeline()
    raw = clf(text)[0]          # {'label': 'POSITIVE'|'NEGATIVE', 'score': float}

    raw_label: str   = raw["label"]
    raw_score: float = raw["score"]

    # SST-2 always returns the score of the *predicted* class, not always positive.
    # Normalise: we always want the probability that the text is POSITIVE.
    positive_score = raw_score if raw_label.upper() == "POSITIVE" else 1.0 - raw_score

    label, score = _map_to_sentiment(raw_label, positive_score)
    tone_instruction = _TONE_INSTRUCTIONS[label]

    logger.debug(
        "analyze | label=%s score=%.3f raw=(%s, %.3f)",
        label, score, raw_label, raw_score,
    )

    return SentimentResult(
        label=label,
        score=score,
        tone_instruction=tone_instruction,
    )


# ─── CLI smoke-test ───────────────────────────────────────────────────────────

def _main() -> None:
    if len(sys.argv) < 2:
        print('Usage: python -m src.classifier.sentiment "<utterance>"')
        sys.exit(1)

    text = " ".join(sys.argv[1:])
    result = analyze(text)

    print(f"\n{'─'*60}")
    print(f"  Input            : {text}")
    print(f"  Label            : {result['label']}")
    print(f"  Score            : {result['score']:.1%}")
    print(f"  Tone instruction : {result['tone_instruction']}")
    print(f"{'─'*60}\n")


if __name__ == "__main__":
    _main()
