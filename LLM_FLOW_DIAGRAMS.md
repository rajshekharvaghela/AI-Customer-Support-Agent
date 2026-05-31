# LLM Provider Selection Flow Diagram

## 🔄 Application Startup Flow

```
┌─────────────────────────────────────────────────────────────────┐
│ Application Starts                                              │
│ (main.py / frontend/app.py imports backend.llm_client)         │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│ llm_client.py loads .env variables                              │
│ (load_dotenv() called)                                          │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│ get_llm() executes at module import                             │
│ Begins provider selection process                               │
└────────────────┬────────────────────────────────────────────────┘
                 │
         ┌───────┴──────────┐
         │                  │
         ▼                  ▼
    ┌─────────────┐   ┌──────────────────┐
    │ Check for   │   │                  │
    │ OPENAI_     │   │ Is key set?      │
    │ API_KEY     │   │                  │
    └─────┬───────┘   └──────┬───────────┘
          │                  │
     YES  │          NO      │
          │                  ▼
          ▼            ┌──────────────────┐
    ┌──────────────┐   │ Check for        │
    │ Try init     │   │ ANTHROPIC_       │
    │ ChatGPT      │   │ API_KEY          │
    └──┬───────────┘   └──────┬───────────┘
       │                      │
       │ ✅ Success           │
       │                 YES  │          NO
       │                      │
       │                      ▼
       │                 ┌──────────────┐
       │                 │ Try init     │
       │                 │ Claude       │
       │                 └──┬───────────┘
       │                    │
       │                    │ ✅ Success
       │                    │
       │                    ▼
       ├───────────────────────────┐
       │                           │
       ▼                           ▼
  ┌──────────────┐          ┌──────────────┐
  │ llm =        │          │ llm =        │
  │ ChatOpenAI() │          │ ChatAnthropic()
  │ (ChatGPT)    │          │ (Claude)     │
  └──────────────┘          └──────────────┘
       │                           │
       │                           ▼
       │                    ┌──────────────┐
       │                    │ No AI key?   │
       │                    │ Try Ollama   │
       │                    └──┬───────────┘
       │                       │
       │                       ▼
       │                  ┌──────────────────┐
       │                  │ llm =            │
       │                  │ ChatOllama()     │
       │                  │ (Ollama Cloud)   │
       │                  └──────┬───────────┘
       │                         │
       └──────────────┬──────────┘
                      │
                      ▼
        ┌─────────────────────────────┐
        │ llm object exported & ready │
        │ for use throughout app      │
        └────────────────┬────────────┘
                         │
                    ✅ SUCCESS
                         │
        ┌────────────────┴────────────────┐
        │                                 │
        ▼                                 ▼
    ┌──────────┐                    ┌────────────┐
    │ main.py  │                    │ nodes.py   │
    │          │                    │            │
    │ llm.     │                    │ llm.       │
    │ invoke() │                    │ invoke()   │
    └──────────┘                    └────────────┘
```

---

## 🎯 Provider Priority Order

