"""
app.py — Streamlit UI for Data Theorist AI.
Entry point for the chat-based learning assistant.

Run with: streamlit run app.py
"""

import logging
import streamlit as st

# ── Logging Setup ─────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("app")

# ── Page Config (must be first Streamlit call) ────────────────────────────────
st.set_page_config(
    page_title="Data Theorist AI",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* Import Google Font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* Main background */
    .stApp {
        background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
        color: #e0e0e0;
    }

    /* Chat messages */
    .stChatMessage {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        border: 1px solid rgba(255,255,255,0.1);
        backdrop-filter: blur(10px);
        margin-bottom: 1rem;
        padding: 0.5rem;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: rgba(15, 12, 41, 0.95);
        border-right: 1px solid rgba(255,255,255,0.1);
    }

    /* Input box */
    .stChatInputContainer {
        background: rgba(255,255,255,0.08);
        border: 1px solid rgba(255,255,255,0.2);
        border-radius: 12px;
    }

    /* Token badge */
    .token-badge {
        background: rgba(99, 102, 241, 0.2);
        border: 1px solid rgba(99, 102, 241, 0.5);
        border-radius: 8px;
        padding: 4px 10px;
        font-size: 0.78rem;
        color: #a5b4fc;
        display: inline-block;
        margin: 2px;
    }

    /* Source tag */
    .source-tag {
        background: rgba(16, 185, 129, 0.15);
        border: 1px solid rgba(16, 185, 129, 0.4);
        border-radius: 6px;
        padding: 3px 8px;
        font-size: 0.75rem;
        color: #6ee7b7;
        display: inline-block;
        margin: 2px;
    }

    /* Metric cards in sidebar */
    [data-testid="metric-container"] {
        background: rgba(99, 102, 241, 0.1);
        border: 1px solid rgba(99, 102, 241, 0.3);
        border-radius: 10px;
        padding: 10px;
    }

    /* Hide default Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


# ── Cached Resource Loaders ───────────────────────────────────────────────────
@st.cache_resource(show_spinner="📚 Loading knowledge base...")
def load_resources():
    """Load the vector store, LLM, and token tracker once per session."""
    from src.embedder import get_embedding_model, load_vector_store
    from src.chain import create_llm
    from src.token_tracker import TokenTracker

    embeddings = get_embedding_model()
    vector_store = load_vector_store(embeddings)
    llm = create_llm()
    token_tracker = TokenTracker()
    return vector_store, llm, token_tracker


# ── Session State Initialization ──────────────────────────────────────────────
def init_session_state() -> None:
    """Initialize all session state variables."""
    if "messages" not in st.session_state:
        st.session_state.messages = []       # Chat history for display
    if "memory" not in st.session_state:
        from src.memory import create_memory
        st.session_state.memory = create_memory()
    if "total_tokens" not in st.session_state:
        st.session_state.total_tokens = 0
    if "message_count" not in st.session_state:
        st.session_state.message_count = 0


# ── Sidebar ───────────────────────────────────────────────────────────────────
def render_sidebar(token_tracker) -> None:
    """Render the sidebar with project info and token metrics."""
    with st.sidebar:
        st.markdown("""
        <div style='text-align:center; padding: 1rem 0;'>
            <span style='font-size:2.5rem;'>🧠</span>
            <h2 style='color:#a5b4fc; margin:0.3rem 0;'>Data Theorist AI</h2>
            <p style='color:#6b7280; font-size:0.85rem;'>RAG-Powered Learning Assistant</p>
        </div>
        """, unsafe_allow_html=True)

        st.divider()

        # Knowledge Base Info
        st.markdown("### 📚 Knowledge Base")
        books = [
            ("🤖", "Machine Learning"),
            ("🐍", "Python Programming"),
            ("🗄️", "SQL & Databases"),
            ("📊", "Statistics"),
            ("📖", "Data Storytelling"),
        ]
        for icon, name in books:
            st.markdown(f"{icon} `{name}`")

        st.divider()

        # Token Usage Metrics
        st.markdown("### 📊 Token Usage")
        summary = token_tracker.get_summary()

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Last Message", f"{summary['last_message_total']:,}")
        with col2:
            st.metric("Session Total", f"{summary['session_total']:,}")

        st.caption(
            f"↑ Prompt: {summary['session_prompt_tokens']:,}  |  "
            f"↓ Response: {summary['session_completion_tokens']:,}"
        )

        st.divider()

        # Settings
        st.markdown("### ⚙️ Settings")
        st.caption("**Model:** Llama 3 (8B) via Groq")
        st.caption("**Memory:** Last 4 conversation turns")
        st.caption("**Top-K:** 5 book chunks per query")

        st.divider()

        # Clear Chat Button
        if st.button("🗑️ Clear Conversation", use_container_width=True):
            st.session_state.messages = []
            from src.memory import create_memory
            st.session_state.memory = create_memory()
            token_tracker.reset()
            st.session_state.message_count = 0
            st.rerun()

        st.markdown("""
        <div style='text-align:center; margin-top:1rem; color:#4b5563; font-size:0.75rem;'>
            Built with LangChain + Groq + FAISS
        </div>
        """, unsafe_allow_html=True)


# ── Main App ──────────────────────────────────────────────────────────────────
def main() -> None:
    """Main Streamlit application logic."""
    init_session_state()

    # Load resources (cached — runs once)
    try:
        vector_store, llm, token_tracker = load_resources()
    except FileNotFoundError:
        st.error("""
        ## ❌ Vector Store Not Found

        You need to ingest your PDFs first. Open a terminal and run:
        ```bash
        python ingest.py
        ```
        Then refresh this page.
        """)
        st.stop()
    except ValueError as e:
        st.error(f"## ❌ Configuration Error\n\n{e}")
        st.stop()

    # Render sidebar
    render_sidebar(token_tracker)

    # ── Header ────────────────────────────────────────────────────────────
    st.markdown("""
    <div style='text-align:center; padding: 1.5rem 0 1rem 0;'>
        <h1 style='color:#a5b4fc; font-size:2rem; margin:0;'>
            🧠 Data Theorist AI
        </h1>
        <p style='color:#6b7280; font-size:1rem; margin-top:0.3rem;'>
            Ask anything about Machine Learning, Python, SQL, Statistics, or Data Storytelling
        </p>
    </div>
    """, unsafe_allow_html=True)

    # ── Example Questions ─────────────────────────────────────────────────
    if not st.session_state.messages:
        st.markdown("### 💡 Try asking:")
        example_cols = st.columns(3)
        examples = [
            "What is a decision tree?",
            "Explain overfitting simply",
            "How does SQL JOIN work?",
            "What is the Central Limit Theorem?",
            "Difference between mean and median?",
            "How to tell a story with data?",
        ]
        for i, example in enumerate(examples):
            with example_cols[i % 3]:
                if st.button(f"💬 {example}", key=f"example_{i}", use_container_width=True):
                    st.session_state._quick_question = example

    # ── Display Chat History ───────────────────────────────────────────────
    for message in st.session_state.messages:
        with st.chat_message(message["role"], avatar="🎓" if message["role"] == "assistant" else "👤"):
            st.markdown(message["content"])
            if message["role"] == "assistant" and "tokens" in message:
                tok = message["tokens"]
                st.markdown(
                    f'<span class="token-badge">📤 {tok["prompt_tokens"]} prompt</span>'
                    f'<span class="token-badge">📥 {tok["completion_tokens"]} response</span>',
                    unsafe_allow_html=True,
                )
                if message.get("sources"):
                    src_html = "".join(
                        f'<span class="source-tag">📚 {s}</span>'
                        for s in message["sources"]
                    )
                    st.markdown(src_html, unsafe_allow_html=True)

    # ── Handle Quick Question (example button clicked) ─────────────────────
    quick_q = st.session_state.pop("_quick_question", None)

    # ── Chat Input ─────────────────────────────────────────────────────────
    user_input = st.chat_input("Ask a data science question...") or quick_q

    if user_input:
        # Display user message
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user", avatar="👤"):
            st.markdown(user_input)

        # Generate and display assistant response
        with st.chat_message("assistant", avatar="🎓"):
            with st.spinner("📖 Searching books and crafting your answer..."):
                from src.chain import run_rag_chain
                result = run_rag_chain(
                    question=user_input,
                    vector_store=vector_store,
                    memory=st.session_state.memory,
                    llm=llm,
                    token_tracker=token_tracker,
                )

            answer = result["answer"]
            sources = result["sources"]
            tokens = result["tokens"]

            st.markdown(answer)

            # Token info
            st.markdown(
                f'<span class="token-badge">📤 {tokens["prompt_tokens"]} prompt</span>'
                f'<span class="token-badge">📥 {tokens["completion_tokens"]} response</span>',
                unsafe_allow_html=True,
            )

            # Source tags
            if sources:
                src_html = "".join(
                    f'<span class="source-tag">📚 {s}</span>'
                    for s in sources
                )
                st.markdown(src_html, unsafe_allow_html=True)

        # Save assistant message to display state
        st.session_state.messages.append({
            "role": "assistant",
            "content": answer,
            "sources": sources,
            "tokens": tokens,
        })
        st.session_state.message_count += 1

        st.rerun()


if __name__ == "__main__":
    main()
