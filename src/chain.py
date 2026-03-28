"""
chain.py — Assembles the optimized RAG pipeline.
Integrates compressed retrieval, summarized memory, and chat prompts.
"""

import logging
from langchain_groq import ChatGroq
from langchain_community.vectorstores import FAISS
from langchain_classic.memory import ConversationSummaryBufferMemory

from src.config import GROQ_API_KEY, GROQ_MODEL, LLM_TEMPERATURE, LLM_MAX_TOKENS
from src.retriever import get_optimized_retriever, format_context_with_sources
from src.memory import get_chat_history_text, save_turn
from src.prompt import build_prompt
from src.token_tracker import TokenTracker
from src.embedder import get_embedding_model

logger = logging.getLogger(__name__)


def create_llm() -> ChatGroq:
    """Initialize and return the Groq LLM client.

    Returns:
        ChatGroq: The configured Groq LLM instance.
    """
    if not GROQ_API_KEY:
        raise ValueError(
            "GROQ_API_KEY is not set. Please add it to your .env file."
        )

    logger.info(f"Initializing Groq LLM: {GROQ_MODEL}")
    return ChatGroq(
        api_key=GROQ_API_KEY,
        model_name=GROQ_MODEL,
        temperature=LLM_TEMPERATURE,
        max_tokens=LLM_MAX_TOKENS,
    )


def run_rag_chain(
    question: str,
    vector_store: FAISS,
    memory: ConversationSummaryBufferMemory,
    llm: ChatGroq,
    token_tracker: TokenTracker,
) -> dict:
    """Run the optimized RAG pipeline.

    Args:
        question: The user's question.
        vector_store: Loaded FAISS vector store.
        memory: Summarization-based conversation memory.
        llm: Groq LLM instance.
        token_tracker: Token usage tracker.

    Returns:
        dict: {
            "answer": str,
            "sources": list[str],
            "tokens": dict[str, int],
        }
    """
    try:
        # 1. Get embedding model for the compression retriever
        embeddings = get_embedding_model()
        
        # 2. Retrieve & Compress context
        logger.info("Retrieving compressed context...")
        retriever = get_optimized_retriever(vector_store, embeddings)
        compressed_docs = retriever.invoke(question)
        
        context, sources = format_context_with_sources(compressed_docs)

        # 3. Get history (includes auto-summary if needed)
        chat_history = get_chat_history_text(memory)

        # 4. Build prompt (as a string for the .invoke call)
        # In a full LCEL refactor, we'd pass messages directly.
        prompt_text = build_prompt(
            context=context,
            chat_history=chat_history,
            question=question,
        )

        # 5. Call LLM
        logger.info(f"Calling LLM ({GROQ_MODEL})...")
        response = llm.invoke(prompt_text)
        answer = response.content

        # 6. Track tokens
        token_usage = getattr(response, 'response_metadata', {}).get('token_usage', {})
        if token_usage:
            token_stats = token_tracker.track_official(
                token_usage.get('prompt_tokens', 0),
                token_usage.get('completion_tokens', 0)
            )
        else:
            token_stats = token_tracker.track(prompt=prompt_text, completion=answer)

        # 7. Save turn
        save_turn(memory, question, answer)

        return {
            "answer": answer,
            "sources": sources,
            "tokens": token_stats,
        }

    except Exception as e:
        logger.error(f"Error in RAG chain: {e}", exc_info=True)
        return {
            "answer": f"❌ Optimization Error: {str(e)}",
            "sources": [],
            "tokens": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
        }
