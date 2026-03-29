"""
prompt.py — Teaching-style chat prompts for Data Theorist AI.
Defines the system persona and structured response format using Chat Templates.
"""

from langchain_classic.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate


# ── System Persona ────────────────────────────────────────────────────────────
SYSTEM_PERSONA = """You are Data Theorist AI — a friendly, expert data science tutor.
Your job is to teach data science concepts clearly and systematically. 

RULES:
RULES:
1. BE POLITE & FRIENDLY. If the student says "thanks," "hello," or other social greetings, respond warmly but briefly.
2. NO TEACHING FILLER. For any CONCEPT or DATA SCIENCE question, do not use introductory fluff (like "Let's learn...", "Context: ..."). START DIRECTLY with the 📘 **Definition** section.
3. Use the provided book content as your primary source.
4. Always structure your teaching responses in this exact format:
   📘 **Definition** — Clear, simple definition
   💡 **Intuition** — Real-world analogy
   🧪 **Example** — Concrete code snippet or practical example
   📝 **Notes** — Key takeaways or edge cases

5. If you don't find the specific topic in the books, you may use your general knowledge to explain it, but mention that it's based on general principles.
6. Keep language simple and beginner-friendly. Use emojis to make the learning experience engaging.
7. If the student specifically asks for your identity (and only then), you can explain who you are.
"""


# ── Modern Chat Prompt Template ──────────────────────────────────────────────
# We use specific message roles to help the LLM distinguish between
# instructions, retrieved context, and user history.
RAG_CHAT_PROMPT = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template(SYSTEM_PERSONA),
    HumanMessagePromptTemplate.from_template(
        "📖 **Context from Books:**\n{context}\n\n"
        "--- \n\n"
        "🗂️ **Conversation History:**\n{chat_history}\n\n"
        "--- \n\n"
        "🎓 **Student's Question:** {question}"
    ),
])


def build_prompt(context: str, chat_history: str, question: str) -> str:
    """Format the chat prompt into a single string for legacy handlers or return the template.
    
    In a modern LCEL chain, we would just pass the RAG_CHAT_PROMPT.
    For compatibility with the existing run_rag_chain, we'll format it.
    """
    # Formatting into a string representation of the messages
    messages = RAG_CHAT_PROMPT.format_messages(
        context=context,
        chat_history=chat_history if chat_history else "No previous conversation.",
        question=question
    )
    
    # Concatenate messages for the legacy .invoke(string) call in chain.py
    # (Though we will refactor chain.py to handle this better)
    full_prompt = ""
    for m in messages:
        full_prompt += f"{m.content}\n\n"
    return full_prompt.strip()


def get_chat_prompt_template():
    """Returns the structured ChatPromptTemplate for LCEL chains."""
    return RAG_CHAT_PROMPT
