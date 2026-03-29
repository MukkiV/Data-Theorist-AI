"""
app.py — Streamlit UI for Data Theorist AI.
Entry point for the chat-based learning assistant.

Run with: streamlit run app.py
"""

import re
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
    /* Import Inter Font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    :root {
        --bg-dark: #0b1220;
        --sidebar-bg: #0b1220;
        --accent-purple: #7c3aed;
        --accent-blue: #3b82f6;
        --text-primary: #ffffff;
        --text-secondary: #94a3b8;
        --glass-bg: rgba(17, 24, 39, 0.7);
        --glass-border: rgba(255, 255, 255, 0.08);
        --glow-purple: 0 0 15px rgba(124, 58, 237, 0.3);
        --glow-blue: 0 0 15px rgba(59, 130, 246, 0.3);
    }

    /* Global Overrides - Force zero top padding */
    .stApp {
        background-color: var(--bg-dark);
        color: var(--text-primary);
        font-family: 'Inter', sans-serif;
    }

    [data-testid="stAppViewBlockContainer"] {
        padding-top: 0 !important;
        padding-bottom: 5rem !important;
        margin-top: -3rem !important;
    }

    .main .block-container {
        padding-top: 0 !important;
    }

    [data-testid="stHeader"] {
        background: transparent !important;
        color: var(--text-primary) !important;
    }

    /* Ensure the sidebar collapse button is visible and styled */
    [data-testid="collapsedControl"] {
        top: 1rem !important;
        left: 1rem !important;
        background: var(--glass-bg) !important;
        border: 1px solid var(--glass-border) !important;
        border-radius: 8px !important;
        color: var(--text-primary) !important;
    }

    /* Style for the active chat header to look like a premium dashboard */
    .active-header {
        background: rgba(124, 58, 237, 0.05);
        border-bottom: 1px solid var(--glass-border);
        padding: 1.5rem 0;
        margin-bottom: 2rem;
        margin-top: -3rem; /* Compensate for Streamlit's ghost space */
        width: 100vw;
        margin-left: -5rem; /* Center the bleed */
        text-align: center;
    }

    /* Target Streamlit's Native Chat Bubbles for Glassmorphism Styling */
    [data-testid="stChatMessage"] {
        background: var(--glass-bg) !important;
        border: 1px solid var(--glass-border) !important;
        backdrop-filter: blur(12px) !important;
        border-radius: 20px !important;
        padding: 1rem !important;
        margin-bottom: 1rem !important;
        box-shadow: 0 8px 32px rgba(0,0,0,0.2) !important;
    }

    [data-testid="stChatMessageAvatarAssistant"] {
        background: rgba(124, 58, 237, 0.2) !important;
        border: 1px solid rgba(124, 58, 237, 0.4) !important;
        border-radius: 10px !important;
        box-shadow: 0 0 10px rgba(124, 58, 237, 0.2) !important;
    }

    [data-testid="stChatMessageAvatarUser"] {
        background: linear-gradient(135deg, #7c3aed, #5b21b6) !important;
        border-radius: 10px !important;
    }

    /* Sidebar Knowledge Base Chips */
    .kb-chip {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 10px 16px;
        border-radius: 12px;
        margin-bottom: 8px;
        background: transparent;
        border: 1px solid transparent;
        cursor: pointer;
        transition: all 0.3s ease;
        color: var(--text-secondary);
        font-weight: 500;
    }

    .kb-chip:hover {
        background: rgba(124, 58, 237, 0.1);
        color: var(--text-primary);
        border-color: rgba(124, 58, 237, 0.2);
    }

    .kb-chip.active {
        background: rgba(124, 58, 237, 0.15);
        color: var(--text-primary);
        border-color: var(--accent-purple);
        box-shadow: var(--glow-purple);
    }

    /* Stats Ring */
    .stats-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        margin-top: 1rem;
        margin-bottom: 2rem;
        padding: 1.5rem;
        background: rgba(255, 255, 255, 0.03);
        border-radius: 20px;
        border: 1px solid var(--glass-border);
    }

    .stats-ring {
        width: 120px;
        height: 120px;
        border-radius: 50%;
        border: 4px solid var(--accent-purple);
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        margin-bottom: 1rem;
        position: relative;
        box-shadow: var(--glow-purple);
        animation: pulse 4s infinite ease-in-out;
    }

    @keyframes pulse {
        0%, 100% { box-shadow: 0 0 15px rgba(124, 58, 237, 0.3); }
        50% { box-shadow: 0 0 25px rgba(124, 58, 237, 0.5); }
    }

    /* Header Styling */
    .dashboard-header {
        position: relative;
        padding: 1.5rem 1rem;
        text-align: center;
        background: radial-gradient(circle at 50% 50%, rgba(59, 130, 246, 0.1) 0%, transparent 50%);
        margin-bottom: 1rem;
    }

    .gradient-text {
        background: linear-gradient(90deg, #60a5fa, #a78bfa);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3rem;
        font-weight: 800;
        letter-spacing: -0.02em;
        margin-bottom: 0.5rem;
    }

    /* Chat Area */
    .chat-container {
        max-width: 900px;
        margin: 0 auto;
        padding-top: 0;
        padding-bottom: 120px;
    }

    /* Message Bubbles */
    .message-row {
        display: flex;
        margin-bottom: 1.5rem;
        width: 100%;
        animation: fadeIn 0.4s ease-out forwards;
    }

    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }

    .message-user {
        justify-content: flex-end;
    }

    .bubble-user {
        background: linear-gradient(135deg, #7c3aed, #5b21b6);
        color: white;
        padding: 12px 20px;
        border-radius: 20px 20px 4px 20px;
        max-width: 80%;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }

    .bubble-ai {
        background: var(--glass-bg);
        border: 1px solid var(--glass-border);
        backdrop-filter: blur(12px);
        color: var(--text-primary);
        padding: 24px;
        border-radius: 4px 20px 20px 20px;
        width: 100%;
        box-shadow: 0 8px 32px rgba(0,0,0,0.2);
    }
    
    .ai-bubble-container {
        max-width: 85%;
        display: flex;
        flex-direction: row;
    }

    /* Message Sections */
    .ai-section {
        margin-bottom: 12px;
    }
    .ai-section-title {
        font-weight: 600;
        font-size: 0.95rem;
        margin-bottom: 4px;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    /* Typing Dots */
    .typing-dots {
        display: flex;
        gap: 4px;
        margin-top: 8px;
    }
    .dot {
        width: 6px;
        height: 6px;
        background: var(--text-secondary);
        border-radius: 50%;
        animation: dotBounce 1.4s infinite ease-in-out;
    }
    .dot:nth-child(2) { animation-delay: 0.2s; }
    .dot:nth-child(3) { animation-delay: 0.4s; }

    @keyframes dotBounce {
        0%, 80%, 100% { transform: scale(0); }
        40% { transform: scale(1); }
    }

    /* Input Bar */
    .fixed-input {
        position: fixed;
        bottom: 30px;
        left: 50%;
        transform: translateX(-50%);
        width: calc(100% - 350px);
        max-width: 850px;
        background: rgba(17, 24, 39, 0.8);
        backdrop-filter: blur(20px);
        border: 1px solid var(--glass-border);
        border-radius: 24px;
        padding: 12px 16px;
        display: flex;
        align-items: center;
        box-shadow: 0 10px 40px rgba(0,0,0,0.4);
        z-index: 1000;
    }

    /* Suggestion Chips */
    .suggestion-chips {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        justify-content: center;
        margin-top: 1rem;
    }

    .chip {
        background: var(--glass-bg);
        border: 1px solid var(--glass-border);
        padding: 6px 14px;
        border-radius: 100px;
        font-size: 0.85rem;
        color: var(--text-secondary);
        cursor: pointer;
        transition: all 0.2s ease;
    }

    .chip:hover {
        background: rgba(255, 255, 255, 0.05);
        border-color: var(--accent-blue);
        color: var(--text-primary);
        transform: scale(1.02);
    }

    [title]:hover::after {
        content: attr(title);
        position: absolute;
        bottom: 125%;
        left: 50%;
        transform: translateX(-50%);
        background: #1e293b;
        color: white;
        padding: 8px 12px;
        border-radius: 8px;
        font-size: 0.75rem;
        white-space: pre;
        z-index: 1000;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        border: 1px solid var(--glass-border);
    }
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
def init_session_state(llm=None) -> None:
    """Initialize all session state variables."""
    import time
    if "messages" not in st.session_state:
        st.session_state.messages = []       # Chat history for display
    if "memory" not in st.session_state and llm:
        from src.memory import create_memory
        st.session_state.memory = create_memory(llm)
    if "total_tokens" not in st.session_state:
        st.session_state.total_tokens = 0
    if "message_count" not in st.session_state:
        st.session_state.message_count = 0
    if "session_start_time" not in st.session_state:
        st.session_state.session_start_time = time.time()


# ── Sidebar ───────────────────────────────────────────────────────────────────
def render_sidebar(token_tracker) -> None:
    """Render the sidebar with project info and token metrics."""
    import time
    with st.sidebar:
        # Logo & Title
        st.markdown("""
        <div style='text-align:center; padding-bottom: 2rem;'>
            <div style='background: rgba(124, 58, 237, 0.1); width: 80px; height: 80px; border-radius: 20px; display: flex; align-items: center; justify-content: center; margin: 0 auto 1rem auto; border: 1px solid rgba(124, 58, 237, 0.3); box-shadow: 0 0 20px rgba(124, 58, 237, 0.2);'>
                <span style='font-size:3rem;'>🧠</span>
            </div>
            <h2 style='color:white; margin:0; font-size: 1.5rem; letter-spacing: -0.02em;'>Data Theorist <span style='color:#7c3aed;'>AI</span></h2>
            <p style='color:#94a3b8; font-size:0.85rem; margin-top: 0.5rem;'>Your Personal Data Science Tutor</p>
        </div>
        """, unsafe_allow_html=True)

        # Knowledge Base Section
        st.markdown("<p style='color:#64748b; font-size:0.75rem; font-weight:700; text-transform:uppercase; letter-spacing:0.1em; margin-bottom:1rem;'>Knowledge Base</p>", unsafe_allow_html=True)
        
        books = [
            ("🤖", "Machine Learning"),
            ("🐍", "Python"),
            ("🗄️", "SQL"),
            ("📊", "Statistics"),
            ("📖", "Story Telling"),
        ]
        
        for icon, name in books:
            st.markdown(f"""
            <div class="kb-chip">
                <span>{icon}</span>
                <span>{name}</span>
            </div>
            """, unsafe_allow_html=True)

        # Session Stats Ring
        summary = token_tracker.get_summary()
        tokens_used = summary['session_total']
        msg_count = st.session_state.message_count
        
        # Calculate session time
        elapsed = int(time.time() - st.session_state.get("session_start_time", time.time()))
        hrs, remainder = divmod(elapsed, 3600)
        mins, secs = divmod(remainder, 60)
        time_str = f"{hrs:02}:{mins:02}:{secs:02}"

        st.markdown(f"""
        <div class="stats-container">
            <p style='color:#64748b; font-size:0.75rem; font-weight:700; text-transform:uppercase; letter-spacing:0.1em; margin-bottom:1.5rem;'>Session Stats</p>
            <div class="stats-ring">
                <span style='font-size:0.75rem; color:#94a3b8;'>Tokens Used</span>
                <span style='font-size:1.25rem; font-weight:700; color:white;'>{tokens_used:,}</span>
            </div>
            <div style='display:flex; flex-direction:column; align-items:center; gap:8px; margin-top:0.5rem;'>
                <div style='text-align:center;'>
                    <p style='color:#94a3b8; font-size:0.8rem; margin:0;'>Messages</p>
                    <p style='color:white; font-size:1rem; font-weight:600; margin:0;'>{msg_count}</p>
                </div>
                <div style='text-align:center;'>
                    <p style='color:#94a3b8; font-size:0.8rem; margin:0;'>Session Time</p>
                    <p style='color:white; font-size:1rem; font-weight:600; margin:0;'>{time_str}</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<div style='flex-grow: 1;'></div>", unsafe_allow_html=True)

        # Clear Session Button at the bottom
        if st.button("🗑️ Clear Session", use_container_width=True):
            st.session_state.messages = []
            if "memory" in st.session_state:
                st.session_state.memory.clear()
            st.session_state.message_count = 0
            st.rerun()

        st.markdown("""
        <div style='text-align:center; padding: 1rem 0; color:#475569; font-size:0.7rem;'>
            Made with ❤️ by Data Theorist AI
        </div>
        """, unsafe_allow_html=True)

def render_ai_message(content, tokens=None, sources=None, response_time=0):
    """Unified function to parse and render AI messages with professional formatting."""
    # 1. Clean up redundant source lines and conversational filler prefixes
    clean_content = content.replace("📚 Context:", "").replace("📘 Definition:", "📘 Definition") 
    clean_content = re.sub(r'^(?:Your Tutor|Data Theorist AI):\s*', '', clean_content, flags=re.MULTILINE | re.IGNORECASE)
    clean_content = re.sub(r'\n*(?:📚\s*)?Source:\s*.*$', '', clean_content, flags=re.MULTILINE | re.IGNORECASE)
    clean_content = clean_content.strip()
    
    # 2. Extract sections
    icons = {"Definition": "📘", "Intuition": "💡", "Example": "🧪", "Notes": "📝"}
    
    with st.chat_message("assistant", avatar="🤖"):
        # Split by code blocks to preserve them
        parts = re.split(r'(```(?:\w+)?\n[\s\S]*?```)', clean_content)
        
        for part in parts:
            if part.startswith("```"):
                code_match = re.match(r'```(\w+)?\n([\s\S]*?)```', part)
                if code_match:
                    lang = code_match.group(1) or "python"
                    st.code(code_match.group(2), language=lang)
            else:
                sections = part.split("\n\n")
                for sec in sections:
                    if not sec.strip(): continue
                    found_title = None
                    clean_sec = sec.strip()
                    for title in icons:
                        header_pat = rf'^[^\w\s]*\s*\*\*?{title}\*\*?\s*—?\s*'
                        if re.match(header_pat, clean_sec, re.IGNORECASE):
                            found_title = title
                            clean_sec = re.sub(header_pat, '', clean_sec, count=1, flags=re.IGNORECASE)
                            break
                    
                    if found_title:
                        st.markdown(f'**{icons[found_title]} {found_title}**: {clean_sec}')
                    else:
                        st.markdown(clean_sec)

        # 3. Professional Info Chip
        if tokens or sources or response_time:
            total_tok = tokens.get("total_tokens", 0) if tokens else 0
            prompt_tok = tokens.get("prompt_tokens", 0) if tokens else 0
            comp_tok = tokens.get("completion_tokens", 0) if tokens else 0
            source_str = " • ".join(sources) if sources else "Knowledge Base"
            
            st.markdown(f"""
            <div style="margin-top: 1rem; border-top: 1px solid var(--glass-border); padding-top: 0.5rem; display: flex; justify-content: space-between; align-items: center; opacity: 0.8;">
                <div style="font-size: 0.75rem; color: #94a3b8;">Ref: {source_str}</div>
                <div style="display: flex; gap: 8px;">
                    <div class="chip" style="font-size: 0.7rem;">⏱️ {response_time:.1f}s</div>
                    <div class="chip" style="font-size: 0.7rem;" title="Prompt: {prompt_tok} | Resp: {comp_tok}">🪙 {total_tok:,} Tokens</div>
                </div>
            </div>
            """, unsafe_allow_html=True)


# ── Main App ──────────────────────────────────────────────────────────────────
def main() -> None:
    """Main Streamlit application logic."""
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

    # Initialize state with LLM (for memory summarization)
    init_session_state(llm)

    # Render sidebar
    render_sidebar(token_tracker)

    # ── Header & Example Questions ────────────────────────────────────────
    if not st.session_state.messages:
        st.markdown("""
        <div class="dashboard-header">
            <h1 class="gradient-text">✨ Data Theorist AI</h1>
            <p style='color:#94a3b8; font-size:1.1rem; margin-top:0.5rem;'>Your Personal Data Science Tutor</p>
            <p style='color:#64748b; font-size:0.9rem;'>Ask anything about Machine Learning, Python, SQL, Statistics, or Data Storytelling</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<div style='text-align:center; margin-bottom: 1rem;'><span style='font-size:1.2rem;'>💡</span> <span style='font-weight:600; color:white;'>Try Asking:</span></div>", unsafe_allow_html=True)
        examples = [
            "What is a decision tree?", "Explain overfitting simply", "How does SQL JOIN work?",
            "What is the Central Limit Theorem?", "Difference between mean and median?", "How to tell a story with data?",
        ]
        st.markdown("<div class='suggestion-chips'>", unsafe_allow_html=True)
        cols = st.columns(3)
        for i, example in enumerate(examples):
            with cols[i % 3]:
                if st.button(example, key=f"ex_{i}", use_container_width=True):
                    st.session_state._quick_question = example
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        # Compact Header for active chat - Styled as a premium dashboard card
        st.markdown("""
        <div class="active-header">
            <h1 style='background: linear-gradient(90deg, #60a5fa, #a78bfa); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin:0; font-size: 3rem;'>✨ Data Theorist AI</h1>
            <p style='color: #94a3b8; font-size: 1rem; margin-top: 0.5rem;'>Your Deep Intelligence Partner</p>
        </div>
        """, unsafe_allow_html=True)

    # ── Display Chat History ───────────────────────────────────────────────
    for message in st.session_state.messages:
        role = message["role"]
        content = message["content"]
        
        if role == "user":
            with st.chat_message("user", avatar="👤"):
                st.markdown(content)
        else:
            render_ai_message(
                content=content,
                tokens=message.get("tokens"),
                sources=message.get("sources"),
                response_time=message.get("response_time", 0)
            )

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
        with st.container():
            # Typing Indicator
            typing_container = st.empty()
            typing_container.markdown(f"""
            <div class="message-row">
                <div style="margin-right: 12px; margin-top: 10px;">
                    <div style="background: rgba(124, 58, 237, 0.2); width: 36px; height: 36px; border-radius: 10px; display: flex; align-items: center; justify-content: center; border: 1px solid rgba(124, 58, 237, 0.4);">
                        <span style="font-size: 1.2rem;">🤖</span>
                    </div>
                </div>
                <div class="bubble-ai">
                    <div style="display: flex; align-items: center; gap: 8px; color: var(--text-secondary); font-size: 0.9rem;">
                        AI is typing 
                        <div class="typing-dots">
                            <div class="dot"></div>
                            <div class="dot"></div>
                            <div class="dot"></div>
                        </div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

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
            resp_time = result["response_time"]

            # Clear typing and show final
            typing_container.empty()
            
            # Unify response rendering
            render_ai_message(content=answer, tokens=tokens, sources=sources, response_time=resp_time)

        # Save assistant message to display state
        st.session_state.messages.append({
            "role": "assistant",
            "content": answer,
            "sources": sources,
            "tokens": tokens,
            "response_time": resp_time,
        })
        st.session_state.message_count += 1

        st.rerun()


if __name__ == "__main__":
    main()