```
┌──────────────────────────────────────────────────────────────────┐
│                     PRIORITY SELECTION                           │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1️⃣  ChatGPT (OpenAI)                                           │
│     ┌─────────────────────────────────────────────────────────┐ │
│     │ Fastest, most capable                                  │ │
│     │ Requires: OPENAI_API_KEY environment variable         │ │
│     │ Model: gpt-4o-mini (or gpt-4, gpt-4-turbo)           │ │
│     └─────────────────────────────────────────────────────────┘ │
│                          ↓                                       │
│     If no OPENAI_API_KEY, fall back to:                        │
│                          ↓                                       │
│  2️⃣  Claude (Anthropic)                                         │
│     ┌─────────────────────────────────────────────────────────┐ │
│     │ Highest quality responses                              │ │
│     │ Requires: ANTHROPIC_API_KEY environment variable      │ │
│     │ Model: claude-3-5-sonnet-20241022                     │ │
│     └─────────────────────────────────────────────────────────┘ │
│                          ↓                                       │
│     If no ANTHROPIC_API_KEY, fall back to:                     │
│                          ↓                                       │
│  3️⃣  Ollama Cloud (MiniMax)                                     │
│     ┌─────────────────────────────────────────────────────────┐ │
│     │ Free, always available                                 │ │
│     │ Optional: OLLAMA_CLOUD_API_KEY                         │ │
│     │ Model: minimax-m2.5:cloud                             │ │
│     │ Also: supports local Ollama installation              │ │
│     └─────────────────────────────────────────────────────────┘ │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

---

## 🔌 Module Import & Usage

```
┌─────────────────────────────────────────────────────────────────┐
│ backend/main.py                                                 │
│ ───────────────────────────────────────────────────────────────│
│ from backend.llm_client import llm                              │
│                                                                 │
│ @app.post("/api/chat")                                          │
│ async def chat(request: ChatRequest):                           │
│     response = llm.invoke([...])  # ✅ Works with any provider │
│     return response                                             │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ backend/agent/nodes.py                                          │
│ ───────────────────────────────────────────────────────────────│
│ from backend.llm_client import llm                              │
│                                                                 │
│ def llm_reasoning_node(state: AgentState):                      │
│     response = llm.invoke([...])  # ✅ Works with any provider │
│     return response                                             │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ backend/test.py                                                 │
│ ───────────────────────────────────────────────────────────────│
│ from llm_client import llm                                      │
│                                                                 │
│ response = llm.invoke("Hello, how are you?")                   │
│ print(response)  # ✅ Works with any provider                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🐛 Chat Badge Fix - Before vs After

### ❌ BEFORE: All Messages Get Badges

```
┌─────────────────────────────────────┐
│ USER: "Why can't my refund process?" │
└─────────────────────────────────────┘
             ▼
┌─────────────────────────────────────┐
│ ASSISTANT: "Could you provide...?"   │
│ (decision: "APPROVED")                │
│ 🟢 APPROVED ← ❌ WRONG! Not a refund │
└─────────────────────────────────────┘
             ▼
┌─────────────────────────────────────┐
│ USER: "ORD_1009"                     │
└─────────────────────────────────────┘
             ▼
┌─────────────────────────────────────┐
│ ASSISTANT: "I found your order..."   │
│ (decision: "APPROVED")                │
│ 🟢 APPROVED ← ❌ WRONG! Not a refund │
└─────────────────────────────────────┘
             ▼
┌─────────────────────────────────────┐
│ USER: "Help me cancel instead"       │
└─────────────────────────────────────┘
             ▼
┌─────────────────────────────────────┐
│ ASSISTANT: "Sure! Here's how..."     │
│ (decision: "APPROVED")                │
│ 🟢 APPROVED ← ❌ WRONG! Not a refund │
└─────────────────────────────────────┘
```

### ✅ AFTER: Only Refund Decisions Get Badges

```
┌─────────────────────────────────────┐
│ USER: "Why can't my refund process?" │
└─────────────────────────────────────┘
             ▼
┌─────────────────────────────────────┐
│ ASSISTANT: "Could you provide...?"   │
│ (is_refund_decision: false)           │
│ [No Badge] ✅ CORRECT!              │
└─────────────────────────────────────┘
             ▼
┌─────────────────────────────────────┐
│ USER: "ORD_1009"                     │
└─────────────────────────────────────┘
             ▼
┌─────────────────────────────────────┐
│ ASSISTANT: "I found your order..."   │
│ (is_refund_decision: false)           │
│ [No Badge] ✅ CORRECT!              │
└─────────────────────────────────────┘
             ▼
┌─────────────────────────────────────┐
│ USER: "Help me cancel instead"       │
└─────────────────────────────────────┘
             ▼
┌─────────────────────────────────────┐
│ ASSISTANT: "Sure! Here's how..."     │
│ (is_refund_decision: false)           │
│ [No Badge] ✅ CORRECT!              │
└─────────────────────────────────────┘

BUT WHEN ACTUAL REFUND IS PROCESSED:
             ▼
┌──────────────────────────────────────────┐
│ REFUND DECISION MADE:                    │
│ "Your refund has been approved..."       │
│ (is_refund_decision: true)                │
│ 🟢 APPROVED ✅ CORRECT!                  │
└──────────────────────────────────────────┘
```

---

