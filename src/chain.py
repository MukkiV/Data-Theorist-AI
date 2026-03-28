"""
chain.py — Assembles the RAG chain: retriever + memory + LLM + prompt.
This is the core orchestration module.
"""

import logging
from langchain_groq import ChatGroq
from langchain_community.vectorstores import FAISS
from langchain_classic.memory import ConversationBufferWindowMemory

from src.config import GROQ_API_KEY, GROQ_MODEL, LLM_TEMPERATURE, LLM_MAX_TOKENS
from src.retriever import retrieve_context, format_context_with_sources
from src.memory import get_chat_history_text, save_turn
from src.prompt import build_prompt
from src.token_tracker import TokenTracker

logger = logging.getLogger(__name__)


def create_llm() -> ChatGroq:
    """Initialize and return the Groq LLM client.

    Returns:
        ChatGroq: The configured Groq LLM instance.

    Raises:
        ValueError: If GROQ_API_KEY is not set.
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
    memory: ConversationBufferWindowMemory,
    llm: ChatGroq,
    token_tracker: TokenTracker,
) -> dict:
    """Run the full RAG pipeline for a single user question.

    Args:
        question: The user's question.
        vector_store: Loaded FAISS vector store.
        memory: Bounded conversation memory.
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
        # 1. Retrieve relevant book chunks
        docs = retrieve_context(vector_store, question)
        context, sources = format_context_with_sources(docs)

        # 2. Get chat history from memory
        chat_history = get_chat_history_text(memory)

        # 3. Build the full teaching prompt
        prompt_text = build_prompt(
            context=context,
            chat_history=chat_history,
            question=question,
        )

        # 4. Call the LLM
        logger.info("Calling Groq LLM...")
        response = llm.invoke(prompt_text)
        answer = response.content

        # 5. Track token usage (try official first, then estimate)
        token_usage = getattr(response, 'response_metadata', {}).get('token_usage', {})
        if token_usage:
            prompt_tokens = token_usage.get('prompt_tokens', 0)
            completion_tokens = token_usage.get('completion_tokens', 0)
            token_stats = token_tracker.track_official(prompt_tokens, completion_tokens)
        else:
            token_stats = token_tracker.track(prompt=prompt_text, completion=answer)

        # 6. Save this turn to memory
        save_turn(memory, question, answer)

        logger.info("RAG chain completed successfully.")
        return {
            "answer": answer,
            "sources": sources,
            "tokens": token_stats,
        }

    except Exception as e:
        logger.error(f"Error in RAG chain: {e}", exc_info=True)
        return {
            "answer": f"❌ An error occurred: {str(e)}\n\nPlease check your API key and try again.",
            "sources": [],
            "tokens": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
        }
