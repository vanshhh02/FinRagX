import sys
import os
import subprocess
import streamlit as st
from pathlib import Path

# --------------------------------------------------
# FIX PYTHON PATH
# --------------------------------------------------
ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT_DIR))

from app.rag import RAGPipeline

DATA_DIR = ROOT_DIR / "data"

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------
st.set_page_config(
    page_title="FinRAGX – Enterprise RAG",
    page_icon="📄",
    layout="wide"
)

# --------------------------------------------------
# CUSTOM CSS
# --------------------------------------------------
st.markdown("""
<style>
body { background-color: #0e1117; }
h1, h2, h3 { color: #ffffff; }
.block-container { padding-top: 2rem; }

.card {
    background: #161b22;
    padding: 1.5rem;
    border-radius: 12px;
    border: 1px solid #30363d;
    margin-bottom: 1.2rem;
}

.user {
    background: #0d1117;
    padding: 1rem;
    border-radius: 8px;
    border-left: 4px solid #58a6ff;
    margin-bottom: 0.8rem;
}

.assistant {
    background: #0d1117;
    padding: 1rem;
    border-radius: 8px;
    border-left: 4px solid #3fb950;
    margin-bottom: 1.2rem;
}
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------
st.sidebar.title("⚙️ FinRAGX Controls")

TOP_K = st.sidebar.slider("Top Chunks Retrieved", 3, 15, 5)
MEMORY_TURNS = st.sidebar.slider("Conversation Memory Turns", 1, 6, 3)
SHOW_TRACE = st.sidebar.checkbox("Show Retrieval Trace", False)

if st.sidebar.button("🧹 Clear Chat"):
    st.session_state.chat_history = []

st.sidebar.markdown("---")
st.sidebar.markdown("""
### 🧠 Enabled Features
- Hierarchical RAG  
- Multi-Agent Validation  
- Chat Memory  
- Citations  
""")

# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# --------------------------------------------------
# LOAD RAG
# --------------------------------------------------
@st.cache_resource
def load_rag(top_k):
    return RAGPipeline(top_k=top_k)

rag = load_rag(TOP_K)

# --------------------------------------------------
# HEADER
# --------------------------------------------------
st.markdown("# 📄 FinRAGX – Enterprise RAG System")
st.markdown(
    "Conversational Memory · Grounded Retrieval · Enterprise Validation"
)

st.markdown("---")

# --------------------------------------------------
# PDF UPLOAD
# --------------------------------------------------
st.markdown("## 📤 Upload Documents")

uploaded_files = st.file_uploader(
    "Upload PDF files",
    type=["pdf"],
    accept_multiple_files=True
)

if uploaded_files:
    os.makedirs(DATA_DIR, exist_ok=True)

    for file in uploaded_files:
        with open(DATA_DIR / file.name, "wb") as f:
            f.write(file.getbuffer())

    st.success(f"Uploaded {len(uploaded_files)} file(s).")

    if st.button("🔄 Ingest Documents"):
        with st.spinner("Ingesting..."):
            subprocess.run(
                ["python", "-m", "scripts.ingest"],
                cwd=str(ROOT_DIR)
            )
            st.cache_resource.clear()
            st.success("Ingestion complete.")

st.markdown("---")

# --------------------------------------------------
# CHAT HISTORY DISPLAY
# --------------------------------------------------
st.markdown("## 💬 Conversation")

for turn in st.session_state.chat_history:
    st.markdown(
        f"<div class='user'><b>User:</b> {turn['question']}</div>",
        unsafe_allow_html=True
    )
    st.markdown(
        f"<div class='assistant'><b>Assistant:</b><br>{turn['answer']}</div>",
        unsafe_allow_html=True
    )

# --------------------------------------------------
# USER INPUT
# --------------------------------------------------
query = st.text_input(
    "Ask a question",
    placeholder="What does GDPR say about data security?"
)

if query:
    # --------------------------------------------------
    # BUILD MEMORY CONTEXT
    # --------------------------------------------------
    memory_context = ""
    for turn in st.session_state.chat_history[-MEMORY_TURNS:]:
        memory_context += f"User: {turn['question']}\nAssistant: {turn['answer']}\n"

    full_query = f"""
Conversation so far:
{memory_context}

Current question:
{query}
"""

    with st.spinner("🔍 Thinking..."):
        answer = rag.run(full_query)

    # Save to memory
    st.session_state.chat_history.append({
        "question": query,
        "answer": answer
    })

    st.experimental_rerun()

# --------------------------------------------------
# FOOTER
# --------------------------------------------------
st.markdown("---")
st.markdown(
    "<center>🚀 FinRAGX — Conversational Enterprise RAG</center>",
    unsafe_allow_html=True
)
