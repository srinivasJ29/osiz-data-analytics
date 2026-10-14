import streamlit as st
import pandas as pd
from src.session_manager import init_session_state, set_stage, clear_all_filters
from src.analytics import compute_dataset_kpis, compute_numerical_summary, compute_categorical_summary, generate_automated_insights
from src.visualization import recommend_charts, create_chart, THEME_PALETTES

def render_stage_3():
    st.subheader("📊 Stage 3: Interactive Data Visualization & Analytics")
    st.caption("Explore distribution curves, multivariate relationships, automatic chart recommendations, and data-driven analytical insights synced live with your active dataset.")
    st.write("")


    if st.session_state.get("working_df") is None:
        st.warning("⚠️ No dataset loaded. Please upload a dataset in Stage 1.")
        if st.button("⬅️ Go to Stage 1"):
            set_stage(1)
            st.rerun()
        return

    # Choose analysis scope
    scope_col, nav_col = st.columns([3, 1])
    with scope_col:
        scope = st.radio("Active Analytics Scope:", ["Filtered Data", "Cleaned Working Data", "Original Data"], horizontal=True)
    with nav_col:
        if st.button("Proceed to Stage 4: Report Generation ➡️", type="primary", use_container_width=True):
            set_stage(4)
            st.rerun()

    if scope == "Original Data":
        df = st.session_state.get("original_df")
    elif scope == "Cleaned Working Data":
        df = st.session_state.get("working_df")
    else:
        df = st.session_state.get("filtered_df", st.session_state.get("working_df"))

    if df is None or df.empty:
        st.error("⚠️ The selected dataset scope is empty (0 records). Try adjusting or resetting your filters in Stage 2.")
        if st.button("🔄 Reset Filters"):
            clear_all_filters()
            st.rerun()
        return

    # 1. SUMMARY CARDS
    kpis = compute_dataset_kpis(df, st.session_state.get("original_df"))
    st.markdown("#### 📌 Key Performance Indicators (KPIs)")
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.metric("Total Records", f"{kpis['total_rows']:,}")
    c2.metric("Total Columns", kpis["total_cols"])
    c3.metric("Numerical Features", kpis["num_numerical"])
    c4.metric("Categorical Features", kpis["num_categorical"])
    c5.metric("Missing Cells", f"{kpis['missing_cells']:,}")
    c6.metric("Retention Ratio", f"{kpis['retention_pct']}%")

    st.markdown("---")

    # 2. AUTOMATED INSIGHTS
    st.markdown("#### 💡 Automated Data-Driven Insights")
    insights = generate_automated_insights(df)
    insight_cols = st.columns(min(len(insights), 3)) if insights else []
    for i, ins in enumerate(insights):
        col_idx = i % 3
        with insight_cols[col_idx]:
            icon = "ℹ️" if ins["type"] == "info" else ("⚠️" if ins["type"] == "warning" else "✅")
            st.info(f"**{icon} {ins['title']}**\n\n{ins['text']}")

    st.markdown("---")

    # 3. AUTOMATIC CHART RECOMMENDATIONS
    st.markdown("#### 🤖 Smart Recommended Visualizations")
    recs = recommend_charts(df)
    if recs:
        rec_tabs = st.tabs([r["title"] for r in recs])
        for idx, r in enumerate(recs):
            with rec_tabs[idx]:
                st.caption(f"**Suggestion logic:** {r['description']}")
                fig = create_chart(
                    df=df,
                    chart_type=r["type"],
                    x_col=r["x"],
                    y_col=r["y"],
                    color_col=r["color"],
                    title=r["title"]
                )
                st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No automatic chart patterns inferred.")

    st.markdown("---")

    # 4. CUSTOM INTERACTIVE CHART BUILDER
    st.markdown("#### 🎨 Custom Interactive Chart Studio")
    with st.expander("Configure Chart Parameters", expanded=True):
        p_col1, p_col2, p_col3, p_col4 = st.columns(4)
        
        all_cols = list(df.columns)
        num_cols = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]
        
        with p_col1:
            chart_type = st.selectbox(
                "Chart Type",
                ["Histogram", "Box Plot", "Scatter Plot", "Bar Chart", "Donut / Pie Chart", "Line Chart", "Correlation Heatmap"]
            )
        with p_col2:
            x_col = st.selectbox("X-Axis / Category Column", options=["None"] + all_cols)
            x_col = None if x_col == "None" else x_col
        with p_col3:
            y_col = st.selectbox("Y-Axis / Metric Column", options=["None"] + num_cols)
            y_col = None if y_col == "None" else y_col
        with p_col4:
            color_col = st.selectbox("Color / Cohort Grouping", options=["None"] + all_cols)
            color_col = None if color_col == "None" else color_col

        t_col1, t_col2, t_col3 = st.columns(3)
        with t_col1:
            theme_choice = st.selectbox("Color Theme", list(THEME_PALETTES.keys()))
        with t_col2:
            custom_title = st.text_input("Chart Title", value=f"{chart_type} Analysis")
        with t_col3:
            agg_choice = st.selectbox("Aggregation Method (for Bar/Pie)", ["sum", "mean", "median"])

    # Render custom chart
    custom_fig = create_chart(
        df=df,
        chart_type=chart_type,
        x_col=x_col,
        y_col=y_col,
        color_col=color_col,
        title=custom_title,
        theme=theme_choice,
        agg_func=agg_choice
    )
    st.plotly_chart(custom_fig, use_container_width=True)

    # 5. STATISTICAL SUMMARIES TAB
    st.markdown("#### 📋 Detailed Feature Profiles")
    summary_tabs = st.tabs(["Numerical Features Summary", "Categorical Features Summary"])
    with summary_tabs[0]:
        num_summary = compute_numerical_summary(df)
        if not num_summary.empty:
            st.dataframe(num_summary, use_container_width=True)
        else:
            st.info("No numerical features available.")
    with summary_tabs[1]:
        cat_summary = compute_categorical_summary(df)
        if not cat_summary.empty:
            st.dataframe(cat_summary, use_container_width=True)
        else:
            st.info("No categorical features available.")

if __name__ == "__main__":
    init_session_state()
    render_stage_3()
