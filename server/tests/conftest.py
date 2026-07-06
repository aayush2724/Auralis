"""
conftest.py
──────────────────────────────────────────────────────────────────
Pytest configuration: load .env before any tests run so that
GEMINI_API_KEY and DATABASE_URL are available to the application code.
"""
from __future__ import annotations

import os
from pathlib import Path

# Load the .env file from the project root (two levels up from server/tests/)
_dotenv_path = Path(__file__).parent.parent.parent / ".env"

try:
    from dotenv import load_dotenv
    load_dotenv(dotenv_path=_dotenv_path, override=False)
except ImportError:
    pass  # python-dotenv not installed; rely on env vars being set externally

import pytest
from unittest.mock import patch

# Apply global mocks immediately if USE_MOCK_LLM is enabled.
if os.getenv("USE_MOCK_LLM", "").lower() in ("1", "true", "yes"):
    
    from src.classifier.shared_model import LLMZeroShotClassifier
    def fake_classify(self, text: str, candidate_labels: list[str], **kwargs):
        t = (text or "").lower()
        
        if candidate_labels and ("competitor" in candidate_labels or "price" in candidate_labels):
            if "hubspot" in t or "hub spot" in t or "competitor" in t or "pipedrive" in t or "salesforce" in t:
                label = "competitor"
            elif "time" in t or "quarter" in t:
                label = "timing"
            elif "heard" in t or "case studies" in t or "prove" in t:
                label = "trust"
            elif "complex" in t or "workflow" in t or "fit" in t or "integrate" in t:
                label = "fit"
            elif "trial" in t or "demo" in t or "buy" in t or "interested" in t or "contract" in t:
                label = "buying_signal"
            elif "$" in t or "price" in t or "cost" in t or "expensive" in t or "budget" in t:
                label = "price"
            else:
                label = "neutral"
                
        elif candidate_labels and ("CEO" in candidate_labels or "CTO" in candidate_labels):
            if "cto" in t or "technical" in t or "integration complexity" in t:
                label = "CTO"
            elif "developer" in t or "api" in t or "sdk" in t:
                label = "Developer"
            elif "founder" in t or "competitive moat" in t:
                label = "Founder"
            elif "ceo" in t or "roi" in t:
                label = "CEO"
            elif "product manager" in t or "roadmap" in t:
                label = "Product_Manager"
            else:
                label = candidate_labels[0]
                
        elif candidate_labels and ("positive" in candidate_labels or "negative" in candidate_labels):
            if any(w in t for w in ("not happy", "angry", "hate", "terrible", "bad", "worst", "frustrated", "problems")):
                label = "negative"
            elif "okay, i see" in t:
                label = "neutral"
            else:
                label = "positive"
        else:
            label = candidate_labels[0] if candidate_labels else "unknown"
            
        if candidate_labels and label not in candidate_labels:
            label = candidate_labels[0]
            
        return {"labels": [label], "scores": [0.99]}
        
    # Patch the LLM classification entrypoint
    patch.object(LLMZeroShotClassifier, "__call__", fake_classify).start()

    # 2. Patch the underlying google-genai SDK for embeddings globally.
    # This prevents LangChain from throwing `TypeError: 'FakeEmbeddings' object is not callable`
    # because it will still use the real LangChain embeddings class, but the network call is intercepted.
    from google.genai.models import Models
    from google.genai.types import EmbedContentResponse, ContentEmbedding
    
    def fake_embed_content(self, model, contents, **kwargs):
        # Determine number of items to embed based on `contents` which can be a single item or a list
        if not isinstance(contents, list):
            contents = [contents]
        
        embeddings = []
        for i, _ in enumerate(contents):
            # Deterministic, simple mock embedding
            embeddings.append(ContentEmbedding(values=[float((i + 1) % 10) for _ in range(768)]))
        return EmbedContentResponse(embeddings=embeddings)
        
    patch.object(Models, "embed_content", fake_embed_content).start()
