"""LLM client configuration for Ollama Cloud (OpenAI-compatible)."""

import os

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

llm = ChatOpenAI(
    model=os.getenv("OLLAMA_MODEL", "minimax-m2.5:cloud"),
    base_url=os.getenv("OLLAMA_BASE_URL", "https://api.ollama.com/v1"),
    api_key=os.getenv("OLLAMA_CLOUD_API_KEY", "not-set"),
    temperature=0.1,
)
