"""
auralis/src/dashboard/app.py
─────────────────────────────
Streamlit admin dashboard for Auralis.

Tabs
────
  1. Overview    — health check, quick stats
  2. Knowledge Base — upload collateral, view KB stats
  3. A/B Test    — variant comparison chart
  4. Analytics   — sentiment trend, objection distribution

Run
───
    streamlit run src/dashboard/app.py
"""

from __future__ import annotations

import os

import httpx
import streamlit as st

# ─── Config ───────────────────────────────────────────────────────────────────

API_BASE = os.getenv("AURALIS_API_URL", "http://localhost:8000")

st.set_page_config(
    page_title="Auralis Admin",
    page_icon="🎙️",
    layout="wide",
)

# ─── Auth helpers ─────────────────────────────────────────────────────────────


def _get_token() -> str | None:
    """Return the cached JWT or None."""
    return st.session_state.get("jwt_token")


def _login_form() -> str | None:
    """Display a login form and return the JWT on success."""
    with st.form("login_form"):
        email = st.text_input("Email", value="admin@auralis.ai")
        password = st.text_input("Password", type="password", value="changeme")
        submitted = st.form_submit_button("Login")
        if submitted:
            resp = httpx.post(
                f"{API_BASE}/auth/token",
                data={"username": email, "password": password},
                timeout=10,
            )
            if resp.status_code == 200:
                token = resp.json()["access_token"]
                st.session_state["jwt_token"] = token
                st.success("Logged in.")
                return token
            else:
                st.error(f"Login failed: {resp.status_code} — {resp.text}")
    return None


def _auth_headers() -> dict[str, str]:
    """Return Authorization header dict."""
    token = _get_token()
    return {"Authorization": f"Bearer {token}"} if token else {}


# ─── KB tab ───────────────────────────────────────────────────────────────────


def _kb_tab():
    st.header("Knowledge Base")

    # ── File uploader ──────────────────────────────────────────────────────
    uploaded_files = st.file_uploader(
        "Upload sales collateral",
        type=["pdf", "csv", "md"],
        accept_multiple_files=True,
        key="kb_uploader",
    )

    if uploaded_files and st.button("Ingest Files"):
        headers = _auth_headers()
        if not headers:
            st.error("Not authenticated. Please login first.")
            return

        files_data = [
            ("files", (f.name, f.getvalue(), f.type or "application/octet-stream"))
            for f in uploaded_files
        ]

        with st.spinner("Uploading and ingesting files..."):
            try:
                resp = httpx.post(
                    f"{API_BASE}/kb/ingest",
                    headers=headers,
                    files=files_data,
                    timeout=120,
                )
                if resp.status_code == 200:
                    result = resp.json()
                    st.success(
                        f"✅ Ingested {result['files_processed']} file(s) — "
                        f"{result['chunks_added']} chunks added to the index."
                    )
                else:
                    st.error(f"Ingestion failed: {resp.status_code} — {resp.text}")
            except httpx.ConnectError:
                st.error("Cannot connect to Auralis API. Is it running?")
            except Exception as exc:
                st.error(f"Error: {exc}")

    st.divider()

    # ── KB stats ───────────────────────────────────────────────────────────
    st.subheader("Current KB Statistics")
    headers = _auth_headers()
    if headers:
        try:
            resp = httpx.get(f"{API_BASE}/kb/stats", headers=headers, timeout=10)
            if resp.status_code == 200:
                stats = resp.json()
                col1, col2, col3 = st.columns(3)
                col1.metric("Total Documents", stats["total_documents"])
                col2.metric("Total Chunks", stats["total_chunks"])
                col3.metric("Last Updated", stats["last_updated"] or "Never")
            else:
                st.warning(f"Could not load KB stats: {resp.status_code}")
        except httpx.ConnectError:
            st.info("API not reachable — KB stats unavailable.")
    else:
        st.info("Login to view KB statistics.")


# ─── Overview tab ─────────────────────────────────────────────────────────────