## 📊 Configuration Options Matrix

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         CONFIGURATION MATRIX                                │
├──────────────────┬──────────────┬──────────────┬──────────────┬──────────────┤
│ Scenario         │ OPENAI_KEY   │ ANTHROPIC_KEY│ OLLAMA_KEY   │ Provider Used│
├──────────────────┼──────────────┼──────────────┼──────────────┼──────────────┤
│ ChatGPT Only     │ ✅           │ ❌           │ ❌           │ 🟢 ChatGPT   │
├──────────────────┼──────────────┼──────────────┼──────────────┼──────────────┤
│ Claude Only      │ ❌           │ ✅           │ ❌           │ 🔵 Claude    │
├──────────────────┼──────────────┼──────────────┼──────────────┼──────────────┤
│ Ollama Only      │ ❌           │ ❌           │ ✅ or empty  │ ⚫ Ollama     │
├──────────────────┼──────────────┼──────────────┼──────────────┼──────────────┤
│ ChatGPT+Claude   │ ✅           │ ✅           │ ❌ or ✅     │ 🟢 ChatGPT*  │
│ (ChatGPT wins)   │              │              │              │              │
├──────────────────┼──────────────┼──────────────┼──────────────┼──────────────┤
│ ChatGPT+Ollama   │ ✅           │ ❌           │ ✅           │ 🟢 ChatGPT*  │
│ (ChatGPT wins)   │              │              │              │              │
├──────────────────┼──────────────┼──────────────┼──────────────┼──────────────┤
│ Claude+Ollama    │ ❌           │ ✅           │ ✅           │ 🔵 Claude*   │
│ (Claude wins)    │              │              │              │              │
├──────────────────┼──────────────┼──────────────┼──────────────┼──────────────┤
│ All Three        │ ✅           │ ✅           │ ✅           │ 🟢 ChatGPT*  │
│ (ChatGPT wins)   │              │              │              │              │
├──────────────────┼──────────────┼──────────────┼──────────────┼──────────────┤
│ None Set         │ ❌           │ ❌           │ ❌           │ ⚫ Ollama     │
│ (Ollama fallback)│              │              │              │ (local)      │
└──────────────────┴──────────────┴──────────────┴──────────────┴──────────────┘

Legend:
  ✅ = Environment variable is set
  ❌ = Environment variable is not set
  * = Highest priority is used (others ignored)
  ⚫ = Falls back to local Ollama if available
```

---

## 🔄 Error Handling Flow

```
┌─────────────────────────────────┐
│ Try ChatGPT                     │
└──────────────┬──────────────────┘
               │
        ❌ Error / Missing Key
               │
               ▼
┌─────────────────────────────────┐
│ Try Claude                      │
└──────────────┬──────────────────┘
               │
        ❌ Error / Missing Key
               │
               ▼
┌─────────────────────────────────┐
│ Try Ollama Cloud                │
└──────────────┬──────────────────┘
               │
        ❌ Error / Missing Key
               │
               ▼
┌──────────────────────────────────┐
│ Try Local Ollama                 │
└──────────────┬───────────────────┘
               │
        ❌ Error / Not Running
               │
               ▼
┌──────────────────────────────────┐
│ ❌ RAISE ERROR                   │
│ "Failed to initialize any LLM"   │
│                                  │
│ User sees helpful message:       │
│ "Please set OPENAI_API_KEY,      │
│  ANTHROPIC_API_KEY, or ensure    │
│  Ollama is running"              │
└──────────────────────────────────┘
```

---

## 🎯 Key Improvements Summary

```
┌──────────────────────────────────────────────────────────────────────┐
│                          IMPROVEMENTS                                │
├──────────────────────────────────────────────────────────────────────┤
│                                                                      │
│ BEFORE                              AFTER                           │
│ ──────────────────────────────────────────────────────────────────  │
│                                                                      │
│ 1 LLM provider (Ollama)      →      3 LLM providers               │
│ No API key flexibility       →      Flexible API key support      │
│ Fixed provider              →      Automatic selection            │
│ No fallback logic           →      Priority-based fallback        │
│ Badge on all chat           →      Badge only on refunds          │
│ Manual provider switching   →      Automatic provider selection   │
│ Limited documentation       →      Comprehensive guides           │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
```
