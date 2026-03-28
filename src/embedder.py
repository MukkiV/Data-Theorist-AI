"""
embedder.py — Handles PDF loading and FAISS vector store creation.
Run this module's logic via ingest.py (one-time only).
"""

import os
import logging
from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

from src.config import (
    BOOKS_DIR,
    VECTOR_STORE_DIR,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
    EMBEDDING_MODEL,
    BOOK_NAMES,
)

logger = logging.getLogger(__name__)


def get_embedding_model() -> HuggingFaceEmbeddings:
    """Load and return the HuggingFace embedding model.

    Returns:
        HuggingFaceEmbeddings: The embedding model instance.
    """
    logger.info(f"Loading embedding model: {EMBEDDING_MODEL}")
    return HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)


def load_pdfs() -> list:
    """Load all PDF books from the books directory with source metadata.

    Returns:
        list: A flat list of LangChain Document objects with metadata.

    Raises:
        FileNotFoundError: If the books directory does not exist.
    """
    books_path = Path(BOOKS_DIR)
    if not books_path.exists():
        raise FileNotFoundError(f"Books directory not found: {BOOKS_DIR}")

    all_docs = []
    pdf_files = list(books_path.glob("*.pdf"))

    if not pdf_files:
        raise FileNotFoundError(f"No PDF files found in: {BOOKS_DIR}")

    for pdf_file in pdf_files:
        book_key = pdf_file.stem  # filename without extension
        book_display_name = BOOK_NAMES.get(book_key, book_key.replace("_", " ").title())

        logger.info(f"Loading: {book_display_name} ({pdf_file.name})")
        loader = PyPDFLoader(str(pdf_file))
        docs = loader.load()

        # Attach book name to every page's metadata
        for doc in docs:
            doc.metadata["source"] = book_display_name
            doc.metadata["file"] = pdf_file.name

        all_docs.extend(docs)
        logger.info(f" → Loaded {len(docs)} pages from {book_display_name}")

    logger.info(f"Total pages loaded: {len(all_docs)}")
    return all_docs


def split_documents(docs: list) -> list:
    """Split documents into smaller chunks for embedding.

    Args:
        docs: List of LangChain Document objects.

    Returns:
        list: List of chunked Document objects (sanitized).
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=len,
    )
    chunks = splitter.split_documents(docs)

    # Sanitize: remove chunks with empty/None/non-string content
    # (common with image-heavy PDF pages)
    valid_chunks = []
    for chunk in chunks:
        content = chunk.page_content
        # Ensure content is a non-null string
        if content is None or not isinstance(content, (str, bytes)):
            continue
        
        # Cast to string and sanitize characters
        if isinstance(content, bytes):
            content = content.decode('utf-8', errors='ignore')
        else:
            # Remove surrogates and non-encodable characters that trip up the tokenizer
            # This handles mathematical symbols and other complex PDF extractions
            content = content.encode('utf-8', 'ignore').decode('utf-8')
            # Specifically strip half-surrogates (U+D800 to U+DFFF)
            content = ''.join(c for c in content if not (0xD800 <= ord(c) <= 0xDFFF))

        # Basic cleaning
        content = content.strip()
        
        # Filter out chunks that are practically empty or consist only of whitespace/noise
        if len(content) < 20: 
            continue
            
        chunk.page_content = str(content) # Strong cast to string
        valid_chunks.append(chunk)

    skipped = len(chunks) - len(valid_chunks)
    if skipped:
        logger.warning(f"Skipped {skipped} invalid/empty chunks during sanitization.")
    logger.info(f"Total valid chunks for embedding: {len(valid_chunks)}")
    return valid_chunks


def build_vector_store(chunks: list, embeddings: HuggingFaceEmbeddings) -> FAISS:
    """Build and persist a FAISS vector store from document chunks.

    Args:
        chunks: List of chunked Document objects.
        embeddings: The embedding model to use.

    Returns:
        FAISS: The built vector store.
    """
    logger.info("Building FAISS vector store...")
    vector_store = FAISS.from_documents(chunks, embeddings)

    os.makedirs(VECTOR_STORE_DIR, exist_ok=True)
    vector_store.save_local(VECTOR_STORE_DIR)
    logger.info(f"Vector store saved to: {VECTOR_STORE_DIR}/")

    return vector_store


def load_vector_store(embeddings: HuggingFaceEmbeddings) -> FAISS:
    """Load a pre-built FAISS vector store from disk.

    Args:
        embeddings: The embedding model (must match the one used during ingestion).

    Returns:
        FAISS: The loaded vector store.

    Raises:
        FileNotFoundError: If vector store does not exist on disk.
    """
    if not Path(VECTOR_STORE_DIR).exists():
        raise FileNotFoundError(
            f"Vector store not found at '{VECTOR_STORE_DIR}/'. "
            "Please run: python ingest.py"
        )
    logger.info(f"Loading vector store from: {VECTOR_STORE_DIR}/")
    return FAISS.load_local(
        VECTOR_STORE_DIR,
        embeddings,
        allow_dangerous_deserialization=True,
    )
