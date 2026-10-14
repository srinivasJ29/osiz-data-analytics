import streamlit as st
import pandas as pd
from src.session_manager import init_session_state, set_stage
from src.data_loader import load_dataset, get_dataset_metadata
from src.data_validator import validate_dataframe
from src.report_generator import export_to_csv

def render_stage_1():
    st.subheader("📤 Stage 1: Dataset Upload & Inspection")
    st.caption("Upload your raw CSV or Excel dataset to automatically profile schema, detect data quality defects, and examine initial summary distributions.")
    st.write("")


    uploaded_file = st.file_uploader(
        "Choose a CSV or Excel file",
        type=["csv", "xlsx", "xls"],
        help="Upload datasets up to 50 MB. Formats supported: .csv, .xlsx, .xls",
        key="file_uploader_stage1"
    )

    # Allow clearing/resetting
    col_upload_actions = st.columns([1, 1, 4])
    with col_upload_actions[0]:
        if st.session_state.get("original_df") is not None:
            if st.button("🔄 Start New Analysis", use_container_width=True):
                st.session_state["original_df"] = None
                st.session_state["working_df"] = None
                st.session_state["filtered_df"] = None
                st.session_state["metadata"] = None
                st.session_state["audit_history"] = []
                st.session_state["undo_stack"] = []
                st.rerun()

    if uploaded_file is not None:
        file_bytes = uploaded_file.getvalue()
        file_size = len(file_bytes)
        
        # Check if already loaded to avoid redundant reloading
        current_meta = st.session_state.get("metadata")
        if current_meta is None or current_meta.get("filename") != uploaded_file.name:
            with st.spinner("Analyzing and parsing dataset..."):
                df, err = load_dataset(uploaded_file, uploaded_file.name)
                if err:
                    st.error(f"⚠️ Error loading file: {err}")
                    return

                # Save into session state
                st.session_state["original_df"] = df.copy()
                st.session_state["working_df"] = df.copy()
                st.session_state["filtered_df"] = df.copy()
                meta = get_dataset_metadata(df, uploaded_file.name, file_size)
                st.session_state["metadata"] = meta
                st.session_state["audit_history"] = [{
                    "action": f"Uploaded file: {uploaded_file.name}",
                    "affected": len(df),
                    "timestamp": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
                }]
                st.success(f"✅ Successfully loaded '{uploaded_file.name}' with {len(df):,} rows and {len(df.columns)} columns!")

    df = st.session_state.get("working_df")
    meta = st.session_state.get("metadata")

    if df is not None and meta is not None:
        # Metrics Row
        st.markdown("#### 📊 Dataset Metrics Overview")
        m1, m2, m3, m4, m5 = st.columns(5)
        m1.metric("Total Records", f"{meta['total_rows']:,}")
        m2.metric("Total Columns", f"{meta['total_cols']:,}")
        m3.metric("Numerical Columns", len(meta["numerical_columns"]))
        m4.metric("Categorical Columns", len(meta["categorical_columns"]))
        m5.metric("Duplicate Rows", f"{meta['duplicate_rows']:,}")

        # Data Health Validation
        val_result = validate_dataframe(df)
        if val_result.get("warnings"):
            with st.expander("⚠️ Data Quality Alerts & Observations", expanded=True):
                for w in val_result["warnings"]:
                    st.warning(f"• {w}")

        # Original Data Download
        col_dl, col_nav = st.columns([1, 1])
        with col_dl:
            csv_bytes = export_to_csv(st.session_state["original_df"])
            st.download_button(
                label="📥 Download Original Uploaded CSV",
                data=csv_bytes,
                file_name=f"original_{meta['filename'].split('.')[0]}.csv",
                mime="text/csv",
                use_container_width=True
            )
        with col_nav:
            if st.button("Proceed to Stage 2: Data Management ➡️", type="primary", use_container_width=True):
                set_stage(2)
                st.rerun()

        # Preview Data Table
        st.markdown("#### 🔍 Interactive Dataset Preview")
        st.dataframe(df.head(100), use_container_width=True, height=320)

        # Detailed Column Schema Profile
        st.markdown("#### 📋 Column Schema & Health Profile")
        st.dataframe(meta["column_profiles"], use_container_width=True)

        # Statistical Summary Preview
        with st.expander("📈 Initial Statistical Distribution (Numerical Features)", expanded=False):
            num_cols = meta["numerical_columns"]
            if num_cols:
                st.dataframe(df[num_cols].describe().T, use_container_width=True)
            else:
                st.info("No numerical features detected in this dataset.")
    else:
        st.info("👆 Please upload a CSV or Excel file to get started.")

if __name__ == "__main__":
    init_session_state()
    render_stage_1()
