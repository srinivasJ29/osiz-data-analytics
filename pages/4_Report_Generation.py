import streamlit as st
import pandas as pd
from datetime import datetime
from src.session_manager import init_session_state, set_stage
from src.analytics import compute_numerical_summary, compute_categorical_summary, generate_automated_insights, compute_dataset_kpis
from src.report_generator import generate_pdf_report, generate_word_report, export_to_csv, export_to_excel

def render_stage_4():
    st.subheader("📄 Stage 4: Overall Summary & Publication Report Generation")
    st.caption("Compile executive analytics, statistical profiles, and audit histories into branded, publication-ready PDF, Word (.docx), Excel, and CSV files.")
    st.write("")


    if st.session_state.get("working_df") is None:
        st.warning("⚠️ No dataset uploaded yet. Please proceed to Stage 1.")
        if st.button("⬅️ Go to Stage 1"):
            set_stage(1)
            st.rerun()
        return

    # Scope Selection
    scope_col, title_col = st.columns([1, 2])
    with scope_col:
        scope = st.selectbox("Reporting Data Scope", ["Cleaned Working Data", "Filtered Data", "Original Uploaded Data"])
    with title_col:
        report_title = st.text_input("Report Title", value="Executive Data Quality & Analytics Report")

    # Author & Sections
    auth_col, date_col = st.columns([1, 1])
    with auth_col:
        author_name = st.text_input("Author / Analyst Name", value="Senior Data Analyst")
    with date_col:
        st.text_input("Generation Date", value=datetime.now().strftime("%B %d, %Y"), disabled=True)

    # Resolve dataset scope
    if scope == "Original Uploaded Data":
        df = st.session_state.get("original_df")
    elif scope == "Cleaned Working Data":
        df = st.session_state.get("working_df")
    else:
        df = st.session_state.get("filtered_df", st.session_state.get("working_df"))

    if df is None or df.empty:
        st.error("Selected scope dataset is empty.")
        return

    # Section selection
    st.markdown("#### 📑 Report Content Configuration")
    sections = st.multiselect(
        "Sections to include in generated report:",
        options=["Dataset Overview", "Data Quality & Operations", "Statistical Summary", "Automated Insights"],
        default=["Dataset Overview", "Data Quality & Operations", "Statistical Summary", "Automated Insights"]
    )

    # Compute profiling data
    from src.data_loader import get_dataset_metadata
    meta = get_dataset_metadata(df, st.session_state.get("metadata", {}).get("filename", "Dataset"))
    stats_df = compute_numerical_summary(df)
    insights = generate_automated_insights(df)
    audit_history = st.session_state.get("audit_history", [])

    st.markdown("---")
    st.markdown("#### 👁️ Report Live Preview")

    # Summary Preview Box
    with st.container():
        p1, p2, p3, p4 = st.columns(4)
        p1.metric("Analyzed Rows", f"{len(df):,}")
        p2.metric("Analyzed Columns", len(df.columns))
        p3.metric("Missing Cells", int(df.isna().sum().sum()))
        p4.metric("Logged Actions", len(audit_history))

        st.markdown("##### 📌 Key Analytical Findings Preview")
        for ins in insights[:3]:
            st.markdown(f"- **{ins['title']}**: {ins['text']}")

        if not stats_df.empty:
            st.markdown("##### 📈 Statistical Distribution Preview")
            st.dataframe(stats_df.head(5), use_container_width=True)

    st.markdown("---")
    st.markdown("#### 📥 Download Publication Reports")

    col_pdf, col_docx, col_excel, col_csv = st.columns(4)

    # 1. PDF Download
    with col_pdf:
        with st.spinner("Generating PDF..."):
            pdf_bytes = generate_pdf_report(
                metadata=meta,
                stats_df=stats_df,
                insights=insights,
                audit_history=audit_history,
                scope_name=scope,
                report_title=report_title,
                author_name=author_name,
                selected_sections=sections
            )
        st.download_button(
            label="📕 Download PDF Report",
            data=pdf_bytes,
            file_name=f"Smart_Data_Report_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
            mime="application/pdf",
            use_container_width=True,
            type="primary"
        )

    # 2. Word (.docx) Download
    with col_docx:
        with st.spinner("Compiling Word Document..."):
            docx_bytes = generate_word_report(
                metadata=meta,
                stats_df=stats_df,
                insights=insights,
                audit_history=audit_history,
                scope_name=scope,
                report_title=report_title,
                author_name=author_name
            )
        st.download_button(
            label="📘 Download Word Report (.docx)",
            data=docx_bytes,
            file_name=f"Smart_Data_Report_{datetime.now().strftime('%Y%m%d_%H%M')}.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            use_container_width=True
        )

    # 3. Excel Download
    with col_excel:
        excel_bytes = export_to_excel(df, sheet_name=scope[:31])
        st.download_button(
            label="📗 Download Excel Workbook",
            data=excel_bytes,
            file_name=f"Data_Export_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

    # 4. CSV Download
    with col_csv:
        csv_bytes = export_to_csv(df)
        st.download_button(
            label="📄 Download Cleaned CSV",
            data=csv_bytes,
            file_name=f"Data_Export_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv",
            use_container_width=True
        )

if __name__ == "__main__":
    init_session_state()
    render_stage_4()
