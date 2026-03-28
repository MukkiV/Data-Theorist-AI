"""
ingest.py — One-time PDF ingestion script.
Run this ONCE to build the FAISS vector store from your PDF books.

Usage:
    python ingest.py
"""

import logging
import sys
from pathlib import Path

# Configure logging before importing project modules
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("ingest")


def main() -> None:
    """Main ingestion pipeline: load PDFs → chunk → embed → save."""
    from src.embedder import get_embedding_model, load_pdfs, split_documents, build_vector_store
    from src.config import VECTOR_STORE_DIR

    # Guard: warn if vector store already exists
    if Path(VECTOR_STORE_DIR).exists():
        logger.warning(
            f"Vector store already exists at '{VECTOR_STORE_DIR}/'.\n"
            "Delete it manually if you want to re-embed."
        )
        confirm = input("Re-embed anyway? (yes/no): ").strip().lower()
        if confirm != "yes":
            logger.info("Ingestion cancelled. Using existing vector store.")
            sys.exit(0)

    try:
        logger.info("=" * 55)
        logger.info("  Data Theorist AI — PDF Ingestion Pipeline")
        logger.info("=" * 55)

        # Step 1: Load embedding model
        embeddings = get_embedding_model()

        # Step 2: Load all PDFs
        docs = load_pdfs()

        # Step 3: Split into chunks
        chunks = split_documents(docs)

        # Step 4: Build and save vector store
        build_vector_store(chunks, embeddings)

        logger.info("=" * 55)
        logger.info("  ✅ Ingestion complete! Vector store is ready.")
        logger.info("  👉 Now run: streamlit run app.py")
        logger.info("=" * 55)

    except FileNotFoundError as e:
        logger.error(f"❌ {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
