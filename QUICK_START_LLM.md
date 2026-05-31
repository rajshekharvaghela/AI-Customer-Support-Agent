# Quick Start Guide - LLM Configuration

## 🚀 Quick Setup (Choose One)

### Option A: Use Ollama Cloud (Free - Default)
```bash
# No setup needed! Just use .env.example as-is
cp .env.example .env
docker-compose up --build
```
✅ Works immediately  
❌ Requires Ollama Cloud account  

---

### Option B: Use ChatGPT (Recommended)
```bash
# 1. Get your OpenAI API key from https://platform.openai.com/api-keys
# 2. Edit .env:
OPENAI_API_KEY=sk-proj-YOUR_KEY_HERE
OPENAI_MODEL=gpt-4o-mini

# 3. Run
docker-compose up --build
```
✅ Fast, powerful, well-supported  
💰 Requires OpenAI account  

---

### Option C: Use Claude (Anthropic)
```bash
# 1. Get your Anthropic API key from https://console.anthropic.com/keys
# 2. Edit .env:
ANTHROPIC_API_KEY=sk-ant-YOUR_KEY_HERE
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022

# 3. Install (if not already):
pip install langchain-anthropic

# 4. Run
docker-compose up --build
```
✅ High quality responses  
💰 Requires Anthropic account  

---

## 🔄 How It Works

When your application starts:
1. ✅ Checks for `OPENAI_API_KEY` → uses ChatGPT
2. ✅ If not found, checks for `ANTHROPIC_API_KEY` → uses Claude
3. ✅ If not found, uses Ollama Cloud (default)
4. ❌ If all fail, shows error

**Result:** You can set multiple keys, and the app will use the first available one!

---

## 🧪 Test Your Setup

### Run the backend test:
```bash
cd /Users/rajvaghela/Desktop/E_commerce_project/AI-Customer-Support-Agent
source .venv/bin/activate
python3 backend/test.py
```

Expected output:
```
content="Hello! I'm doing well, thank you for asking. How can I help you today?" 
...
model='minimax-m2.5'  (or 'gpt-4-turbo', 'claude-3-5-sonnet', etc)
```

---

## 🔧 Troubleshooting

### "OPENAI_API_KEY not set in .env"
```bash
# Solution: Add your OpenAI key to .env
OPENAI_API_KEY=sk-proj-...
```

### "ANTHROPIC_API_KEY not set in .env"
```bash
# Solution: Add your Anthropic key to .env
ANTHROPIC_API_KEY=sk-ant-...
```

### "Failed to initialize any LLM client"
```bash
# Solution: Ensure at least one API key is set, or Ollama is running locally
# Check your .env file has one of:
# - OPENAI_API_KEY=...
# - ANTHROPIC_API_KEY=...
# - OLLAMA_CLOUD_API_KEY=...
```

### "Import 'langchain_anthropic' could not be resolved"
```bash
# This is just a linter warning. If you want to use Claude, install:
pip install langchain-anthropic
```

---

## 📊 Performance Comparison

| Provider | Speed | Cost | Quality | Setup |
|----------|-------|------|---------|-------|
| **ChatGPT** | ⚡⚡⚡ | $$$ | ⭐⭐⭐⭐ | 5 min |
| **Claude** | ⚡⚡ | $$ | ⭐⭐⭐⭐⭐ | 5 min |
| **Ollama** | ⚡⚡⚡⚡ | FREE | ⭐⭐⭐ | Instant |

---

## 📝 Environment Variables Reference

```bash
# OPTION 1: OpenAI / ChatGPT
OPENAI_API_KEY=sk-proj-...
OPENAI_MODEL=gpt-4o-mini  # or gpt-4, gpt-4-turbo

# OPTION 2: Anthropic / Claude
ANTHROPIC_API_KEY=sk-ant-...
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022

# OPTION 3: Ollama Cloud (always available as fallback)
OLLAMA_CLOUD_API_KEY=your_key_here
OLLAMA_MODEL=minimax-m2.5:cloud
OLLAMA_BASE_URL=https://api.ollama.com/v1

# ALWAYS REQUIRED
FASTAPI_HOST=0.0.0.0
FASTAPI_PORT=8000
BACKEND_URL=http://localhost:8000
```

---

## 🆘 Still Stuck?

1. Check your `.env` file has the right API key
2. Verify the API key is valid by testing on the provider's website
3. Check your internet connection
4. Try with Ollama Cloud (free fallback) to isolate the issue
5. Check `CHANGELOG_LLM_UPDATE.md` for detailed technical info

---

## 🎯 Next Steps

1. Choose your LLM provider (ChatGPT recommended)
2. Get an API key from the provider's website
3. Add it to your `.env` file
4. Run `docker-compose up --build`
5. Visit http://localhost:8501 for the frontend
6. Visit http://localhost:8000/docs for API docs

Enjoy! 🚀
