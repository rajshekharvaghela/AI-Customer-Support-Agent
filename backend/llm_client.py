"""LLM client configuration with support for ChatGPT, Claude, and Ollama."""

import os

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama

# Optional imports - will fail gracefully if packages not installed
try:
    from langchain_anthropic import ChatAnthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False

# Load .env file if it exists (for local development)
if os.path.exists(".env"):
    load_dotenv()


def _is_placeholder(value):
    """Check if a value is a placeholder (not configured)."""
    if not value:
        return True
    value_str = str(value).strip().lower()
    return value_str.startswith("your_") or value_str == "none"


def get_chatgpt_llm():
    """Initialize ChatGPT (OpenAI) LLM client."""
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if api_key == "" or not api_key or _is_placeholder(api_key):
        return None
    try:
        return ChatOpenAI(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            api_key=api_key,
            temperature=0.1,
        )
    except Exception as e:
        print(f"ChatGPT initialization failed: {e}")
        return None


def get_claude_llm():
    """Initialize Claude (Anthropic) LLM client."""
    if not HAS_ANTHROPIC:
        return None
    api_key = os.getenv("ANTHROPIC_API_KEY", "").strip()
    if api_key == "" or not api_key or _is_placeholder(api_key):
        return None
    try:
        return ChatAnthropic(
            model=os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022"),
            api_key=api_key,
            temperature=0.1,
        )
    except Exception as e:
        print(f"Claude initialization failed: {e}")
        return None


def get_ollama_llm():
    """Initialize Ollama LLM client (no API key needed)."""
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "minimax-m2.5:cloud")
    try:
        ollama_client = ChatOllama(model=OLLAMA_MODEL)
        return ollama_client
    except Exception as e:
        print(f"Ollama not available: {e}")
        return None


def get_dummy_llm():
    """Create a dummy LLM that returns fake responses."""
    class DummyLLM:
        def __init__(self):
            self.content = "No LLM provider available. Please configure OpenAI, Claude, or Ollama."
        
        def invoke(self, *args, **kwargs):
            """Return a mock response."""
            class Response:
                def __init__(self, content):
                    self.content = content
            return Response(self.content)
    
    return DummyLLM()


def get_llm():
    """Get the appropriate LLM client with fallback chain: ChatGPT -> Claude -> Ollama."""
    # Try ChatGPT first
    llm = get_chatgpt_llm()
    if llm:
        print("✓ Using ChatGPT LLM")
        return llm

    # Try Claude next
    llm = get_claude_llm()
    if llm:
        print("✓ Using Claude LLM")
        return llm

    # Try Ollama (always available if installed)
    llm = get_ollama_llm()
    if llm:
        print("✓ Using Ollama LLM")
        return llm
    
    # Fallback to dummy
    print("✗ No LLM available - using dummy mode")
    return get_dummy_llm()


# Initialize the LLM on module import
llm = get_llm()
