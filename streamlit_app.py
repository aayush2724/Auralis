"""
streamlit_app.py
────────────────
Interactive Streamlit front-end for PitchIQ (Auralis).

Tabs
────
  1. 💬 Sales Chat     — live conversation with sidebar diagnostics
  2. 📊 Analytics      — dashboard with plotly charts
  3. 🧪 A/B Test       — variant comparison
  4. 📁 Knowledge Base — upload collateral (admin only)

Run
───
    streamlit run streamlit_app.py
"""

from __future__ import annotations

import os
import uuid

import httpx
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ─── Config ───────────────────────────────────────────────────────────────────

API_BASE = os.getenv("AURALIS_API_URL", "http://localhost:8000")

st.set_page_config(
    page_title="PitchIQ",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Session state init ──────────────────────────────────────────────────────

if "messages" not in st.session_state:
    st.session_state.messages = []
if "session_id" not in st.session_state:
    st.session_state.session_id = ""
if "jwt_token" not in st.session_state:
    st.session_state.jwt_token = ""
if "last_response" not in st.session_state:
    st.session_state.last_response = None

# ─── Helpers ──────────────────────────────────────────────────────────────────

_SENTIMENT_EMOJI = {
    "positive": "😊",
    "neutral":  "😐",
    "negative": "😠",
}

_OBJECTION_COLORS = {
    "price":       "#ff6b6b",
    "trust":       "#ffa94d",
    "timing":      "#ffd43b",
    "competitor":  "#69db7c",
    "fit":         "#74c0fc",
    "buying_signal": "#da77f2",
    "neutral":     "#adb5bd",
}


def _auth_headers() -> dict[str, str]:
    token = st.session_state.jwt_token
    return {"Authorization": f"Bearer {token}"} if token else {}


def _api_post(path: str, json: dict | None = None, **kwargs) -> httpx.Response | None:
    try:
        return httpx.post(f"{API_BASE}{path}", json=json, headers=_auth_headers(), timeout=30, **kwargs)
    except httpx.ConnectError:
        st.error("Cannot connect to PitchIQ API. Is it running?")
        return None


def _api_get(path: str, **kwargs) -> httpx.Response | None:
    try:
        return httpx.get(f"{API_BASE}{path}", headers=_auth_headers(), timeout=15, **kwargs)
    except httpx.ConnectError:
        st.error("Cannot connect to PitchIQ API. Is it running?")
        return None


# ─── Login ────────────────────────────────────────────────────────────────────


def _login() -> bool:
    if st.session_state.jwt_token:
        return True

    st.title("🎙️ PitchIQ")
    st.subheader("Sign in to continue")

    with st.form("login"):
        email = st.text_input("Email", value="admin@auralis.ai")
        password = st.text_input("Password", type="password")
        if st.form_submit_button("Login"):
            resp = httpx.post(
                f"{API_BASE}/auth/token",
                data={"username": email, "password": password},
                timeout=10,
            )
            if resp.status_code == 200:
                st.session_state.jwt_token = resp.json()["access_token"]
                st.rerun()
            else:
                st.error("Invalid credentials")
    return False


# ─── Tab 1: Sales Chat ───────────────────────────────────────────────────────


def _tab_chat():
    # Session ID
    col_id, col_btn = st.columns([3, 1])
    with col_id:
        sid = st.text_input(
            "Session ID",
            value=st.session_state.session_id,
            placeholder="Leave empty to auto-generate",
            key="sid_input",
        )
    with col_btn:
        if st.button("New Session", use_container_width=True):
            st.session_state.session_id = str(uuid.uuid4())
            st.session_state.messages = []
            st.session_state.last_response = None
            st.rerun()

    if not st.session_state.session_id:
        if sid:
            st.session_state.session_id = sid
        else:
            st.session_state.session_id = str(uuid.uuid4())

    # ── Main area: chat history ───────────────────────────────────────────
    chat_col, sidebar_col = st.columns([3, 1])

    with chat_col:
        # Display message history
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        # Input
        if prompt := st.chat_input("Type your message..."):
            # Show user message
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            # Call API
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    resp = _api_post("/chat", json={
                        "session_id": st.session_state.session_id,
                        "message": prompt,
                    })
                    if resp and resp.status_code == 200:
                        data = resp.json()
                        st.session_state.last_response = data
                        st.markdown(data["response"])
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": data["response"],
                        })
                    elif resp:
                        st.error(f"API error: {resp.status_code} — {resp.text}")

    # ── Right sidebar: live diagnostics ───────────────────────────────────
    with sidebar_col:
        st.markdown("### Live Diagnostics")
        data = st.session_state.last_response

        if data:
            # Objection badge
            obj_label = data.get("objection_label", "neutral")
            conf = data.get("confidence", 0.0)
            color = _OBJECTION_COLORS.get(obj_label, "#adb5bd")
            st.markdown(
                f'<div style="background:{color};color:white;padding:8px 12px;'
                f'border-radius:8px;text-align:center;margin-bottom:8px;">'
                f'<b>{obj_label.upper()}</b><br>{conf:.0%} confidence</div>',
                unsafe_allow_html=True,
            )

            # Sentiment emoji
            sentiment = data.get("sentiment", "neutral")
            emoji = _SENTIMENT_EMOJI.get(sentiment, "😐")
            st.markdown(f"**Sentiment:** {emoji} {sentiment}")

            # Persona badge
            persona = data.get("persona", "Unknown")
            st.markdown(f"**Persona:** `{persona}`")

            # Strategy
            strategy = data.get("strategy", "")
            st.markdown(f"**Strategy:** `{strategy}`")

            # Handoff warning
            if data.get("should_handoff"):
                st.warning("⚠️ Human handoff recommended!")

            # Session facts
            memory = data.get("memory_context", "")
            if memory:
                st.divider()
                st.markdown("**Session Memory**")
                st.caption(memory)

            # ── Expanders ────────────────────────────────────────────────
            st.divider()

            with st.expander("Why did PitchIQ say this?"):
                exp = data.get("explanation", {})
                st.markdown(f"**Objection:** {exp.get('objection_reason', '')}")
                st.markdown(f"**Persona:** {exp.get('persona_reason', '')}")
                st.markdown(f"**Sentiment:** {exp.get('sentiment_reason', '')}")
                st.markdown(f"**Strategy:** {exp.get('strategy_reason', '')}")
                triggers = exp.get("trigger_phrases", [])
                if triggers:
                    st.markdown(f"**Trigger phrases:** {', '.join(triggers)}")
                if exp.get("confidence_note"):
                    st.info(exp["confidence_note"])
                if exp.get("handoff_reason"):
                    st.warning(exp["handoff_reason"])

            with st.expander("Retrieved documents"):
                docs = data.get("retrieved_docs", [])
                if docs:
                    for i, doc in enumerate(docs, 1):
                        st.markdown(
                            f"**[{i}]** `{doc['source_file']}` (chunk {doc['chunk_index']}, "
                            f"score {doc['score']:.3f})"
                        )
                        st.caption(doc["text"][:300])
                else:
                    st.info("No documents retrieved for this turn.")
        else:
            st.info("Send a message to see live diagnostics.")


