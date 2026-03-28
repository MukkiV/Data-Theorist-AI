"""
retriever.py — Handles document retrieval from the FAISS vector store.
Returns optimized, diverse, and compressed chunks.
"""

import logging
from langchain_community.vectorstores import FAISS
from langchain_classic.schema import Document
from langchain_classic.retrievers import ContextualCompressionRetriever
from langchain_classic.retrievers.document_compressors import EmbeddingsFilter

from src.config import TOP_K_RESULTS

logger = logging.getLogger(__name__)


def get_optimized_retriever(vector_store: FAISS, embeddings):
    """Create an optimized retriever with MMR and Contextual Compression.

    MMR (Maximum Marginal Relevance) ensures we get diverse chunks,
    avoiding redundant information. Contextual Compression filters
    out chunks that don't meet a relevance threshold.

    Args:
        vector_store: A loaded FAISS vector store instance.
        embeddings: The embedding model for compression filtering.

    Returns:
        ContextualCompressionRetriever: A precision-tuned retriever.
    """
    # 1. Base retriever with MMR for diversity
    base_retriever = vector_store.as_retriever(
        search_type="mmr",
        search_kwargs={
            "k": TOP_K_RESULTS,
            "fetch_k": 20,    # Fetch 20, then pick top-K diverse ones
            "lambda_mult": 0.6 # 0.5 is balanced, 0.7 is more relevance-focused
        },
    )

    # 2. Contextual compressor (EmbeddingsFilter)
    # Drops any chunks with < 0.7 similarity to the query
    compressor = EmbeddingsFilter(
        embeddings=embeddings, 
        similarity_threshold=0.7
    )

    # 3. Combine into a compression retriever
    compression_retriever = ContextualCompressionRetriever(
        base_compressor=compressor, 
        base_retriever=base_retriever
    )

    logger.info(f"Optimized retriever created (MMR k={TOP_K_RESULTS}, Compression enabled)")
    return compression_retriever


def format_context_with_sources(docs: list[Document]) -> tuple[str, list[str]]:
    """Format retrieved documents into a context string and collect sources.

    Args:
        docs: List of retrieved Document objects.

    Returns:
        tuple: (context_string, list_of_source_names)
    """
    context_parts = []
    sources = []

    for i, doc in enumerate(docs, 1):
        source = doc.metadata.get("source", "Unknown Source")
        if source not in sources:
            sources.append(source)
        
        # Clean up content: remove excessive newlines/whitespace
        content = doc.page_content.replace("\n\n", "\n").strip()
        context_parts.append(f"[{source}]\n{content}")

    # Use a smaller separator to save tokens
    context_str = "\n---\n".join(context_parts)
    return context_str, sources
