# 🧠 SKILLS.md — Data Theorist AI (RAG-Based Learning Assistant)

> These are the **core rules, design principles, and developer guidelines** for this project.
> Every contributor (or AI assistant) must follow these strictly.

---

## 🎯 Project Mission

Build a **production-quality, modular AI tutor** that teaches Data Science concepts using:
- Multiple PDF books as the knowledge base
- RAG (Retrieval-Augmented Generation) for accurate answers
- Groq API as the LLM backbone
- Streamlit as the conversational UI

---

## 📁 Project Structure Rules

```
data_theorist_ai/
├── books/                  # PDF knowledge base (never commit large PDFs to git)
├── vector_store/           # Persisted FAISS index (auto-created on first run)
├── src/
│   ├── config.py           # All configuration & constants
│   ├── embedder.py         # PDF loading + FAISS vector store builder
│   ├── retriever.py        # Context retrieval logic
│   ├── memory.py           # Conversational memory (last 3–5 turns)
│   ├── prompt.py           # Teaching-style prompt templates
│   ├── chain.py            # LangChain RAG chain assembly
│   └── token_tracker.py    # Token usage tracking (per message + session)
├── app.py                  # Streamlit UI entry point
├── ingest.py               # One-time PDF ingestion script
├── .env                    # API keys (never commit)
├── requirements.txt        # Dependencies
├── SKILLS.md               # This file — rules & guidelines
└── README.md               # Project documentation
```

---

## 🔒 Immutable Design Rules

### 1. No Re-Embedding on Every Run
- Embeddings are created **once** via `ingest.py`
- The FAISS vector store is **persisted to disk** in `vector_store/`
- `app.py` **only loads** the existing index — never rebuilds it unless forced

### 2. Teaching Format is Mandatory
Every AI response must follow this structured format:

```
📘 Definition
   Clear, simple definition of the concept

💡 Intuition
   Real-world analogy or layman explanation

🧪 Example
   Code snippet or concrete example

📝 Notes
   Key takeaways, edge cases, or tips

📚 Source
   Book name and chapter (if available)
```

### 3. Modular Code Only
- No monolithic files. Each `src/` module has **one responsibility**.
- Cross-module imports go top-down (config → embedder → retriever → chain → app)
- Never import `app.py` from within `src/`

### 4. Groq API is the ONLY LLM
- Model: `llama3-8b-8192` (fast), or `llama3-70b-8192` (powerful)
- All LLM calls go through **LangChain's ChatGroq wrapper**
- No OpenAI, Anthropic, or other LLM imports

### 5. Memory is Bounded
- Keep only the **last 3–5 conversation turns** in memory
- Memory is session-scoped (resets on app reload)
- Use `ConversationBufferWindowMemory` from LangChain

### 6. Source Attribution is Required
- Every answer must cite the **book name** it was retrieved from
- Retriever must return document metadata with `source` field
- Display source in the response footer

---

## 🧑‍💻 Coding Standards

| Standard | Rule |
|---|---|
| Language | Python 3.10+ |
| Style | PEP 8, max 100 chars per line |
| Docstrings | Google-style on all public functions |
| Type hints | Required on all function signatures |
| Error handling | All LLM/API calls wrapped in `try/except` |
| Env vars | Read via `python-dotenv`, never hardcoded |
| Logging | Use Python `logging` module (not `print`) |
| Constants | ALL_CAPS in `config.py` only |

---

## 🚀 Performance Rules

- **Vector store loads once** per app session (cached with `@st.cache_resource`)
- Retriever returns **top-K=5** most relevant chunks by default
- Chunk size: **500 tokens**, chunk overlap: **50 tokens**
- Groq API calls are async-friendly but sync in MVP

---

## 🔐 Security Rules

- `.env` is **always in `.gitignore`**
- `vector_store/` is in `.gitignore` (rebuild from PDFs)
- `books/` is in `.gitignore` (large binaries — share separately)
- Never log or display raw API keys

---

## 📦 Dependency Rules

- Pin all versions in `requirements.txt`
- Prefer LangChain ecosystem for consistency
- Minimize external dependencies — no unused packages

---

## 🧪 Testing Guidelines

- Test retriever with at least 3 known questions per book
- Verify memory is correctly bounded (not exceeding 5 turns)
- Confirm token tracker increments correctly
- Validate teaching format is present in every response

---

## 🤝 Contribution Protocol

1. Read `SKILLS.md` before writing a single line of code
2. Follow the module structure — do NOT add logic to `app.py`
3. All new features need a corresponding config entry in `config.py`
4. Run `ingest.py` after adding new books
5. Test locally before pushing

---

*Last updated: March 2026 | Maintained by the Data Theorist AI team*
