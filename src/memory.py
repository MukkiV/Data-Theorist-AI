"""
memory.py — Manages intelligent conversational memory for the chat session.
Uses a sliding window for recent turns and summarizes older ones.
"""

import logging
from langchain_classic.memory import ConversationSummaryBufferMemory
from langchain_groq import ChatGroq

from src.config import MEMORY_MAX_TOKENS

logger = logging.getLogger(__name__)


def create_memory(llm: ChatGroq) -> ConversationSummaryBufferMemory:
    """Create a new summary-buffered conversation memory instance.

    Args:
        llm: The LLM instance to use for summarization.

    Returns:
        ConversationSummaryBufferMemory: Memory that summarizes older turns.
    """
    logger.info(f"Creating summary buffer memory (max_tokens={MEMORY_MAX_TOKENS})")
    return ConversationSummaryBufferMemory(
        llm=llm,
        max_token_limit=MEMORY_MAX_TOKENS,
        memory_key="chat_history",
        return_messages=True,
        output_key="answer",
    )


def get_chat_history_text(memory: ConversationSummaryBufferMemory) -> str:
    """Extract the chat history as a readable string (including any summary).

    Args:
        memory: The conversation memory instance.

    Returns:
        str: Formatted string of past conversation turns and summaries.
    """
    # This retrieves the messages (which includes the SystemMessage summary if generated)
    messages = memory.load_memory_variables({})["chat_history"]
    
    if not messages:
        return ""

    history_parts = []
    for msg in messages:
        if msg.type == "system": # This is typically the summary
            history_parts.append(f"Summary of previous conversation: {msg.content}")
        else:
            role = "User" if msg.type == "human" else "Assistant"
            history_parts.append(f"{role}: {msg.content}")

    return "\n".join(history_parts)


def save_turn(memory: ConversationSummaryBufferMemory, question: str, answer: str) -> None:
    """Save a single Q&A turn into memory.

    Args:
        memory: The conversation memory instance.
        question: The user's question.
        answer: The assistant's response.
    """
    memory.save_context({"input": question}, {"answer": answer})
    logger.debug("Saved turn to memory.")