def _overview_tab():
    st.header("Auralis Overview")

    headers = _auth_headers()
    if not headers:
        st.info("Login to view dashboard data.")
        return

    try:
        resp = httpx.get(f"{API_BASE}/health", timeout=5)
        if resp.status_code == 200:
            health = resp.json()
            st.success(f"API Status: {health['status']} | Version: {health['version']}")
        else:
            st.warning(f"Health check failed: {resp.status_code}")
    except httpx.ConnectError:
        st.error("Cannot connect to Auralis API.")


# ─── A/B Test tab ────────────────────────────────────────────────────────────


def _ab_test_tab():
    st.header("A/B Test Results")

    headers = _auth_headers()
    if not headers:
        st.info("Login to view A/B test data.")
        return

    try:
        resp = httpx.get(f"{API_BASE}/ab-test/results", headers=headers, timeout=10)
        if resp.status_code == 200:
            data = resp.json()

            col1, col2 = st.columns(2)
            with col1:
                st.subheader("STATIC Variant")
                st.metric("Conversion Rate", f"{data['static_conversion_rate']:.1%}")
                st.metric("Avg Confidence", f"{data['static_avg_confidence']:.2f}")
                st.metric("Sessions", data["sessions_per_variant"].get("STATIC", 0))
            with col2:
                st.subheader("ADAPTIVE Variant")
                st.metric("Conversion Rate", f"{data['adaptive_conversion_rate']:.1%}")
                st.metric("Avg Confidence", f"{data['adaptive_avg_confidence']:.2f}")
                st.metric("Sessions", data["sessions_per_variant"].get("ADAPTIVE", 0))
        else:
            st.warning(f"Could not load A/B data: {resp.status_code}")
    except httpx.ConnectError:
        st.error("Cannot connect to Auralis API.")


# ─── Analytics tab ────────────────────────────────────────────────────────────


def _analytics_tab():
    st.header("Analytics Dashboard")

    headers = _auth_headers()
    if not headers:
        st.info("Login to view analytics.")
        return

    try:
        resp = httpx.get(f"{API_BASE}/analytics/dashboard", headers=headers, timeout=10)
        if resp.status_code == 200:
            data = resp.json()

            col1, col2, col3 = st.columns(3)
            col1.metric("Total Sessions", data["total_sessions"])
            col2.metric("Conversion Rate", f"{data['conversion_rate']:.1%}")
            col3.metric("Avg Confidence", f"{data['avg_confidence']:.2f}")

            if data.get("objection_distribution"):
                st.subheader("Objection Distribution")
                st.bar_chart(data["objection_distribution"])

            if data.get("persona_distribution"):
                st.subheader("Persona Distribution")
                st.bar_chart(data["persona_distribution"])

            if data.get("sentiment_trend"):
                st.subheader("Sentiment Trend (Last 30 Days)")
                st.line_chart(
                    {
                        "positive": [d["positive"] for d in data["sentiment_trend"]],
                        "neutral":  [d["neutral"]  for d in data["sentiment_trend"]],
                        "negative": [d["negative"] for d in data["sentiment_trend"]],
                    }
                )
        else:
            st.warning(f"Could not load analytics: {resp.status_code}")
    except httpx.ConnectError:
        st.error("Cannot connect to Auralis API.")


# ─── Main app ────────────────────────────────────────────────────────────────


def main():
    # Ensure user is logged in
    if not _get_token():
        _login_form()
        return

    st.sidebar.title("Auralis")
    st.sidebar.caption("Admin Dashboard")

    if st.sidebar.button("Logout"):
        del st.session_state["jwt_token"]
        st.rerun()

    tab_overview, tab_kb, tab_ab, tab_analytics = st.tabs(
        ["Overview", "Knowledge Base", "A/B Test", "Analytics"]
    )

    with tab_overview:
        _overview_tab()
    with tab_kb:
        _kb_tab()
    with tab_ab:
        _ab_test_tab()
    with tab_analytics:
        _analytics_tab()


if __name__ == "__main__":
    main()
