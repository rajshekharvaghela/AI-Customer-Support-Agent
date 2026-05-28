# AI Customer Support Refund Agent

An intelligent system for processing e-commerce refunds using LangGraph agents and local LLMs.

## Features
- 🤖 Autonomous refund decision-making using LangGraph
- 💬 Customer-facing chat interface (Streamlit)
- 📊 Admin dashboard with agent reasoning logs
- 🔒 Policy-compliant decision making
- 🚀 Single-command deployment with Docker

## Architecture

### System Components
1. **Streamlit Frontend** - Customer chat interface + admin dashboard
2. **FastAPI Backend** - REST API for agent orchestration
3. **LangGraph Agent** - Autonomous decision-making loop
4. **Ollama LLM** - Local language model for reasoning
5. **Mock Database** - Synthetic customer & order data

## Prerequisites
- Docker & Docker Compose
- Python 3.11+ (for local development)
- Ollama installed on host machine (for local testing)

## Quick Start

### Option 1: Docker Compose (Recommended)

```bash
# Clone the repository
git clone git@github.com:YOUR_USERNAME/E_Commerce_Refund_Agent.git
cd E_Commerce_Refund_Agent

# Start all services
docker-compose up --build

# Access the application
- Frontend: http://localhost:8501
- Backend API: http://localhost:8000
- Ollama: http://localhost:11434
```

### Option 2: Local Development

```bash
# Clone repository
git clone git@github.com:YOUR_USERNAME/E_Commerce_Refund_Agent.git
cd E_Commerce_Refund_Agent

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Ensure Ollama is running
ollama serve

# In separate terminals:

# Terminal 1: Start backend
cd backend
python -m uvicorn main:app --reload

# Terminal 2: Start frontend
streamlit run frontend/app.py
```

## Configuration

### Environment Variables
Copy `.env.example` to `.env` and update:
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=mistral  # or your chosen model
FASTAPI_PORT=8000
STREAMLIT_SERVER_PORT=8501

### Ollama Model Setup
```bash
# Pull a model (first time only)
ollama pull mistral
# or
ollama pull neural-chat
```

## API Endpoints

### POST /api/chat
Submit a refund request to the agent

**Request:**
```json
{
  "customer_id": "CUST_001",
  "order_id": "ORD_12345",
  "user_message": "I want a refund for my broken shoes"
}
```

**Response:**
```json
{
  "response": "Agent's natural language response",
  "decision": "APPROVED|DENIED|ESCALATED",
  "reasoning": "Internal decision reasoning",
  "confidence": 0.95
}
```

### GET /api/reasoning/{conversation_id}
Retrieve agent's internal reasoning logs for a decision

## Project Structure
├── backend/           # FastAPI application
│   ├── agent/        # LangGraph agent logic
│   ├── database/     # Mock CRM data
│   ├── policy/       # Refund policy engine
│   └── models/       # Pydantic schemas
├── frontend/          # Streamlit app
│   ├── app.py        # Main interface
│   └── pages/        # Multi-page components
├── data/             # Synthetic datasets
├── docker/           # Container definitions
├── docker-compose.yml
└── requirements.txt

## Testing

```bash
# Run unit tests
pytest tests/

# Run specific test file
pytest tests/test_agent.py -v

# Run with coverage
pytest --cov=backend tests/
```

## Development Workflow

1. **Activate virtual environment**
```bash
   source venv/bin/activate
```

2. **Install new dependencies**
```bash
   pip install package_name
   pip freeze > requirements.txt
```

3. **Make changes and test locally**
```bash
   pytest
```

4. **Commit and push**
```bash
   git add .
   git commit -m "Feature: description"
   git push origin main
```

## Performance Considerations
- Ollama model response time: ~2-5 seconds
- Agent loop execution: ~5-10 seconds total
- Streamlit page load: ~1-2 seconds

## Known Limitations
- Local Ollama models may have lower reasoning accuracy than GPT-4/Claude
- Mock database is static (no persistence)
- Single-threaded agent loop (can add async support if needed)

## Future Enhancements
- WebSocket support for real-time chat streaming
- Database persistence with PostgreSQL
- Multi-language support
- Advanced analytics dashboard
- A/B testing framework for policy variations

## Troubleshooting

**Docker build fails:**
```bash
docker-compose down -v
docker-compose build --no-cache
docker-compose up
```

**Ollama connection error:**
Ensure Ollama service is running: `ollama serve` or check `http://localhost:11434`

**Port already in use:**
```bash
# Kill process on port 8000 (macOS)
lsof -ti:8000 | xargs kill -9
```

## Support
For questions, please refer to the Worknoon interview instructions or open a GitHub issue.

---

**Submission**: Please ensure all tests pass and documentation is complete before submitting.
