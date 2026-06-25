"""
tests/test_api.py
──────────────────
Pytest suite for the FastAPI endpoints in src/api/main.py and src/api/routes/chat.py.
"""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

# Mock the database init so we don't connect to a real PostgreSQL on import/lifespan startup
import src.api.main
with patch("src.api.main.init_db", new_callable=AsyncMock) as mock_startup_init, \
     patch("src.api.main.init_users_db", new_callable=AsyncMock), \
     patch("src.api.main.seed_admin", new_callable=AsyncMock), \
     patch("src.api.main.init_analytics_db", new_callable=AsyncMock):
    from src.api.main import app

# ─── Auth override ──────────────────────────────────────────────────────────────────
# Replace get_current_user with a no-op that returns a fake admin so all
# existing tests pass without a real JWT or database.

from src.api.auth import User, get_current_user

_FAKE_ADMIN = User(id="00000000-0000-0000-0000-000000000001", email="admin@test.ai", role="admin")

app.dependency_overrides[get_current_user] = lambda: _FAKE_ADMIN

client = TestClient(app)


# ─── Mock Data Generators ─────────────────────────────────────────────────────

def _mock_graph_state() -> dict[str, Any]:
    return {
        "user_input": "We use HubSpot.",
        "objection": {
            "label": "competitor",
            "confidence": 0.95,
            "all_scores": {"competitor": 0.95, "neutral": 0.05},
            "triggers": ["HubSpot"],
        },
        "sentiment": {
            "label": "neutral",
            "score": 0.80,
            "tone_instruction": "Stay professional.",
        },
        "persona": {
            "label": "CEO",
            "confidence": 0.90,
            "pitch_angle": "Focus on ROI and strategic moat.",
        },
        "retrieved_docs": [
            {
                "text": "HubSpot integration features...",
                "source_file": "hubspot.md",
                "chunk_index": 2,
                "score": 0.15,
            }
        ],
        "citations": "[1] HubSpot Comparison (hubspot.md, chunk 2)",
        "memory_context": "Customer context: tools=HubSpot.",
        "strategy": "competitor_strategy",
        "response": "Here is how we compare to HubSpot...",
        "confidence": 0.95,
        "should_handoff": False,
        "metadata": {"competitor_mentioned": "HubSpot"},
    }


def _mock_explanation() -> dict[str, Any]:
    return {
        "objection_reason": "Detected competitor objection (confidence 95%) because...",
        "persona_reason": "Identified CEO because of domain-specific framing...",
        "sentiment_reason": "Customer tone is measured...",
        "strategy_reason": "Applied competitor_strategy because...",
        "trigger_phrases": ["HubSpot"],
        "confidence_note": "",
        "handoff_reason": None,
    }


# ─── Health check tests ────────────────────────────────────────────────────────

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["status"] == "ok"
    assert "version" in json_data


# ─── GET /session/{session_id} tests ───────────────────────────────────────────

class TestGetSessionEndpoint:
    @patch("src.api.routes.chat.load_session", new_callable=AsyncMock)
    def test_session_found(self, mock_load):
        mock_load.return_value = {
            "company_name": "Acme Corp",
            "persona_label": "CEO",
            "tools_mentioned": ["HubSpot", "Salesforce"],
            "objections_raised": [{"turn": 1, "label": "price", "confidence": 0.88}],
            "budget_signal": "$50k",
        }

        response = client.get("/session/session_123")
        assert response.status_code == 200
        json_data = response.json()
        assert json_data["session_id"] == "session_123"
        assert json_data["company_name"] == "Acme Corp"
        assert json_data["persona_label"] == "CEO"
        assert "HubSpot" in json_data["tools_mentioned"]
        assert len(json_data["objections_raised"]) == 1
        assert json_data["found"] is True

    @patch("src.api.routes.chat.load_session", new_callable=AsyncMock)
    def test_session_not_found(self, mock_load):
        mock_load.return_value = None

        response = client.get("/session/session_unknown")
        assert response.status_code == 200
        json_data = response.json()
        assert json_data["session_id"] == "session_unknown"
        assert json_data["found"] is False
        assert json_data["company_name"] is None

    def test_session_invalid_id(self):
        # Empty session_id path parameter check (if FastAPI routes allow empty string, but usually it matches different route or errors)
        response = client.get("/session/%20")  # spaces
        assert response.status_code == 400
        assert "must be a non-empty string" in response.json()["detail"]


