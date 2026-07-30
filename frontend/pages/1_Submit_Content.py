import streamlit as st
import requests
import os
import json

st.set_page_config(page_title="Submit Content - AMC MediaOps", page_icon="📝", layout="wide")

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

st.markdown(
    """
    <style>
    .gradient-header {
        background: linear-gradient(135deg, #1f4037 0%, #99f2c8 100%);
        padding: 15px;
        border-radius: 8px;
        color: white;
        margin-bottom: 20px;
    }
    .task-card {
        background-color: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown('<div class="gradient-header"><h2>📝 Ingest Raw Media & Execute Agents</h2></div>', unsafe_allow_html=True)

# Examples to auto-populate
st.subheader("Quick Mock Inputs")
example_selection = st.selectbox(
    "Choose a preset template or choose 'None' to enter custom content:",
    [
        "None",
        "Sports Broadcast Briefing (IOC Rights)",
        "ACA Investigative Segment (Retail Leak)",
        "Legal Guidelines (Sub Judice Rules)"
    ]
)

# Text inputs
content = ""
content_type = "transcript"
source = "AMC News"

if example_selection == "Sports Broadcast Briefing (IOC Rights)":
    content = "Transcript from Australian Media Channel Executive Briefing: The sports division will broadcast the upcoming Olympic Games. We must prioritize live multi-platform distribution. Our coverage should align with editorial integrity: neutrality, accuracy, and highlighting local athletes. Commercial slots should not overlap with critical athletic finals. Legal risks include trademark infringement of the IOC rings and exclusive sponsor protections."
    content_type = "brief"
    source = "AMC Executive Sports Committee"
elif example_selection == "ACA Investigative Segment (Retail Leak)":
    content = "Special Report transcript: A major national retail brand has leaked customer profiles. Reporter: 'Is this cyber attack a result of outdated security?' Analyst: 'It appears so. The breach affects over two million Australians. Under current privacy acts, corporations must disclose immediately.' Editorial guidelines: Ensure we protect the identities of individual victims and verify source materials from hacker forums using independent cyber-forensic experts."
    content_type = "transcript"
    source = "Daily Investigative News"
elif example_selection == "Legal Guidelines (Sub Judice Rules)":
    content = "Official Guidelines: Coverage of active trials in Australian courts must respect sub judice rules to avoid contempt of court. Reporters must not publish any content that could prejudice a fair trial, including previous convictions, speculation on guilt, or interviewing witnesses during an active trial. All court reporting needs a senior legal sign-off. Defamation risks are extremely high, legal check required."
    content_type = "article"
    source = "AMC Editorial Legal Counsel"

with st.form("submit_form"):
    source = st.text_input("Source Division", value=source)
    content_type = st.selectbox("Content Classification Type", ["transcript", "article", "brief"], index=["transcript", "article", "brief"].index(content_type))
    content = st.text_area("Content Body", value=content, height=250)
    
    submitted = st.form_submit_button("Submit Content to Orchestrator 🚀")
    
    if submitted:
        if not content.strip():
            st.error("Error: Content body cannot be empty!")
        else:
            payload = {
                "content": content,
                "content_type": content_type,
                "source": source
            }
            try:
                res = requests.post(f"{BACKEND_URL}/api/submit", json=payload)
                if res.status_code == 200:
                    data = res.json()
                    st.success(f"Task submitted successfully! Task ID: {data['task_id']}")
                    st.info(f"Agents are executing in the background. Status: {data['status']}")
                else:
                    st.error(f"Failed to submit: {res.text}")
            except Exception as e:
                st.error(f"Could not connect to FastAPI backend: {e}")

st.markdown("---")
st.subheader("Active Tasks & Jobs Status")

# Refresh list button
if st.button("🔄 Refresh Task List"):
    st.rerun()

try:
    res = requests.get(f"{BACKEND_URL}/api/tasks")
    if res.status_code == 200:
        tasks = res.json()
        if not tasks:
            st.write("No tasks found in system. Submit content above to start!")
        else:
            for task in tasks:
                status_color = "#00d2ff"  # blue for running
                if task["status"] == "completed":
                    status_color = "#2ecc71"
                elif task["status"] == "pending_review":
                    status_color = "#f1c40f"
                elif task["status"] == "failed":
                    status_color = "#e74c3c"
                
                with st.expander(f"Task: {task['task_id']} | Type: {task['content_type'].upper()} | Source: {task['source']}"):
                    st.markdown(
                        f"""
                        <div class="task-card">
                            <p><b>Status:</b> <span style="color:{status_color}; font-weight:bold;">{task['status'].upper()}</span></p>
                            <p><b>Created At:</b> {task['created_at']}</p>
                            <p><b>Content Snippet:</b> {task['content'][:150]}...</p>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                    if task["intelligence_pack"]:
                        st.json(task["intelligence_pack"])
    else:
        st.error(f"Error fetching tasks: {res.text}")
except Exception as e:
    st.error(f"Could not connect to FastAPI backend: {e}")
