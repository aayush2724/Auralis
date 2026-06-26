"""
auralis/src/utils/logger.py
───────────────────────────
Structured JSON logging, request middleware, and Prometheus metrics for Auralis.

Provides:
  - structlog-based JSON logger (one log line per request with structured fields)
  - FastAPI middleware that times requests, catches exceptions, and emits logs
  - Prometheus counters/histograms via prometheus-fastapi-instrumentator
  - GET /metrics endpoint for Prometheus scraping
"""

from __future__ import annotations

import logging
import sys
import time
import traceback
from typing import Any, TypedDict

import structlog
from fastapi import FastAPI, Request, Response
from fastapi.responses import PlainTextResponse
from prometheus_client import CollectorRegistry, Counter, Histogram, generate_latest
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

# ─── structlog setup ──────────────────────────────────────────────────────────

shared_processors: list[structlog.types.Processor] = [
    structlog.contextvars.merge_contextvars,
    structlog.processors.add_log_level,
    structlog.processors.TimeStamper(fmt="iso"),
    structlog.processors.StackInfoRenderer(),
    structlog.dev.set_exc_info,
    structlog.processors.format_exc_info,
]


def setup_structlog() -> None:
    """Configure structlog for JSON output to stdout."""
    structlog.configure(
        processors=[
            *shared_processors,
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(file=sys.stdout),
        cache_logger_on_first_use=True,
    )


# ─── Structured log emitter ──────────────────────────────────────────────────

def get_logger(name: str) -> structlog.BoundLogger:
    """
    Return a named structlog BoundLogger.

    Usage::

        logger = get_logger(__name__)
        logger.info("something happened", key="value")
    """
    setup_structlog()
    return structlog.get_logger(name)


# ─── RequestLog schema ───────────────────────────────────────────────────────

class RequestLog(TypedDict, total=False):
    """Structured fields emitted for every completed /chat request."""
    session_id:          str
    user_input_length:   int
    objection_label:     str
    objection_confidence: float
    sentiment_label:     str
    persona_label:       str
    strategy_chosen:     str
    response_length:     int
    latency_ms:          float
    should_handoff:      bool
    handoff_trigger:     str | None


def log_request(data: RequestLog) -> None:
    """Emit a structured JSON log line for a completed /chat request."""
    logger = get_logger("auralis.request")
    logger.info("chat_request", **data)


def log_exception(
    *,
    method: str = "",
    path: str = "",
    status_code: int = 500,
    error: str = "",
    traceback_str: str = "",
) -> None:
    """Emit a structured JSON log line for an unhandled exception."""
    logger = get_logger("auralis.request")
    logger.error(
        "request_exception",
        method=method,
        path=path,
        status_code=status_code,
        error=error,
        traceback=traceback_str,
    )


# ─── Prometheus metrics ───────────────────────────────────────────────────────

_registry = CollectorRegistry()

auralis_requests_total = Counter(
    "auralis_requests_total",
    "Total HTTP requests processed",
    ["method", "path", "status_code", "objection_label"],
    registry=_registry,
)

auralis_latency_seconds = Histogram(
    "auralis_latency_seconds",
    "Request latency in seconds",
    ["method", "path"],
    buckets=(0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0),
    registry=_registry,
)

auralis_handoffs_total = Counter(
    "auralis_handoffs_total",
    "Total handoff escalations",
    ["trigger"],
    registry=_registry,
)

auralis_objections_total = Counter(
    "auralis_objections_total",
    "Total objection classifications",
    ["objection_label"],
    registry=_registry,
)


def render_metrics() -> str:
    """Return the Prometheus metrics text exposition."""
    return generate_latest(_registry).decode("utf-8")


# ─── FastAPI middleware ───────────────────────────────────────────────────────

# Stores per-request metadata so the middleware can emit a rich log line.
# Keyed by (method, path); written by route handlers, read by middleware.
_request_metadata: dict[tuple[str, str], dict[str, Any]] = {}


def set_request_metadata(method: str, path: str, **kwargs: Any) -> None:
    """Store structured metadata for the current request (called by route handlers)."""
    _request_metadata[(method, path)] = kwargs


def _pop_request_metadata(method: str, path: str) -> dict[str, Any]:
    """Retrieve and clear stored metadata for this request."""
    return _request_metadata.pop((method, path), {})


class StructuredLoggingMiddleware(BaseHTTPMiddleware):
    """
    FastAPI middleware that:
      1. Records the start time.
      2. Catches unhandled exceptions and logs them with stack trace.
      3. Logs every response with structured fields.
      4. Updates Prometheus counters/histograms.
    """

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint,
    ) -> Response:
        method = request.method
        path = request.url.path
        start = time.perf_counter()

        try:
            response = await call_next(request)
        except Exception as exc:
            elapsed_ms = (time.perf_counter() - start) * 1000
            tb_str = traceback.format_exc()
            log_exception(
                method=method,
                path=path,
                status_code=500,
                error=str(exc),
                traceback_str=tb_str,
            )
            auralis_requests_total.labels(
                method=method, path=path, status_code=500, objection_label="",
            ).inc()
            auralis_latency_seconds.labels(method=method, path=path).observe(
                elapsed_ms / 1000
            )
            raise

        elapsed_ms = (time.perf_counter() - start) * 1000
        meta = _pop_request_metadata(method, path)

        log_request(RequestLog(
            session_id=meta.get("session_id", ""),
            user_input_length=meta.get("user_input_length", 0),
            objection_label=meta.get("objection_label", ""),
            objection_confidence=meta.get("confidence", 0.0),
            sentiment_label=meta.get("sentiment", ""),
            persona_label=meta.get("persona", ""),
            strategy_chosen=meta.get("strategy", ""),
            response_length=meta.get("response_length", 0),
            latency_ms=round(elapsed_ms, 2),
            should_handoff=meta.get("handoff", False),
            handoff_trigger=meta.get("handoff_trigger"),
        ))

        # Prometheus counters
        objection_label = meta.get("objection_label", "")
        auralis_requests_total.labels(
            method=method, path=path,
            status_code=str(response.status_code),
            objection_label=objection_label,
        ).inc()
        auralis_latency_seconds.labels(method=method, path=path).observe(
            elapsed_ms / 1000
        )
        if meta.get("handoff"):
            trigger = meta.get("handoff_trigger", "unknown")
            auralis_handoffs_total.labels(trigger=trigger).inc()

        return response


# ─── Mount on FastAPI app ─────────────────────────────────────────────────────

def mount_logging(app: FastAPI) -> None:
    """
    Add the structured-logging middleware and /metrics endpoint to the app.

    Call this once after the app is created but before uvicorn starts.
    """
    setup_structlog()
    app.add_middleware(StructuredLoggingMiddleware)

    @app.get(
        "/metrics",
        response_class=PlainTextResponse,
        tags=["Observability"],
        summary="Prometheus scrape target.",
        include_in_schema=False,
    )
    async def metrics() -> Response:
        return Response(
            content=render_metrics(),
            media_type="text/plain; version=0.0.4; charset=utf-8",
        )
