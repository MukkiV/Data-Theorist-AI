"""
config.py — Central configuration for Data Theorist AI.
All constants and environment variables are defined here.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ── API Keys ──────────────────────────────────────────────────────────────────
# Prioritize Streamlit Secrets for cloud deployment
try:
    import streamlit as st
    GROQ_API_KEY: str = st.secrets.get("GROQ_API_KEY", os.getenv("GROQ_API_KEY", ""))
except ImportError:
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")

# ── LLM Settings ─────────────────────────────────────────────────────────────
GROQ_MODEL: str = "llama-3.1-8b-instant"     # Free tier fast model
LLM_TEMPERATURE: float = 0.3                # Low temp = factual, consistent answers
LLM_MAX_TOKENS: int = 1024                  # Max tokens per response

# ── Embedding Settings ────────────────────────────────────────────────────────
EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"  # Lightweight, fast HuggingFace model

# ── Chunking Settings ─────────────────────────────────────────────────────────
CHUNK_SIZE: int = 500                        # Characters per chunk
CHUNK_OVERLAP: int = 50                      # Overlap between chunks

# ── Retriever Settings ────────────────────────────────────────────────────────
TOP_K_RESULTS: int = 5                       # Number of chunks to retrieve per query

# ── Memory Settings ───────────────────────────────────────────────────────────
MEMORY_WINDOW_K: int = 4                     # Keep last 4 conversation turns (≈ 3–5 rule)

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
