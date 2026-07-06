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

@pytest.fixture(autouse=True)
def mock_external_models(monkeypatch):
    """When USE_MOCK_LLM is true, replace LLM/embedding calls with deterministic mocks."""
    if os.getenv("USE_MOCK_LLM", "").lower() not in ("1", "true", "yes"):
        return

    try:
        import auralis.classifier.shared_model as shared_model
    except ImportError:
        shared_model = None
        
    try:
        from src.classifier.shared_model import classify_text_with_llm, classify
    except ImportError:
        pass

    def fake_classify(text: str, labels: list[str]):
        """Return deterministic label+confidence based on simple keywords used by tests."""
        t = (text or "").lower()
        if "hubspot" in t or "hub spot" in t or "competitor" in t:
            return {"label": "competitor", "confidence": 0.99}
        if "$" in t or "price" in t or "cost" in t or "expensive" in t:
            return {"label": "price", "confidence": 0.99}
        if "not ready" in t or "later" in t or "timing" in t or "wait" in t:
            return {"label": "timing", "confidence": 0.99}
        if "fit" in t or "integrate" in t:
            return {"label": "fit", "confidence": 0.99}
        if "buy" in t or "ready to buy" in t or "interested" in t:
            return {"label": "buying_signal", "confidence": 0.99}
        if "cto" in t or "technical" in t or "integration complexity" in t:
            return {"label": "CTO", "confidence": 0.99}
        if "founder" in t or "competitive moat" in t:
            return {"label": "Founder", "confidence": 0.99}
        if "product manager" in t or "roadmap" in t:
            return {"label": "Product_Manager", "confidence": 0.99}
        if any(w in t for w in ("not happy", "angry", "hate", "terrible", "bad", "worst")):
            return {"label": "negative", "confidence": 0.99}
        return {"label": labels[0] if labels else "unknown", "confidence": 0.99}

    if shared_model is not None:
        monkeypatch.setattr(shared_model, "classify_text_with_llm", fake_classify, raising=False)
        monkeypatch.setattr(shared_model, "classify", fake_classify, raising=False)
    
    # Also patch directly on the module if running locally from src
    try:
        monkeypatch.setattr("src.classifier.shared_model.classify_text_with_llm", fake_classify, raising=False)
        monkeypatch.setattr("src.classifier.shared_model.classify", fake_classify, raising=False)
    except Exception:
        pass

    class DummyEmbeddings:
        def __init__(self, *args, **kwargs):
            pass

        def embed_documents(self, texts):
            return [[float((i + 1) % 10) for _ in range(8)] for i, _ in enumerate(texts)]

        def embed_query(self, text):
            return [0.1 for _ in range(8)]

    monkeypatch.setattr("langchain.embeddings.openai.OpenAIEmbeddings", DummyEmbeddings, raising=False)
    monkeypatch.setattr("langchain_google_genai._client.GoogleGenerativeAI", DummyEmbeddings, raising=False)
    monkeypatch.setattr("langchain.embeddings.base.Embeddings", DummyEmbeddings, raising=False)
    monkeypatch.setattr("langchain_google_genai.GoogleGenerativeAIEmbeddings", DummyEmbeddings, raising=False)
    monkeypatch.setattr("src.rag.retriever.GoogleGenerativeAIEmbeddings", DummyEmbeddings, raising=False)
    monkeypatch.setattr("src.rag.ingest.GoogleGenerativeAIEmbeddings", DummyEmbeddings, raising=False)
