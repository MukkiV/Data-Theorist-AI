"""
config.py — Central configuration for Data Theorist AI.
All constants and environment variables are defined here.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ── API Keys ──────────────────────────────────────────────────────────────────
# Prioritize environment variables (.env), fallback to Streamlit Secrets
GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")

# If not found in .env, try Streamlit (only if running as a web app)
if not GROQ_API_KEY:
    try:
        import streamlit as st
        # st.runtime.exists() is the safest way to check if we're in the app
        if st.runtime.exists():
            GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", "")
    except Exception:
        # Silently fail if streamlit isn't fully initialized
        pass

# ── LLM Settings ─────────────────────────────────────────────────────────────
GROQ_MODEL: str = "llama-3.1-8b-instant"     # Free tier fast model
LLM_TEMPERATURE: float = 0.3                # Low temp = factual, consistent answers
LLM_MAX_TOKENS: int = 1024                  # Max tokens per response

# ── Embedding Settings ────────────────────────────────────────────────────────
EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"  # Lightweight, fast HuggingFace model

# ── Chunking Settings ─────────────────────────────────────────────────────────
CHUNK_SIZE: int = 600                        # Characters per chunk (≈150 tokens)
CHUNK_OVERLAP: int = 100                     # Improved overlap for continuity

# ── Retriever Settings ────────────────────────────────────────────────────────
TOP_K_RESULTS: int = 4                       # Reduced but more precise results

# ── Memory Settings ───────────────────────────────────────────────────────────
MEMORY_MAX_TOKENS: int = 1500                # Summarize when history > 1500 tokens

# ── File Paths ────────────────────────────────────────────────────────────────
BOOKS_DIR: str = "books"                     # Directory containing PDF books
VECTOR_STORE_DIR: str = "vector_store"       # Directory to persist FAISS index

# ── Book Metadata ─────────────────────────────────────────────────────────────
BOOK_NAMES: dict[str, str] = {
    "machine_learning": "Machine Learning",
    "python": "Python Programming",
    "sql": "SQL & Databases",
    "statistics": "Statistics",
    "story_telling": "Data Storytelling",
}
