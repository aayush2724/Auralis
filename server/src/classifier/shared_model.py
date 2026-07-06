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
    label_index: int = Field(description="The 0-based index of the most appropriate label from the candidate list.")
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
            "Classify the following text into exactly one of these categories, identified by their 0-based index:\n"
            "{candidate_labels}\n\n"
            "Text to classify: {text}\n\n"
            "Select the best matching label_index (an integer) and provide a confidence score (0.0-1.0)."
        )

    def __call__(self, text: str, candidate_labels: list[str], **kwargs) -> dict[str, Any]:
        try:
            # format candidate labels with their index
            formatted_labels = "\n".join([f"{i}: {label}" for i, label in enumerate(candidate_labels)])
            chain = self.prompt | self.llm
            result: ClassificationOutput = chain.invoke({
                "candidate_labels": formatted_labels,
                "text": text
            })
            idx = result.label_index if 0 <= result.label_index < len(candidate_labels) else 0
            label = candidate_labels[idx]
            score = result.confidence
        except Exception as e:
            logger.error(f"LLM Classification failed: {e}")
            label = candidate_labels[0]
            score = 0.5
            
        return {
            "labels": [label],
            "scores": [score]
        }

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
