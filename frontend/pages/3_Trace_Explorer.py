import streamlit as st
import requests
import os
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Trace Explorer - AMC MediaOps", page_icon="📊", layout="wide")

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

st.markdown(
    """
    <style>
    .gradient-header {
        background: linear-gradient(135deg, #00c6ff 0%, #0072ff 100%);
        padding: 15px;
        border-radius: 8px;
        color: white;
        margin-bottom: 20px;
    }
    .node-log {
        background-color: rgba(255, 255, 255, 0.05);
        border-left: 5px solid #00d2ff;
        padding: 15px;
        border-radius: 4px;
        margin-bottom: 12px;
    }
    .metric-value {
        font-size: 24px;
        font-weight: bold;
        color: #00d2ff;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown('<div class="gradient-header"><h2>📊 Agent Trace Explorer</h2></div>', unsafe_allow_html=True)
st.write("Drill down into agent pipeline step-by-step executions, latency parameters, tool input/output logs, and cost models.")

# Fetch tasks to choose from
task_options = []
tasks_map = {}
try:
    res = requests.get(f"{BACKEND_URL}/api/tasks")
    if res.status_code == 200:
        tasks = res.json()
        for t in tasks:
            label = f"{t['task_id'][:8]}... | Type: {t['content_type'].upper()} | Status: {t['status'].upper()}"
            task_options.append(label)
            tasks_map[label] = t["task_id"]
except Exception as e:
    st.error(f"Could not load tasks: {e}")

if not task_options:
    st.info("No active tasks to explore. Run a task on the 'Submit Content' page first.")
else:
    selected_label = st.selectbox("Select Task to Analyze", task_options)
    task_id = tasks_map[selected_label]
    
    # Fetch details
    try:
        details_res = requests.get(f"{BACKEND_URL}/api/tasks/{task_id}")
        if details_res.status_code == 200:
            data = details_res.json()
            task = data["task"]
            traces = data["traces"]
            
            # Key statistics
            total_duration = sum(tr["duration_ms"] for tr in traces)
            total_steps = len(traces)
            
            # Display KPIs
            st.markdown("### Execution Statistics")
            metric_col1, metric_col2, metric_col3 = st.columns(3)
            with metric_col1:
                st.markdown(f'<div class="node-log"><b>Total Pipeline Latency</b><br><span class="metric-value">{total_duration/1000:.2f}s</span></div>', unsafe_allow_html=True)
            with metric_col2:
                st.markdown(f'<div class="node-log"><b>Total Agent Steps</b><br><span class="metric-value">{total_steps}</span></div>', unsafe_allow_html=True)
            with metric_col3:
                status_color = "#2ecc71" if task["status"] == "completed" else "#f1c40f" if task["status"] == "pending_review" else "#e74c3c"
                st.markdown(f'<div class="node-log"><b>Workflow Terminal Status</b><br><span class="metric-value" style="color:{status_color};">{task["status"].upper()}</span></div>', unsafe_allow_html=True)
            
            # Latency Breakdown Chart
            if traces:
                st.markdown("### Latency Breakdown by Agent Node")
                df_traces = pd.DataFrame(traces)
                fig = px.bar(
                    df_traces,
                    x="node_name",
                    y="duration_ms",
                    labels={"node_name": "Agent Node", "duration_ms": "Latency (ms)"},
                    title="Agent Node Execution Speed",
                    template="plotly_dark"
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # Chronological logs
            st.markdown("### Process Trace Logs (Chronological Order)")
            for idx, trace in enumerate(traces):
                with st.expander(f"Step {idx+1}: {trace['node_name']} ({trace['duration_ms']:.1f} ms)"):
                    st.markdown(f"**Timestamp:** `{trace['timestamp']}`")
                    if trace["error_message"]:
                        st.error(f"Error: {trace['error_message']}")
                    
                    inner_col1, inner_col2 = st.columns(2)
                    with inner_col1:
                        st.markdown("**Node Input:**")
                        st.json(trace["inputs"])
                    with inner_col2:
                        st.markdown("**Node Output:**")
                        st.json(trace["outputs"])
        else:
            st.error("Failed to load task traces.")
    except Exception as e:
        st.error(f"Error connecting to backend: {e}")
