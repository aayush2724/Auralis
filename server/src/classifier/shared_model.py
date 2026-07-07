import logging
import os
from typing import Any
from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate

import threading

logger = logging.getLogger("auralis.classifier.shared")

_classifier = None
_lock = threading.Lock()


class ClassificationOutput(BaseModel):
    label_index: int = Field(
        description="The 0-based index of the most appropriate label from the candidate list."
    )
    confidence: float = Field(description="Confidence score between 0.0 and 1.0.")


class LLMZeroShotClassifier:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model=os.environ.get("GEMINI_MODEL", "gemini-2.0-flash"),
            temperature=0,
            google_api_key=os.getenv("GEMINI_API_KEY"),
        ).with_structured_output(ClassificationOutput)
        self.prompt = PromptTemplate.from_template(
            "You are an expert sales conversation analyst.\n"
            "Classify the following sales text into exactly one of these categories (by 0-based index).\n"
            "Read the description carefully before choosing:\n\n"
            "{candidate_labels}\n\n"
            "Text to classify: {text}\n\n"
            "Pick the single best-matching label_index and provide a confidence score (0.0-1.0)."
        )

    def __call__(
        self,
        text: str,
        candidate_labels: list[str],
        descriptions: list[str] | None = None,
        **kwargs,
    ) -> dict[str, Any]:
        import time

        max_retries = 3
        for attempt in range(max_retries):
            try:
                # Format labels with optional descriptions for better LLM accuracy
                if descriptions and len(descriptions) == len(candidate_labels):
                    formatted_labels = "\n".join(
                        [
                            f"{i}: {label} — {desc}"
                            for i, (label, desc) in enumerate(
                                zip(candidate_labels, descriptions)
                            )
                        ]
                    )
                else:
                    formatted_labels = "\n".join(
                        [f"{i}: {label}" for i, label in enumerate(candidate_labels)]
                    )
                chain = self.prompt | self.llm
                result: ClassificationOutput = chain.invoke(
                    {"candidate_labels": formatted_labels, "text": text}
                )
                idx = (
                    result.label_index
                    if 0 <= result.label_index < len(candidate_labels)
                    else 0
                )
                label = candidate_labels[idx]
                score = result.confidence
                return {"labels": [label], "scores": [score]}
            except Exception as e:
                err_str = str(e)
                if "RESOURCE_EXHAUSTED" in err_str or "429" in err_str:
                    wait = 15 * (attempt + 1)  # 15s, 30s, 45s
                    logger.warning(
                        f"Rate limited by Gemini API, retrying in {wait}s (attempt {attempt + 1}/{max_retries})"
                    )
                    time.sleep(wait)
                else:
                    logger.error(f"LLM Classification failed: {e}")
                    break

        # Final fallback after all retries exhausted
        logger.error("All retries exhausted, returning fallback label")
        return {"labels": [candidate_labels[0]], "scores": [0.5]}


def get_zeroshot_pipeline():
    """
    Load the Gemini LLM classifier in a thread-safe manner.
    Retains the get_zeroshot_pipeline name for backwards compatibility.
    """
    global _classifier
    if _classifier is None:
        with _lock:
            if _classifier is None:
                logger.info("Loading shared LLM classifier (Gemini)")
                _classifier = LLMZeroShotClassifier()
    return _classifier
