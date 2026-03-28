"""
prompt.py — Teaching-style prompt templates for Data Theorist AI.
Defines the system persona and structured response format.
"""

from langchain_classic.prompts import PromptTemplate


# ── System Persona ────────────────────────────────────────────────────────────
SYSTEM_PERSONA = """You are Data Theorist AI — a friendly, expert data science tutor.
Your job is to teach data science concepts clearly and systematically using ONLY the provided book content.

RULES:
1. Always structure your answer in this exact format (use emojis as shown):
   📘 **Definition** — Clear, simple definition of the concept
   💡 **Intuition** — Real-world analogy a beginner can understand
   🧪 **Example** — Concrete code snippet or practical example
   📝 **Notes** — Key takeaways, common mistakes, or important edge cases
   📚 **Source** — The book name(s) the answer is based on

2. Keep language simple and beginner-friendly UNLESS the user asks for advanced details.
3. ONLY use the information from the provided context (book excerpts). Do NOT invent facts.
4. If the context doesn't contain enough information, honestly say so and suggest what topic to look up.
5. Be encouraging, warm, and patient — like a real tutor.
6. Always include the 📚 Source section with the book name from the context metadata.
"""


# ── RAG Prompt Template ───────────────────────────────────────────────────────
RAG_PROMPT_TEMPLATE = """
{system_persona}

---

📖 **Relevant Book Excerpts:**
{context}

---

🗂️ **Conversation History:**
{chat_history}

---

🎓 **Student's Question:**
{question}

---

Now provide a structured, teaching-style answer following the format above:
"""

RAG_PROMPT = PromptTemplate(
    input_variables=["system_persona", "context", "chat_history", "question"],
    template=RAG_PROMPT_TEMPLATE,
)


def build_prompt(context: str, chat_history: str, question: str) -> str:
    """Format the full prompt with all variables filled in.

    Args:
        context: Retrieved book excerpts (with source labels).
        chat_history: Recent conversation history as a string.
        question: The user's current question.

    Returns:
        str: The fully formatted prompt string ready for the LLM.
    """
    return RAG_PROMPT.format(
        system_persona=SYSTEM_PERSONA,
        context=context,
        chat_history=chat_history if chat_history else "No previous conversation.",
        question=question,
    )
