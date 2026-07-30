import streamlit as st
import requests
import os
import json

st.set_page_config(page_title="Human Review Queue - AMC MediaOps", page_icon="👥", layout="wide")

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

st.markdown(
    """
    <style>
    .gradient-header {
        background: linear-gradient(135deg, #f1c40f 0%, #f39c12 100%);
        padding: 15px;
        border-radius: 8px;
        color: white;
        margin-bottom: 20px;
    }
    .review-box {
        background-color: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 8px;
        padding: 20px;
        margin-bottom: 15px;
    }
    .risk-flag {
        background-color: rgba(231, 76, 60, 0.2);
        border-left: 5px solid #e74c3c;
        padding: 10px;
        border-radius: 4px;
        margin-bottom: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown('<div class="gradient-header"><h2>👥 Human-in-the-Loop Review Queue</h2></div>', unsafe_allow_html=True)
st.write("Inspect intelligence packs flagged for human oversight due to high risks or low confidence scores.")

if st.button("🔄 Refresh Queue"):
    st.rerun()

try:
    res = requests.get(f"{BACKEND_URL}/api/review-queue")
    if res.status_code == 200:
        queue = res.json()
        if not queue:
            st.success("✅ Clean Queue! No tasks require human intervention at the moment.")
        else:
            for task in queue:
                task_id = task["task_id"]
                st.subheader(f"Task ID: {task_id}")
                
                col1, col2 = st.columns(2)
                
                pack = task["intelligence_pack"] or {}
                evaluation = task["evaluation"] or {}
                
                with col1:
                    st.markdown("### Raw Media Content")
                    st.text_area("Input Content", value=task["content"], height=250, disabled=True, key=f"raw_{task_id}")
                    
                    st.markdown("### Judge Evaluation Details")
                    st.markdown(f"**Factuality Score:** `{evaluation.get('factuality_score', 'N/A')}/10`")
                    st.markdown(f"**Policy Compliance:** `{evaluation.get('policy_compliance', 'N/A')}`")
                    st.markdown(f"**Feedback:** {evaluation.get('feedback', 'No feedback')}")
                    
                with col2:
                    st.markdown("### Draft Editorial Pack (Edit directly to Modify)")
                    
                    # Create editable form fields
                    edited_summary = st.text_area("Executive Summary", value=pack.get("executive_summary", ""), key=f"sum_{task_id}", height=120)
                    
                    # Simple lists to edit (comma separated)
                    themes_str = st.text_input("Key Themes (comma separated)", value=", ".join(pack.get("key_themes", [])), key=f"themes_{task_id}")
                    tags_str = st.text_input("Metadata Tags (comma separated)", value=", ".join(pack.get("metadata_tags", [])), key=f"tags_{task_id}")
                    
                    # Highlight risks
                    risks = pack.get("editorial_risk_flags", [])
                    st.markdown("**Identified Risks:**")
                    if risks:
                        for risk in risks:
                            st.markdown(f'<div class="risk-flag">⚠️ {risk}</div>', unsafe_allow_html=True)
                    else:
                        st.write("No major risks flagged.")
                        
                    risks_str = st.text_input("Modify Risk Flags (comma separated)", value=", ".join(risks), key=f"risks_{task_id}")
                    headlines_str = st.text_input("Suggested Headlines (comma separated)", value=", ".join(pack.get("suggested_headlines", [])), key=f"headlines_{task_id}")

                # Human review decision
                st.markdown("### Take Action")
                feedback = st.text_input("Internal Editor Notes / Feedback", key=f"fb_{task_id}", placeholder="Explain reason for decision...")
                
                action_col1, action_col2, action_col3 = st.columns(3)
                
                # Setup modified pack structure
                modified_pack = {
                    "executive_summary": edited_summary,
                    "key_themes": [x.strip() for x in themes_str.split(",") if x.strip()],
                    "metadata_tags": [x.strip() for x in tags_str.split(",") if x.strip()],
                    "editorial_risk_flags": [x.strip() for x in risks_str.split(",") if x.strip()],
                    "suggested_headlines": [x.strip() for x in headlines_str.split(",") if x.strip()]
                }
                
                with action_col1:
                    if st.button("🟢 Approve As Is", key=f"app_{task_id}", use_container_width=True):
                        payload = {"action": "approve", "feedback": feedback}
                        res = requests.post(f"{BACKEND_URL}/api/review/{task_id}", json=payload)
                        if res.status_code == 200:
                            st.success("Task approved!")
                            st.rerun()
                        else:
                            st.error(f"Error: {res.text}")
                            
                with action_col2:
                    if st.button("🔵 Apply Modifications & Approve", key=f"mod_{task_id}", use_container_width=True):
                        payload = {"action": "modify", "modified_pack": modified_pack, "feedback": feedback}
                        res = requests.post(f"{BACKEND_URL}/api/review/{task_id}", json=payload)
                        if res.status_code == 200:
                            st.success("Task modified and approved!")
                            st.rerun()
                        else:
                            st.error(f"Error: {res.text}")
                            
                with action_col3:
                    if st.button("🔴 Reject Output", key=f"rej_{task_id}", use_container_width=True):
                        payload = {"action": "reject", "feedback": feedback}
                        res = requests.post(f"{BACKEND_URL}/api/review/{task_id}", json=payload)
                        if res.status_code == 200:
                            st.success("Task rejected!")
                            st.rerun()
                        else:
                            st.error(f"Error: {res.text}")
                
                st.markdown("---")
    else:
        st.error(f"Error fetching review queue: {res.text}")
except Exception as e:
    st.error(f"Could not connect to FastAPI backend: {e}")
