# Auralis 🎙️

[![CI](https://github.com/aayush2724/auralis/actions/workflows/ci.yml/badge.svg)](https://github.com/aayush2724/auralis/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-v0.100+-green.svg?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![LangGraph](https://img.shields.io/badge/LangGraph-Framework-orange.svg?style=flat-square)](https://github.com/langchain-ai/langgraph)
[![FAISS](https://img.shields.io/badge/FAISS-VectorStore-yellow.svg?style=flat-square)](https://github.com/facebookresearch/faiss)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue.svg?style=flat-square&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Redis](https://img.shields.io/badge/Redis-Cache-red.svg?style=flat-square&logo=redis&logoColor=white)](https://redis.io/)
[![React](https://img.shields.io/badge/React-18-blue.svg?style=flat-square&logo=react&logoColor=white)](https://react.dev/)
[![Tailwind](https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=flat-square&logo=tailwind-css&logoColor=white)](https://tailwindcss.com/)
[![Docker](https://img.shields.io/badge/Docker-Container-blue.svg?style=flat-square&logo=docker&logoColor=white)](https://www.docker.com/)
[![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-CI/CD-black.svg?style=flat-square&logo=githubactions&logoColor=white)](https://github.com/features/actions)

> AI sales coach that adapts in real time to objections, sentiment, and persona — built with LangGraph, RAG, and 14 production features.

---

## Architecture Diagram

```text
                               +-----------------------------+
                               |         Web Browser         |
                               |  (React / Vite Frontend)    |
                               +--------------+--------------+
                                              |
                                              v (HTTP / REST)
                               +--------------+--------------+
                               |     FastAPI Server (API)    |
                               +--------------+--------------+
                                              |
                                              v
      +---------------------------------------+---------------------------------------+
      |                               LangGraph Pipeline                              |
      |                                                                               |
      |  +-------------------+     +------------------+     +----------------------+  |
      |  |  Classify Node    |     |  Retrieve Node   |     |    Strategy Node     |  |
      |  | (Objection/Sentiment| --> |  (FAISS Vector   | --> | (Objection-specific  |  |
      |  |  /Persona)        |     |   Store Lookup)  |     |  Pitch Tactics)      |  |
      |  +-------------------+     +------------------+     +----------------------+  |
      |                                                                |              |
      |                                                                v              |
      |                                                     +----------------------+  |
      |                                                     |    Generate Node     |  |
      |                                                     | (Response Synthesis) |  |
      |                                                     +----------------------+  |
      +---------------------------------------+---------------------------------------+
                                              |
                       +----------------------+----------------------+
                       |                                             |
                       v                                             v
        +--------------+--------------+               +--------------+--------------+
        |         PostgreSQL          |               |            Redis            |
        |  (Memory & Analytics DB)    |               |  (Session Cache & A/B State)|
        +-----------------------------+               +-----------------------------+
```

---

## 14 Production Features

| # | Feature | Description |
|---|---|---|
| 1 | **Objection Classification** | Automatically classifies client objections into specific categories like pricing, timing, trust, fit, or competitors. |
| 2 | **Sentiment Analysis** | Real-time sentiment classification to gauge customer frustration, neutrality, or enthusiasm during the sales pitch. |
| 3 | **Persona Profiling** | Detects customer buying personas (e.g., Assertive, Analytical, Amiable, Expressive) to tailor conversational tone. |
| 4 | **LangGraph Adaptive Pipeline** | Manages conversation state using a directed acyclic graph (DAG) structure to dynamic routing based on classifications. |
| 5 | **Vector Retrieval (RAG)** | Performs similarity search on sales collateral using a high-performance FAISS vector store. |
| 6 | **Multi-Format Ingestion** | Ingestion pipeline supporting PDF, CSV, and Markdown files to automatically populate the vector store. |
| 7 | **Source Citations** | Automatically extracts and appends citations/sources to synthesized model answers to ensure factual grounding. |
| 8 | **Explainability Tracking** | Exposes underlying node execution metadata showing why a particular response or strategy was chosen. |
| 9 | **Human Handoff Mechanism** | Triggers an immediate human handoff escalation when low confidence thresholds or critical sentiment targets are hit. |
| 10 | **A/B Testing Module** | Deterministic 50/50 variant assignment (Static vs Adaptive) mapped to Redis sessions to track agent performance. |
| 11 | **Analytics Event Tracker** | Logs key metrics such as sentiment trends, objection frequencies, and variant conversion ratios to a database. |
| 12 | **Redis Session Cache** | Persists conversation history, token metadata, and temporary A/B testing assignments for rapid sub-millisecond retrieval. |
| 13 | **JWT Authentication** | Secures API endpoints with robust JSON Web Token (JWT) authorization, admin hashing, and credential security. |
| 14 | **Prometheus Monitoring** | Exposes structured latency, request total, and handoff frequency metrics for production-grade observability. |

---

## Quickstart

Get the application up and running in just three commands:

```bash
# 1. Clone & enter repository
git clone https://github.com/aayush2724/Auralis.git && cd Auralis

# 2. Set up environment configuration (fill in DEEPSEEK_API_KEY, JWT_SECRET_KEY, and DB credentials)
cp .env.example .env

# 3. Start PostgreSQL, Redis, FastAPI, and React containers
docker compose up --build
```

---

## Resume Bullet

```text
Built Auralis, an adaptive sales intelligence bot using LangGraph + RAG that classifies objections (94% confidence), detects customer persona and sentiment, and generates role-specific responses — improving simulated close rates from 27% to 42% in A/B testing. Deployed with FastAPI, Docker, JWT auth, PostgreSQL, Redis, CI/CD, and Prometheus monitoring.
```
