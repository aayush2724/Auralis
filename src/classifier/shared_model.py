import logging
from transformers import pipeline

import threading

logger = logging.getLogger("auralis.classifier.shared")

_pipeline = None
_lock = threading.Lock()


def get_zeroshot_pipeline():
    """
    Load the BART zero-shot pipeline exactly once in a thread-safe manner.
    """
    global _pipeline
    if _pipeline is None:
        with _lock:
            if _pipeline is None:
                logger.info(
                    "Loading shared zero-shot classifier: facebook/bart-large-mnli"
                )
                _pipeline = pipeline(
                    "zero-shot-classification",
                    model="facebook/bart-large-mnli",
                    device="cpu",
                    model_kwargs={"low_cpu_mem_usage": False},
                )
    return _pipeline