# ─── Tab 2: Analytics Dashboard ──────────────────────────────────────────────


def _tab_analytics():
    st.header("📊 Analytics Dashboard")

    resp = _api_get("/analytics/dashboard")
    if not resp or resp.status_code != 200:
        st.info("No analytics data available yet.")
        return

    data = resp.json()

    # ── Metric cards ──────────────────────────────────────────────────────
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Sessions", data["total_sessions"])
    c2.metric("Conversion Rate", f"{data['conversion_rate']:.1%}")
    c3.metric("Avg Confidence", f"{data['avg_confidence']:.2f}")

    st.divider()

    # ── Objection distribution (bar chart) ────────────────────────────────
    obj_dist = data.get("objection_distribution", {})
    if obj_dist:
        fig_obj = px.bar(
            x=list(obj_dist.keys()),
            y=list(obj_dist.values()),
            labels={"x": "Objection", "y": "Count"},
            title="Objection Distribution",
            color=list(obj_dist.keys()),
            color_discrete_sequence=px.colors.qualitative.Set2,
        )
        fig_obj.update_layout(showlegend=False)
        st.plotly_chart(fig_obj, use_container_width=True)

    col_left, col_right = st.columns(2)

    with col_left:
        # ── Persona distribution (pie chart) ──────────────────────────────
        persona_dist = data.get("persona_distribution", {})
        if persona_dist:
            fig_pie = px.pie(
                names=list(persona_dist.keys()),
                values=list(persona_dist.values()),
                title="Persona Distribution",
                color_discrete_sequence=px.colors.qualitative.Pastel,
            )
            st.plotly_chart(fig_pie, use_container_width=True)

    with col_right:
        # ── Sentiment trend (line chart) ──────────────────────────────────
        trend = data.get("sentiment_trend", [])
        if trend:
            dates = [d["date"] for d in reversed(trend)]
            fig_line = go.Figure()
            fig_line.add_trace(go.Scatter(
                x=dates, y=[d["positive"] for d in reversed(trend)],
                name="Positive", line=dict(color="#51cf66", width=2),
            ))
            fig_line.add_trace(go.Scatter(
                x=dates, y=[d["neutral"] for d in reversed(trend)],
                name="Neutral", line=dict(color="#ffd43b", width=2),
            ))
            fig_line.add_trace(go.Scatter(
                x=dates, y=[d["negative"] for d in reversed(trend)],
                name="Negative", line=dict(color="#ff6b6b", width=2),
            ))
            fig_line.update_layout(
                title="Sentiment Trend (Last 30 Days)",
                xaxis_title="Date",
                yaxis_title="Count",
                hovermode="x unified",
            )
            st.plotly_chart(fig_line, use_container_width=True)


