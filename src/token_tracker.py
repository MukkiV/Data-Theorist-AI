"""
token_tracker.py — Tracks token usage per message and across the session.
"""

import logging
import tiktoken

logger = logging.getLogger(__name__)

# Use cl100k_base encoding (compatible with most modern LLMs)
_ENCODING = tiktoken.get_encoding("cl100k_base")


class TokenTracker:
    """Tracks token usage for prompt and completion across a session.

    Attributes:
        session_prompt_tokens (int): Total prompt tokens used this session.
        session_completion_tokens (int): Total completion tokens this session.
        last_prompt_tokens (int): Prompt tokens for the last message.
        last_completion_tokens (int): Completion tokens for the last message.
    """

    def __init__(self) -> None:
        self.session_prompt_tokens: int = 0
        self.session_completion_tokens: int = 0
        self.last_prompt_tokens: int = 0
        self.last_completion_tokens: int = 0

    def count_tokens(self, text: str) -> int:
        """Count the number of tokens in a string.

        Args:
            text: Input string to tokenize.

        Returns:
            int: Token count.
        """
        return len(_ENCODING.encode(text))

    def track(self, prompt: str, completion: str) -> dict[str, int]:
        """Record token usage (estimated) for a single prompt-completion pair."""
        prompt_tokens = self.count_tokens(prompt)
        completion_tokens = self.count_tokens(completion)
        return self._update_counts(prompt_tokens, completion_tokens)

    def track_official(self, prompt_tokens: int, completion_tokens: int) -> dict[str, int]:
        """Record official token usage from the API response."""
        return self._update_counts(prompt_tokens, completion_tokens)

    def _update_counts(self, prompt_tokens: int, completion_tokens: int) -> dict[str, int]:
        """Internal helper to update counters and return stats."""
        self.last_prompt_tokens = prompt_tokens
        self.last_completion_tokens = completion_tokens
        self.session_prompt_tokens += prompt_tokens
        self.session_completion_tokens += completion_tokens

        return {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": prompt_tokens + completion_tokens,
        }

    @property
    def session_total(self) -> int:
        """Total tokens used in this session."""
        return self.session_prompt_tokens + self.session_completion_tokens

    @property
    def last_message_total(self) -> int:
        """Total tokens used in the last message."""
        return self.last_prompt_tokens + self.last_completion_tokens

    def get_summary(self) -> dict[str, int]:
        """Get a full summary of token usage.

        Returns:
            dict: Session and last-message token counts.
        """
        return {
            "last_prompt_tokens": self.last_prompt_tokens,
            "last_completion_tokens": self.last_completion_tokens,
            "last_message_total": self.last_message_total,
            "session_prompt_tokens": self.session_prompt_tokens,
            "session_completion_tokens": self.session_completion_tokens,
            "session_total": self.session_total,
        }

    def reset(self) -> None:
        """Reset all token counters."""
        self.__init__()
        logger.info("Token tracker reset.")
