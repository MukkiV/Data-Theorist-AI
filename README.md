# 🧠 Data Theorist AI
### *A RAG-Powered Learning Assistant for Data Science*

[![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)](https://www.python.org/)
[![LangChain](https://img.shields.io/badge/LangChain-0.2+-green?logo=chainlink)](https://www.langchain.com/)
[![Groq](https://img.shields.io/badge/LLM-Groq%20API-orange)](https://console.groq.com/)
[![Streamlit](https://img.shields.io/badge/UI-Streamlit-red?logo=streamlit)](https://streamlit.io/)
[![FAISS](https://img.shields.io/badge/Vector%20DB-FAISS-purple)](https://faiss.ai/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 📖 What is Data Theorist AI?

**Data Theorist AI** is a production-ready, RAG-based AI tutor that answers your Data Science questions using **real books** as its knowledge base — not generic internet data.

It doesn't just give you raw answers. It **teaches** you — like a patient tutor — by breaking every concept into:
- A clear **Definition**
- A simple **Intuition** (real-world analogy)
- A hands-on **Example** (code or scenario)
- Key **Notes** and **Source** attribution

> "Ask it about Linear Regression, and it'll cite your ML book, explain the math intuitively, show you Python code, and remind you of the key assumptions — all in one structured response."

---

## 🎯 Features

| Feature | Description |
|---|---|
| 📚 **Multi-Book RAG** | Uses 5 curated Data Science PDFs as knowledge sources |
| 🧠 **Groq LLM** | Powered by Llama 3 via Groq API (ultra-fast inference) |
| 💬 **Conversational Memory** | Remembers last 3–5 turns for context-aware follow-ups |
| 🏫 **Teaching Format** | Every answer is structured: Definition → Intuition → Example → Notes → Source |
| 📊 **Token Tracking** | See token usage per message and total session usage |
| ⚡ **One-Time Embedding** | PDFs are embedded once and cached — no reprocessing on startup |
| 🎨 **Streamlit UI** | Clean, chat-based interface with sidebar controls |
| 🔒 **Modular Architecture** | Fully separated concerns across dedicated modules |

---

## 📚 Knowledge Base

The AI is trained on the following books:

| Book | Topic |
|---|---|
| `machine_learning.pdf` | ML algorithms, theory, and applications |
| `python.pdf` | Python programming fundamentals & data tools |
| `sql.pdf` | SQL queries, databases, and analytics |
| `statistics.pdf` | Statistical methods, probability, and inference |
| `story_telling.pdf` | Data storytelling and visualization principles |

---

## 🏗️ Project Architecture

```
data_theorist_ai/
│
├── 📂 books/                   # Your PDF knowledge base
│   ├── machine_learning.pdf
│   ├── python.pdf
│   ├── sql.pdf
│   ├── statistics.pdf
│   └── story_telling.pdf
│
├── 📂 vector_store/            # Auto-generated FAISS index (gitignored)
│
├── 📂 src/                     # Core business logic (modular)
│   ├── config.py               # All constants and configuration
│   ├── embedder.py             # PDF loader + FAISS vector store builder
│   ├── retriever.py            # Document retrieval from vector store
│   ├── memory.py               # Bounded conversational memory
│   ├── prompt.py               # Teaching-style prompt templates
│   ├── chain.py                # LangChain RAG chain assembly
│   └── token_tracker.py        # Token usage monitoring
│
├── 🚀 app.py                   # Streamlit UI (entry point)
├── 🔧 ingest.py                # One-time PDF ingestion script
├── 📋 requirements.txt         # Dependencies
├── 🔐 .env                     # API keys (never commit!)
├── 📜 SKILLS.md                # Project rules and guidelines
└── 📖 README.md                # This file
```

---

## ⚙️ Setup & Installation

### Prerequisites
- Python 3.10+
- A [Groq API key](https://console.groq.com/) (free tier available)
- PDF books placed in the `books/` directory

### Step 1 — Clone the Repository
```bash
git clone https://github.com/YOUR_USERNAME/data-theorist-ai.git
cd data-theorist-ai
```

### Step 2 — Create a Virtual Environment
```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On Mac/Linux
source venv/bin/activate
```

### Step 3 — Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4 — Configure Environment Variables
Create a `.env` file in the root directory:
```env
GROQ_API_KEY=your_groq_api_key_here
```

### Step 5 — Add Your PDF Books
Place your PDF files in the `books/` folder:
```
books/
├── machine_learning.pdf
├── python.pdf
├── sql.pdf
├── statistics.pdf
└── story_telling.pdf
```

### Step 6 — Ingest PDFs (One-Time Only ⚠️)
```bash
python ingest.py
```
> This creates the `vector_store/` directory with a FAISS index. **You only need to run this once** (or when you add new books).

### Step 7 — Launch the App 🚀
```bash
streamlit run app.py
```

Open your browser at **http://localhost:8501** and start learning!

---

## 💬 How to Use

1. **Ask any Data Science question** in the chat input
2. The AI retrieves relevant passages from your books
3. It generates a **structured teaching response** with:
   - 📘 Definition
   - 💡 Intuition (real-world analogy)
   - 🧪 Example (code or scenario)
   - 📝 Notes (tips, edge cases)
   - 📚 Source (which book it came from)
4. **Follow-up questions** are context-aware (it remembers your conversation)
5. Track your **token usage** in the sidebar

### Example Questions to Try
```
• What is a decision tree?
• Explain overfitting in simple terms
• How does a JOIN work in SQL?
• What is the Central Limit Theorem?
• How do I make a compelling data story?
• What's the difference between supervised and unsupervised learning?
```

---

## 🛠️ Tech Stack

| Component | Technology |
|---|---|
| **LLM** | Llama 3 (8B / 70B) via Groq API |
| **Orchestration** | LangChain |
| **Vector Store** | FAISS (Facebook AI Similarity Search) |
| **Embeddings** | HuggingFace `all-MiniLM-L6-v2` |
| **PDF Parsing** | LangChain PyPDF Loader |
| **UI Framework** | Streamlit |
| **Memory** | LangChain ConversationBufferWindowMemory |
| **Environment** | python-dotenv |

---

## 📊 Token Usage Tracking

Every conversation tracks:
- **Per-message tokens**: prompt + completion tokens for each query
- **Session total**: cumulative tokens used since app start

View this in the sidebar of the Streamlit app.

---

## 🔒 Security & Privacy

- API keys are stored in `.env` — **never hardcoded**
- `.env`, `books/`, and `vector_store/` are all in `.gitignore`
- No data is sent anywhere except to Groq's API for inference

---

## 📋 Requirements

```
langchain>=0.2.0
langchain-groq>=0.1.0
langchain-community>=0.2.0
faiss-cpu>=1.7.4
sentence-transformers>=2.7.0
pypdf>=4.0.0
streamlit>=1.35.0
python-dotenv>=1.0.0
tiktoken>=0.7.0
```

---

## 🗺️ Roadmap

- [x] Core RAG pipeline with FAISS
- [x] Groq LLM integration
- [x] Teaching-style prompt engineering
- [x] Streamlit chat UI
- [x] Token usage tracking
- [x] Conversational memory
- [ ] PDF chapter-level source attribution
- [ ] User query history export
- [ ] Multi-language support
- [ ] Voice input/output
- [ ] Question difficulty selector (Beginner / Intermediate / Advanced)
- [ ] Quiz mode — generate practice questions from books

---

## 🤝 Contributing

Contributions are welcome! Please read [SKILLS.md](./SKILLS.md) first to understand the project rules and architecture guidelines.

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -m 'Add: your feature description'`
4. Push to the branch: `git push origin feature/your-feature`
5. Open a Pull Request

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- [Groq](https://groq.com/) for blazing-fast LLM inference
- [LangChain](https://langchain.com/) for the RAG framework
- [FAISS](https://faiss.ai/) by Meta AI for vector similarity search
- [Streamlit](https://streamlit.io/) for the rapid UI development
- The authors of the books used as the knowledge base

---

<div align="center">

**Built with ❤️ to make Data Science accessible to everyone**

*Data Theorist AI — Learn from books, not the internet*

</div>