# ─── POST /chat tests ──────────────────────────────────────────────────────────

class TestPostChatEndpoint:
    @patch("src.api.routes.chat.ConversationMemory.from_session", new_callable=AsyncMock)
    @patch("src.api.routes.chat.run_graph")
    @patch("src.api.routes.chat.explain")
    @patch("src.api.routes.chat.save_session", new_callable=AsyncMock)
    @patch("src.api.routes.chat.log_event", new_callable=AsyncMock)
    def test_successful_chat_turn(
        self, mock_log_event, mock_save, mock_explain, mock_run_graph, mock_from_session
    ):
        # Mock memory
        mock_mem = MagicMock()
        mock_mem.get_context_string.return_value = "Customer context: tools=HubSpot."
        mock_mem.get_facts.return_value = {
            "company_name": None,
            "tools_mentioned": ["HubSpot"],
            "budget_signal": None,
            "objections_raised": [],
        }
        mock_from_session.return_value = mock_mem

        # Mock graph run & explanation
        state = _mock_graph_state()
        mock_run_graph.return_value = state
        mock_explain.return_value = _mock_explanation()

        payload = {"session_id": "session_123", "message": "We use HubSpot."}
        response = client.post("/chat", json=payload)

        # Asserts
        assert response.status_code == 200
        json_data = response.json()

        assert json_data["response"] == state["response"]
        assert json_data["objection_label"] == "competitor"
        assert json_data["confidence"] == 0.95
        assert json_data["sentiment"] == "neutral"
        assert json_data["persona"] == "CEO"
        assert json_data["strategy"] == "competitor_strategy"
        assert json_data["citations"] == state["citations"]
        assert json_data["should_handoff"] is False
        assert json_data["session_id"] == "session_123"
        assert json_data["memory_context"] == "Customer context: tools=HubSpot."
        
        # Verify explanation model nests properly
        assert json_data["explanation"]["objection_reason"] == json_data["explanation"]["objection_reason"]
        assert json_data["explanation"]["trigger_phrases"] == ["HubSpot"]

        # Verify retrieved docs mapped correctly
        assert len(json_data["retrieved_docs"]) == 1
        assert json_data["retrieved_docs"][0]["text"] == "HubSpot integration features..."
        assert json_data["retrieved_docs"][0]["source_file"] == "hubspot.md"

        # Verify save_session was called with correct facts
        mock_save.assert_called_once()
        saved_facts = mock_save.call_args[0][1]
        assert "CEO" in saved_facts.values() or saved_facts.get("persona_label") == "CEO"

    def test_validation_missing_fields(self):
        # Missing message
        response = client.post("/chat", json={"session_id": "session_123"})
        assert response.status_code == 422  # Unprocessable Entity for Pydantic validation

        # Missing session_id
        response = client.post("/chat", json={"message": "Hello"})
        assert response.status_code == 422

    def test_validation_empty_fields(self):
        # Empty message
        response = client.post("/chat", json={"session_id": "session_123", "message": ""})
        assert response.status_code == 422  # pydantic min_length=1

        # Empty session_id after stripping (checked in handler)
        response = client.post("/chat", json={"session_id": "   ", "message": "Hello"})
        assert response.status_code == 400
        assert "must be a non-empty string" in response.json()["detail"]

    @patch("src.api.routes.chat.ConversationMemory.from_session", side_effect=Exception("DB Down"))
    def test_internal_server_error_propagation(self, mock_from_session):
        payload = {"session_id": "session_123", "message": "Hello"}
        response = client.post("/chat", json=payload)
        assert response.status_code == 500
        assert "An error occurred while processing" in response.json()["detail"]
