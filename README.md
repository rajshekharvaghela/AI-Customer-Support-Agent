# Worknoon AI Refund Agent

A production-ready, fully containerized AI customer support agent that processes refund requests using deterministic policy enforcement and LangGraph orchestration, powered by MiniMax-M2.5 via Ollama Cloud.

![Screenshot Placeholder](docs/screenshot.png)

## Project Overview

The Worknoon AI Refund Agent automates refund decision-making for an e-commerce platform. It reads customer order data from a mock CRM (JSON), applies strict corporate refund policy rules, and escalates edge cases to an LLM only when needed. A Streamlit frontend provides customer chat and an admin reasoning dashboard.

## Architecture Overview

The agent uses a 4-node LangGraph pipeline:

```
┌─────────────┐     ┌──────────────────┐     ┌─────────────────┐     ┌──────────────────┐
│  load_data  │────▶│ validate_request │────▶│  llm_reasoning  │────▶│ format_response  │
│             │     │  (deterministic) │     │  (if PENDING)   │     │                  │
└─────────────┘     └────────┬─────────┘     └─────────────────┘     └──────────────────┘
                             │
                             │ (APPROVED / DENIED / ESCALATED)
                             ▼
                    ┌──────────────────┐
                    │ format_response  │────▶ END
                    └──────────────────┘
```

1. **load_data** — Fetches customer, order, policy, and refund history from JSON files.
2. **validate_request** — Runs all deterministic policy checks (windows, final sale, amount routing, abuse).
3. **llm_reasoning** — Only invoked for ambiguous `PENDING` cases; uses MiniMax-M2.5 via Ollama Cloud.
4. **format_response** — Generates a professional customer-facing message.

## Tech Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Frontend | Streamlit | Customer chat + admin dashboard |
| Backend | FastAPI + Uvicorn | REST API |
| Agent | LangGraph StateGraph | Orchestration pipeline |
| LLM | MiniMax-M2.5 (Ollama Cloud) | Ambiguous case reasoning |
| Data | JSON flat files | Mock CRM + policy |
| Containers | Docker Compose (ARM64) | Mac Silicon deployment |

## Quick Start (Docker)

```bash
git clone <repo>
cd AI-Customer-Support-Agent
cp .env.example .env
# Edit .env and add your OLLAMA_CLOUD_API_KEY
docker-compose up --build
```

- **Frontend:** http://localhost:8501
- **Backend API:** http://localhost:8000/docs

## Getting Your API Key

1. Go to [ollama.com](https://ollama.com) and sign up (no credit card required).
2. Navigate to **Settings → API Keys**.
3. Click **Create API Key** and copy the key.
4. Paste it into your `.env` file as `OLLAMA_CLOUD_API_KEY=your_key_here`.

## Using a Different LLM

The agent uses LangChain's OpenAI-compatible client. Change these environment variables:

| Provider | OLLAMA_BASE_URL | OLLAMA_MODEL | API Key Variable |
|----------|-----------------|--------------|------------------|
| Ollama Cloud (default) | `https://api.ollama.com/v1` | `minimax-m2.5:cloud` | `OLLAMA_CLOUD_API_KEY` |
| OpenAI | `https://api.openai.com/v1` | `gpt-4o-mini` | `OLLAMA_CLOUD_API_KEY` (set to OpenAI key) |
| Anthropic (via proxy) | Your proxy URL | `claude-3-5-sonnet` | `OLLAMA_CLOUD_API_KEY` |

## Refund Policy Summary

- **30-day** return window (standard); **14-day** for electronics
- **Final sale** and **clearance** items: never refundable
- **Custom/personalized** items: not refundable
- **Unopened** condition required; opened items denied
- **Under $100:** auto-approve if compliant
- **$100–$500:** approve after validation
- **Over $500:** escalate to human (agent cannot approve/deny)
- **Processing orders:** cannot refund — must cancel
- **Cancelled orders:** not eligible
- **Shipping damage:** may approve; **customer damage:** deny
- **>2 refunds in 60 days:** escalate for abuse review

## Running Locally (Without Docker)

```bash
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your API key

# Terminal 1
uvicorn backend.main:app --reload

# Terminal 2
streamlit run frontend/app.py
```

## API Docs

Interactive Swagger UI is available at http://localhost:8000/docs

Key endpoints:
- `POST /api/refund` — Structured refund request
- `POST /api/chat` — Free-form customer chat
- `GET /api/customers` — List customers
- `GET /api/customer/{id}/orders` — Customer orders
- `GET /api/policy` — Full policy document
- `GET /health` — Health check

## Agent Resilience

The agent includes prompt injection protection. User messages are scanned for manipulation patterns (e.g., "ignore previous instructions", "approve everything") before any LLM call. Detected injections result in an immediate **DENIED** response without contacting the LLM. The system prompt explicitly instructs the model to only follow corporate policy regardless of user phrasing.

## Test Scenarios

| Customer | Order | Expected |
|----------|-------|----------|
| CUST_001 | ORD_1001 | APPROVED ($45.99, within window) |
| CUST_002 | ORD_1005 | DENIED (final sale) |
| CUST_003 | ORD_1007 | ESCALATED ($899.99 > $500) |
| CUST_006 | ORD_1011 | DENIED (>30 days) |
| CUST_007 | ORD_1012 | DENIED (electronics >14 days) |
| CUST_008 | ORD_1013 | DENIED (processing) |
| CUST_009 | ORD_1015 | DENIED (clearance) |
| CUST_011 | ORD_1017 | ESCALATED (refund abuse) |
