# Auralis 🎙️

> **Adaptive Sales Intelligence Bot** — RAG-powered objection handling with real-time strategy switching.

---

## Architecture

```
auralis/
├── data/                  # Raw knowledge-base files (.pdf, .csv, .md)
├── vectorstore/           # Persisted FAISS index (git-ignored)
├── src/
│   ├── rag/               # Ingestion + retrieval pipeline
│   ├── classifier/        # Objection / persona / sentiment classifiers
│   ├── strategies/        # One file per pitch strategy module
│   ├── memory/            # ConversationMemory + PostgreSQL adapter
│   ├── graph/             # LangGraph nodes + edges
│   ├── api/               # FastAPI routers
│   └── utils/             # Confidence, explainability, citations
├── tests/
├── docker-compose.yml
├── .env.example
└── requirements.txt
```

---

## Quick Start

### 1. Clone & install
```bash
git clone https://github.com/your-org/auralis.git
cd auralis
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure environment
```bash
cp .env.example .env
# Fill in OPENAI_API_KEY and DB credentials
```

### 3. Start services
```bash
docker-compose up -d postgres redis
```

### 4. Ingest knowledge base
```bash
python -m src.rag.ingest --dir data/
```

### 5. Run the API
```bash
uvicorn src.api.main:app --reload
```

### 6. Run tests
```bash
pytest tests/ -v
```

---

## Key Features

| # | Feature |
|---|---------|
| 11 | Source citations in every response |
| 12 | PDF / CSV / Markdown knowledge-base ingestion |
| … | *(more coming in Day 2+)* |

---

## Day 1 Deliverables

- [x] Repository scaffold
- [x] `src/rag/ingest.py` — knowledge-base ingestion pipeline
- [x] `src/rag/retriever.py` — FAISS retriever with source tracking
- [x] `tests/test_retriever.py` — end-to-end pytest suite
