from functools import lru_cache
import logging
from transformers import pipeline

logger = logging.getLogger("auralis.classifier.shared")

@lru_cache(maxsize=1)
def get_zeroshot_pipeline():
    """
    Load the BART zero-shot pipeline exactly once and share it across
    objection, persona, and competitor classifiers to save ~3.2GB of RAM.
    """
    logger.info("Loading shared zero-shot classifier: facebook/bart-large-mnli")
    return pipeline(
        "zero-shot-classification",
        model="facebook/bart-large-mnli"
    )
