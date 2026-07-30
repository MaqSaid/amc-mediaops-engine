import streamlit as st

st.set_page_config(
    page_title="AMC MediaOps Engine",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom premium styling
st.markdown(
    """
    <style>
    /* Gradient banner header */
    .banner {
        background: linear-gradient(135deg, #001f3f 0%, #0056b3 50%, #00d2ff 100%);
        padding: 35px;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 25px;
        box-shadow: 0 8px 32px 0 rgba(0, 86, 179, 0.2);
    }
    .banner h1 {
        font-family: 'Outfit', 'Inter', sans-serif;
        font-weight: 800;
        font-size: 2.8rem;
        margin: 0;
        letter-spacing: -1px;
    }
    .banner p {
        font-size: 1.15rem;
        opacity: 0.9;
        margin-top: 10px;
    }
    /* Glassmorphic Cards */
    .card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    .card h3 {
        color: #00d2ff;
        margin-top: 0;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="banner">
        <h1>🎬 AMC MediaOps Agentic Workflow Engine</h1>
        <p>Production-Grade Multi-Agent Editorial Intelligence & Compliance Suite</p>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown("### Welcome to the AMC Editorial Command")
st.write(
    "This platform automates media briefing ingestion, runs deep semantic memory lookups, "
    "extracts metadata and policy risk factors, runs structured judge evaluation, and escalates high-risk content to editors via "
    "Human-in-the-Loop (HITL) checkpoints. Engineered with Google Antigravity SDK, Vertex AI, and Cloud Run architecture."
)


col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(
        """
        <div class="card">
            <h3>🤖 1. Orchestrated Agents</h3>
            <p>A Supervisor Agent decomposes incoming transcripts, briefs, or articles, assigning specific tasks to specialised Retrieval, Metadata, and Writer Agents built with <b>Google ADK</b>.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

with col2:
    st.markdown(
        """
        <div class="card">
            <h3>🔬 2. Auto-Evaluation</h3>
            <p>Every generated pack undergoes rigorous automated testing by an ethical Judge Agent checking for compliance, factual accuracy, and legal liability (e.g. defamation risks).</p>
        </div>
        """,
        unsafe_allow_html=True
    )

with col3:
    st.markdown(
        """
        <div class="card">
            <h3>👥 3. Human in the Loop</h3>
            <p>High-risk or low-confidence outputs automatically trigger workflow suspension, pushing files to the Human Review Queue for review, edit, or approval before finalisation.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

st.markdown("---")

st.markdown("### System Quick Links")
st.info("💡 Navigation Tip: Use the sidebar menu to submit media files, review items waiting in queue, or trace agent tasks step-by-step.")
