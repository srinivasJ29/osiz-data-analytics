import streamlit as st
import pandas as pd
import importlib

stage1_mod = importlib.import_module("pages.1_Upload_and_Inspection")
stage2_mod = importlib.import_module("pages.2_Data_Management")
stage3_mod = importlib.import_module("pages.3_Visualization")
stage4_mod = importlib.import_module("pages.4_Report_Generation")

render_stage_1 = stage1_mod.render_stage_1
render_stage_2 = stage2_mod.render_stage_2
render_stage_3 = stage3_mod.render_stage_3
render_stage_4 = stage4_mod.render_stage_4

from src.session_manager import init_session_state, set_stage



# Page config
st.set_page_config(
    page_title="Smart Data Analyzer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern visual design
st.markdown("""
<style>
    /* Global Styling */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* Main Container Padding */
    .block-container {
        padding-top: 1.8rem;
        padding-bottom: 3rem;
    }

    /* Top Brand Banner */
    .brand-banner {
        background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 100%);
        padding: 24px 32px;
        border-radius: 12px;
        color: white;
        margin-bottom: 24px;
        box-shadow: 0 4px 14px rgba(15, 23, 42, 0.12);
    }
    .brand-banner h1 {
        margin: 0;
        font-size: 26px;
        font-weight: 700;
        letter-spacing: -0.5px;
        color: #ffffff;
    }
    .brand-banner p {
        margin: 6px 0 0 0;
        color: #cbd5e1;
        font-size: 14px;
    }

    /* Workflow Stage Step Indicators */
    .stepper-container {
        display: flex;
        justify-content: space-between;
        margin-bottom: 24px;
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 12px 18px;
    }
    .step-item {
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 13px;
        font-weight: 600;
        color: #64748b;
    }
    .step-item.active {
        color: #1e3a8a;
    }
    .step-circle {
        width: 26px;
        height: 26px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        background-color: #e2e8f0;
        color: #475569;
        font-size: 12px;
    }
    .step-item.active .step-circle {
        background-color: #1e3a8a;
        color: #ffffff;
    }

    /* Card styling */
    .stage-card {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 16px 20px;
        margin-bottom: 20px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.02);
    }
</style>
""", unsafe_allow_html=True)

init_session_state()

# Top Brand Banner
st.markdown("""
<div class="brand-banner">
    <h1>Smart Data Analyzer</h1>
    <p>Professional end-to-end dataset inspection, cleaning, filtering, analytics & report generation system</p>
</div>
""", unsafe_allow_html=True)

# Stage navigation buttons in sidebar
with st.sidebar:
    st.markdown("### 🧭 Workflow Navigation")
    
    current_stage = st.session_state.get("current_stage", 1)
    
    stages = [
        (1, "1. Upload & Inspection", "📤"),
        (2, "2. Data Management & Cleaning", "🛠️"),
        (3, "3. Visualization & Analytics", "📊"),
        (4, "4. Summary & Report Export", "📄")
    ]

    for stage_num, stage_title, icon in stages:
        is_active = (current_stage == stage_num)
        btn_type = "primary" if is_active else "secondary"
        if st.button(f"{icon} {stage_title}", key=f"sidebar_nav_{stage_num}", type=btn_type, use_container_width=True):
            set_stage(stage_num)
            st.rerun()

    st.markdown("---")
    st.markdown("### ℹ️ Dataset Status")
    working_df = st.session_state.get("working_df")
    filtered_df = st.session_state.get("filtered_df")
    metadata = st.session_state.get("metadata")

    if working_df is not None and metadata is not None:
        st.write(f"📁 **File:** `{metadata.get('filename')}`")
        st.write(f"🔢 **Working Rows:** `{len(working_df):,}`")
        st.write(f"🔍 **Filtered Rows:** `{len(filtered_df):,}`")
        st.write(f"📐 **Columns:** `{len(working_df.columns)}`")
    else:
        st.caption("No dataset loaded yet.")

    st.markdown("---")
    st.caption("Built with Python, Streamlit, Plotly, Pandas, ReportLab & python-docx.")

# Progress indicator stepper using pure Streamlit components
stage_names = ["Upload & Profile", "Clean & Filter", "Visualize & Analyze", "Generate Reports"]
current_stage = st.session_state.get("current_stage", 1)

# Stepper header
step_cols = st.columns(4)
for idx, sname in enumerate(stage_names, 1):
    with step_cols[idx - 1]:
        if idx == current_stage:
            st.info(f"**Step {idx}: {sname}** (Active)")
        elif idx < current_stage:
            st.success(f"✓ Step {idx}: {sname}")
        else:
            st.text(f"Step {idx}: {sname}")

st.progress(current_stage / 4.0)
st.write("")



# Render active stage
current_stage = st.session_state.get("current_stage", 1)
if current_stage == 1:
    render_stage_1()
elif current_stage == 2:
    render_stage_2()
elif current_stage == 3:
    render_stage_3()
elif current_stage == 4:
    render_stage_4()
