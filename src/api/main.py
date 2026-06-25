"""
auralis/src/api/main.py
─────────────────────────
FastAPI application entry point for Auralis.
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routes.chat import router as chat_router
from src.api.schemas import HealthResponse
from src.memory.db import init_db

# ─── Logging Setup ────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("auralis.api")


# ─── Lifespan (Startup / Shutdown) ────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handles startup DB initialization and any teardown tasks."""
    logger.info("Initializing database on startup...")
    try:
        await init_db()
        logger.info("Database initialized successfully.")
    except Exception as exc:
        logger.error("Failed to initialize database: %s", exc, exc_info=True)
    yield
    logger.info("Shutting down API...")


# ─── FastAPI Initialization ───────────────────────────────────────────────────

app = FastAPI(
    title="Auralis AI Sales Agent API",
    description=(
        "Production inference API for Auralis. Implements zero-shot sales objection classification, "
        "persona detection, sentiment analysis, strategy-routing, citation-honest generation, and decision explainability."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins for local development/streamlit dashboards
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── Routes ───────────────────────────────────────────────────────────────────

# Health Check (Feature 14 requirement)
@app.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check endpoint for container orchestrators and monitoring tools.",
)
async def health() -> dict[str, str]:
    return {"status": "ok", "version": "1.0.0"}


# Mount Chat / Session routes
app.include_router(chat_router, tags=["Conversation & Memory"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.api.main:app", host="0.0.0.0", port=8000, reload=True)
