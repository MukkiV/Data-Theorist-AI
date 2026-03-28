"""
memory.py — Manages bounded conversational memory for the chat session.
Keeps only the last K conversation turns to avoid context overflow.
"""

import logging
from langchain_classic.memory import ConversationBufferWindowMemory

from src.config import MEMORY_WINDOW_K

logger = logging.getLogger(__name__)


def create_memory() -> ConversationBufferWindowMemory:
    """Create a new bounded conversation memory instance.

    Returns:
        ConversationBufferWindowMemory: Memory that keeps only the last K turns.
    """
    logger.info(f"Creating conversation memory with window_k={MEMORY_WINDOW_K}")
    return ConversationBufferWindowMemory(
        k=MEMORY_WINDOW_K,
        memory_key="chat_history",
        return_messages=True,
        output_key="answer",
    )


def get_chat_history_text(memory: ConversationBufferWindowMemory) -> str:
    """Extract the chat history as a readable string.

    Args:
        memory: The conversation memory instance.

    Returns:
        str: Formatted string of past conversation turns.
    """
    messages = memory.chat_memory.messages
    if not messages:
        return ""

    history_parts = []
    for msg in messages:
        role = "User" if msg.type == "human" else "Assistant"
        history_parts.append(f"{role}: {msg.content}")

    return "\n".join(history_parts)


def save_turn(memory: ConversationBufferWindowMemory, question: str, answer: str) -> None:
    """Save a single Q&A turn into memory.

    Args:
        memory: The conversation memory instance.
        question: The user's question.
        answer: The assistant's response.
    """
    memory.save_context({"input": question}, {"answer": answer})
    logger.debug(f"Saved turn to memory. Total messages: {len(memory.chat_memory.messages)}")
