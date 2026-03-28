"""
retriever.py — Handles document retrieval from the FAISS vector store.
Returns top-K relevant chunks for a given query.
"""

import logging
from langchain_community.vectorstores import FAISS
from langchain_classic.schema import Document

from src.config import TOP_K_RESULTS

logger = logging.getLogger(__name__)


def get_retriever(vector_store: FAISS):
    """Create a LangChain retriever from the vector store.

    Args:
        vector_store: A loaded FAISS vector store instance.

    Returns:
        A LangChain VectorStoreRetriever configured with top-K results.
    """
    retriever = vector_store.as_retriever(
        search_type="similarity",
        search_kwargs={"k": TOP_K_RESULTS},
    )
    logger.info(f"Retriever created with top_k={TOP_K_RESULTS}")
    return retriever


def retrieve_context(vector_store: FAISS, query: str) -> list[Document]:
    """Retrieve the most relevant document chunks for a query.

    Args:
        vector_store: A loaded FAISS vector store instance.
        query: The user's question or search string.

    Returns:
        list[Document]: Top-K relevant document chunks with metadata.
    """
    logger.info(f"Retrieving context for query: '{query[:60]}...'")
    docs = vector_store.similarity_search(query, k=TOP_K_RESULTS)
    logger.info(f"Retrieved {len(docs)} chunks")
    return docs


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
        context_parts.append(f"[Chunk {i} — {source}]\n{doc.page_content.strip()}")

    context_str = "\n\n".join(context_parts)
    return context_str, sources