# ─── Tab 3: A/B Test Results ────────────────────────────────────────────────


def _tab_ab_test():
    st.header("🧪 A/B Test Results")

    resp = _api_get("/ab-test/results")
    if not resp or resp.status_code != 200:
        st.info("No A/B test data available yet.")
        return

    data = resp.json()

    # ── Side-by-side bar chart ────────────────────────────────────────────
    static_conv = data["static_conversion_rate"]
    adaptive_conv = data["adaptive_conversion_rate"]

    fig = go.Figure(data=[
        go.Bar(
            name="Static", x=["Conversion Rate"], y=[static_conv],
            marker_color="#adb5bd", text=[f"{static_conv:.1%}"], textposition="auto",
        ),
        go.Bar(
            name="Adaptive", x=["Conversion Rate"], y=[adaptive_conv],
            marker_color="#51cf66", text=[f"{adaptive_conv:.1%}"], textposition="auto",
        ),
    ])
    fig.update_layout(
        barmode="group",
        title="Conversion Rate: Static vs Adaptive",
        yaxis_tickformat=".0%",
        yaxis_range=[0, max(static_conv, adaptive_conv, 0.01) * 1.3],
    )
    st.plotly_chart(fig, use_container_width=True)

    # ── Improvement metric ────────────────────────────────────────────────
    if static_conv > 0:
        improvement = ((adaptive_conv - static_conv) / static_conv) * 100
        st.metric(
            "Adaptive Improvement",
            f"{improvement:+.1f}%",
            delta="over Static variant",
        )
    else:
        st.metric("Adaptive Conversion", f"{adaptive_conv:.1%}")

    st.divider()

    # ── Detail table ──────────────────────────────────────────────────────
    sessions = data.get("sessions_per_variant", {})
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("STATIC")
        st.metric("Sessions", sessions.get("STATIC", 0))
        st.metric("Avg Confidence", f"{data['static_avg_confidence']:.2f}")
        st.metric("Conversion", f"{static_conv:.1%}")
    with c2:
        st.subheader("ADAPTIVE")
        st.metric("Sessions", sessions.get("ADAPTIVE", 0))
        st.metric("Avg Confidence", f"{data['adaptive_avg_confidence']:.2f}")
        st.metric("Conversion", f"{adaptive_conv:.1%}")


# ─── Tab 4: Knowledge Base ──────────────────────────────────────────────────


def _tab_kb():
    st.header("📁 Knowledge Base")

    # ── File uploader ─────────────────────────────────────────────────────
    uploaded = st.file_uploader(
        "Upload sales collateral",
        type=["pdf", "csv", "md"],
        accept_multiple_files=True,
        key="kb_upload",
    )

    if uploaded and st.button("Ingest Files", type="primary"):
        files_data = [
            ("files", (f.name, f.getvalue(), f.type or "application/octet-stream"))
            for f in uploaded
        ]
        with st.spinner("Uploading and ingesting..."):
            resp = _api_post("/kb/ingest", files=files_data)
            if resp and resp.status_code == 200:
                result = resp.json()
                st.success(
                    f"Ingested {result['files_processed']} file(s) — "
                    f"{result['chunks_added']} chunks added."
                )
            elif resp:
                st.error(f"Ingestion failed: {resp.text}")

    st.divider()

    # ── KB stats ──────────────────────────────────────────────────────────
    st.subheader("Current Statistics")
    resp = _api_get("/kb/stats")
    if resp and resp.status_code == 200:
        stats = resp.json()
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Documents", stats["total_documents"])
        c2.metric("Total Chunks", stats["total_chunks"])
        c3.metric("Last Updated", stats["last_updated"] or "Never")
    else:
        st.info("KB stats unavailable.")


# ─── Main ─────────────────────────────────────────────────────────────────────


def main():
    if not _login():
        return

    # Sidebar
    with st.sidebar:
        st.title("🎙️ PitchIQ")
        st.caption("AI Sales Agent")
        st.divider()
        if st.button("Logout"):
            st.session_state.jwt_token = ""
            st.session_state.messages = []
            st.session_state.last_response = None
            st.rerun()
        st.divider()
        st.caption(f"Session: `{st.session_state.session_id[:12]}...`")

    # Tabs
    tab_chat, tab_analytics, tab_ab, tab_kb = st.tabs([
        "💬 Sales Chat",
        "📊 Analytics",
        "🧪 A/B Test",
        "📁 Knowledge Base",
    ])

    with tab_chat:
        _tab_chat()
    with tab_analytics:
        _tab_analytics()
    with tab_ab:
        _tab_ab_test()
    with tab_kb:
        _tab_kb()


if __name__ == "__main__":
    main()
