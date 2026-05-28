from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="AI Customer Support Agent",
    description="Refund Processing Agent API",
    version="1.0.0"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For local dev; restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

@app.post("/api/chat")
async def chat_endpoint(user_message: str, conversation_id: str = None):
    """
    Main chat endpoint for refund requests
    """
    # TODO: Integrate with LangGraph agent
    return {
        "response": "Agent response pending implementation",
        "reasoning": "Internal agent reasoning logs",
        "decision": "PENDING"
    }

@app.get("/api/reasoning/{conversation_id}")
async def get_reasoning(conversation_id: str):
    """
    Retrieve agent's internal reasoning logs
    """
    # TODO: Fetch reasoning logs from database
    return {"conversation_id": conversation_id, "logs": []}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=os.getenv("FASTAPI_HOST", "0.0.0.0"),
        port=int(os.getenv("FASTAPI_PORT", 8000)),
        reload=True
    )