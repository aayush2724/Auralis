<div align="center">
  <img src="https://raw.githubusercontent.com/aayush2724/Auralis/main/client/public/vite.svg" width="120" alt="Auralis Logo" />
  
  # Auralis 🎙️
  
  **The AI Sales Coach that reads the room.**
  
  <p align="center">
    <a href="https://auralis-client-five.vercel.app"><b>✨ View Live Demo</b></a> •
    <a href="#-architecture">Architecture</a> •
    <a href="#-features">Features</a> •
    <a href="#-quickstart">Quickstart</a>
  </p>

  [![CI](https://github.com/aayush2724/Auralis/actions/workflows/ci.yml/badge.svg)](https://github.com/aayush2724/Auralis/actions/workflows/ci.yml)
  [![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https%3A%2F%2Fgithub.com%2Faayush2724%2FAuralis)
  [![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/aayush2724/Auralis)
  [![Python](https://img.shields.io/badge/Python-3.11+-blue.svg?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
  [![FastAPI](https://img.shields.io/badge/FastAPI-v0.100+-green.svg?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
  [![LangGraph](https://img.shields.io/badge/LangGraph-Framework-orange.svg?style=flat-square)](https://github.com/langchain-ai/langgraph)
  [![React](https://img.shields.io/badge/React-18-blue.svg?style=flat-square&logo=react&logoColor=white)](https://react.dev/)
  [![Tailwind](https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=flat-square&logo=tailwind-css&logoColor=white)](https://tailwindcss.com/)
</div>

<br/>

> **Auralis** is an adaptive sales intelligence platform that classifies objections (94% confidence), detects customer personas and sentiment, and generates role-specific responses in under 2 seconds. Built for high-performance sales teams using **LangGraph** and **RAG**.

---

## ⚡ Live Demo

The application is deployed live and ready to test!

- **Frontend:** [Auralis Client (Vercel)](https://auralis-client-five.vercel.app)
- **Backend API:** FastAPI (Render) + PostgreSQL (Neon) + Redis (Upstash)

---

## 🏗️ Architecture

Auralis uses a decoupled microservices architecture with a directed acyclic graph (DAG) for conversational state management.

```mermaid
graph TD
    User([User / Browser]) <-->|REST API + WebSocket| API[FastAPI Server]
    
    subgraph Backend Pipeline
        API --> LangGraph[LangGraph Coordinator]
        
        LangGraph --> C[Classify Node]
        C -.->|Persona, Sentiment, Objection| Router{Router}
        
        Router --> S1[Price Strategy]
        Router --> S2[Trust Strategy]
        Router --> S3[Timing Strategy]
        
        LangGraph <--> RAG[(FAISS Vector Store)]
        
        S1 & S2 & S3 --> Gen[Generate Response]
    end
    
    API <--> Cache[(Redis Session Cache)]
    API <--> DB[(Postgres Analytics)]
```

---

## ✨ 14 Production Features

Auralis isn't just a prototype; it's built with 14 production-grade features designed for real-world scaling.

<details>
<summary><b>🧠 1. Core AI Capabilities (Click to expand)</b></summary>

| Feature | Description |
|---|---|
| **Objection Classification** | Automatically classifies client objections (pricing, timing, trust, fit, competitors). |
| **Sentiment Analysis** | Real-time sentiment classification to gauge customer frustration or enthusiasm. |
| **Persona Profiling** | Detects customer buying personas (Assertive, Analytical, Amiable, Expressive). |
| **Adaptive Pipeline** | Uses LangGraph (DAG) for dynamic routing based on classifications. |

</details>

<details>
<summary><b>📚 2. Knowledge & RAG (Click to expand)</b></summary>

| Feature | Description |
|---|---|
| **Vector Retrieval** | High-performance similarity search on sales collateral using FAISS. |
| **Multi-Format Ingestion** | Supports PDF, CSV, and Markdown file ingestion automatically. |
| **Source Citations** | Appends factual citations to synthesized model answers to prevent hallucinations. |
| **Explainability Tracking** | Exposes node execution metadata showing *why* a strategy was chosen. |

</details>

<details>
<summary><b>⚙️ 3. Systems & Infrastructure (Click to expand)</b></summary>

| Feature | Description |
|---|---|
| **Human Handoff** | Triggers an immediate human escalation when low confidence or frustration is detected. |
| **A/B Testing** | Deterministic 50/50 variant assignment (Static vs Adaptive) mapped to Redis. |
| **Analytics Event Tracker** | Logs sentiment trends and variant conversion ratios to Postgres. |
| **Redis Session Cache** | Persists conversation history and state for rapid sub-millisecond retrieval. |
| **JWT Authentication** | Secures REST and WebSocket chat channels with JSON Web Tokens. |
| **Real-time Chat Transport** | Supports authenticated WebSocket chat at `/ws/chat` with HTTP fallback for resilience. |
| **Prometheus Monitoring** | Exposes structured latency and request metrics for observability. |

</details>

---

## 🚀 Quickstart (Local Development)

Want to run Auralis locally? You can spin up the entire stack in just three commands using Docker Compose.

```bash
# 1. Clone the repository
git clone https://github.com/aayush2724/Auralis.git
cd Auralis

# 2. Set up environment configuration
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY and JWT_SECRET_KEY

# 3. Start the stack (PostgreSQL, Redis, FastAPI, and React)
docker compose up --build
```

The frontend will be available at `http://localhost:4000` and the API at `http://localhost:8001`.

---

## ☁️ Deployment

This repository includes everything needed for one-click cloud deployment:

- **Frontend (Vercel):** Connect the repo to Vercel. `client/vercel.json` handles SPA routing automatically.
- **Backend (Render):** A `render.yaml` blueprint is included to instantly provision the FastAPI Web Service and Redis Cache.

---

## 📄 Resume / Portfolio Summary

> *Built Auralis, an adaptive sales intelligence platform using LangGraph + RAG with end-to-end production architecture: React frontend, FastAPI backend, JWT-secured REST + WebSocket APIs, PostgreSQL persistence, Redis-backed experiments, CI/CD, and Prometheus observability.*
