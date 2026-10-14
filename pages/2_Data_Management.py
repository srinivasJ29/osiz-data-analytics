import streamlit as st
import pandas as pd
from src.session_manager import init_session_state, set_stage, record_change, undo_last_change, reset_to_original, clear_all_filters
from src.data_cleaner import (
    remove_duplicates, drop_missing_values, fill_missing_values, 
    trim_and_case_text, detect_outliers_iqr, handle_outliers, cast_column_type
)
from src.data_filter import apply_filters
from src.data_editor import rename_column, drop_columns, delete_rows_by_indices, add_new_row
from src.report_generator import export_to_csv, export_to_excel

def render_stage_2():
    st.subheader("🛠️ Stage 2: Data Management, Cleaning & Interactive Filtering")
    st.caption("Perform verified cleaning transformations, apply multi-criteria filters without altering the baseline, and manually edit records or schemas with complete undo capabilities.")
    st.write("")


    if st.session_state.get("working_df") is None:
        st.warning("⚠️ No dataset uploaded yet. Please proceed to Stage 1 to upload your file.")
        if st.button("⬅️ Go to Stage 1"):
            set_stage(1)
            st.rerun()
        return

    working_df = st.session_state["working_df"]
    filtered_df = st.session_state.get("filtered_df", working_df)

    # Top Control Bar (Stats, Undo, Reset, Navigate)
    top_col1, top_col2, top_col3, top_col4 = st.columns([2, 1, 1, 1])
    with top_col1:
        st.markdown(f"**Working Records:** `{len(working_df):,}` | **Active Filtered View:** `{len(filtered_df):,}`")
    with top_col2:
        can_undo = len(st.session_state.get("undo_stack", [])) > 0
        if st.button("↩️ Undo", disabled=not can_undo, use_container_width=True, help="Revert the last data cleaning/editing operation"):
            if undo_last_change():
                st.success("Undo successful!")
                st.rerun()
    with top_col3:
        if st.button("🔄 Reset All", use_container_width=True, help="Reset dataset to original upload"):
            if reset_to_original():
                st.success("Reset to original upload!")
                st.rerun()
    with top_col4:
        if st.button("Proceed to Stage 3 ➡️", type="primary", use_container_width=True):
            set_stage(3)
            st.rerun()

    tabs = st.tabs(["🧹 Data Cleaning", "🔍 Multi-Criteria Filtering", "✏️ Record & Schema Editing", "📜 Audit History & Export"])

    # ---------------- TAB 1: DATA CLEANING ----------------
    with tabs[0]:
        st.markdown("#### Automated & Controlled Data Cleaning")
        clean_expander1, clean_expander2, clean_expander3, clean_expander4 = st.columns(4)

        # 1. Duplicates
        with st.expander("👯 Duplicate Rows", expanded=False):
            dup_count = int(working_df.duplicated().sum())
            st.write(f"Current duplicates: **{dup_count}**")
            if dup_count > 0:
                if st.button("Remove Duplicates", key="btn_remove_dups", type="primary"):
                    new_df, removed = remove_duplicates(working_df)
                    record_change(f"Removed {removed} duplicate rows", removed, working_df)
                    st.session_state["working_df"] = new_df
                    st.session_state["filtered_df"] = apply_filters(new_df, st.session_state.get("filter_specs", {}))
                    st.success(f"Removed {removed} duplicate records!")
                    st.rerun()
            else:
                st.info("No duplicates detected.")

        # 2. Missing Values
        with st.expander("🩹 Missing Values", expanded=False):
            st.markdown("**Handling Missing Values**")
            missing_action = st.selectbox("Action", ["Drop Rows with Nulls", "Drop Columns with Nulls", "Impute / Fill Column Nulls"])
            
            if missing_action == "Drop Rows with Nulls":
                subset_cols = st.multiselect("Across specific columns (leave blank for all)", options=list(working_df.columns))
                if st.button("Confirm Drop Rows", type="primary"):
                    new_df, removed = drop_missing_values(working_df, axis=0, subset=subset_cols if subset_cols else None)
                    record_change(f"Dropped rows with missing values (affected: {removed})", removed, working_df)
                    st.session_state["working_df"] = new_df
                    st.session_state["filtered_df"] = apply_filters(new_df, st.session_state.get("filter_specs", {}))
                    st.success(f"Removed {removed} rows with missing values!")
                    st.rerun()

            elif missing_action == "Drop Columns with Nulls":
                if st.button("Confirm Drop Columns", type="primary"):
                    new_df, removed = drop_missing_values(working_df, axis=1)
                    record_change(f"Dropped columns with missing values (affected: {removed})", removed, working_df)
                    st.session_state["working_df"] = new_df
                    st.session_state["filtered_df"] = apply_filters(new_df, st.session_state.get("filter_specs", {}))
                    st.success(f"Removed {removed} columns with missing values!")
                    st.rerun()

            elif missing_action == "Impute / Fill Column Nulls":
                col_to_fill = st.selectbox("Select Column to Fill", options=list(working_df.columns))
                is_num = pd.api.types.is_numeric_dtype(working_df[col_to_fill])
                strategies = ["mean", "median", "mode", "custom", "ffill", "bfill"] if is_num else ["mode", "custom", "ffill", "bfill"]
                strategy = st.selectbox("Imputation Strategy", strategies)
                custom_val = None
                if strategy == "custom":
                    custom_val = st.text_input("Custom Fill Value", value="0" if is_num else "Unknown")
                    if is_num:
                        try:
                            custom_val = float(custom_val)
                        except ValueError:
                            st.error("Please enter a valid numeric value.")
                
                if st.button("Apply Imputation", type="primary"):
                    try:
                        new_df, count = fill_missing_values(working_df, col_to_fill, strategy, custom_val)
                        record_change(f"Imputed missing values in '{col_to_fill}' using {strategy}", count, working_df)
                        st.session_state["working_df"] = new_df
                        st.session_state["filtered_df"] = apply_filters(new_df, st.session_state.get("filter_specs", {}))
                        st.success(f"Successfully imputed {count} values in '{col_to_fill}'!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Imputation error: {str(e)}")

        # 3. Text Formatting
        with st.expander("🔤 Text Cleaning", expanded=False):
            str_cols = [c for c in working_df.columns if working_df[c].dtype == 'object' or pd.api.types.is_string_dtype(working_df[c])]
            if str_cols:
                sel_str_cols = st.multiselect("Select String Columns", options=str_cols, default=str_cols[:3])
                trim_spaces = st.checkbox("Trim leading & trailing whitespace", value=True)
                case_opt = st.selectbox("Text Case Transformation", ["None", "lower", "upper", "title"])
                if st.button("Apply Text Formatting", type="primary"):
                    new_df, affected = trim_and_case_text(working_df, sel_str_cols, trim_spaces, None if case_opt == "None" else case_opt)
                    record_change(f"Cleaned text in columns: {sel_str_cols}", affected, working_df)
                    st.session_state["working_df"] = new_df
                    st.session_state["filtered_df"] = apply_filters(new_df, st.session_state.get("filter_specs", {}))
                    st.success(f"Updated text columns! ({affected} values modified)")
                    st.rerun()
            else:
                st.info("No string/text columns detected.")

        # 4. Outlier Handling
        with st.expander("🎯 Outliers (IQR)", expanded=False):
            num_cols = [c for c in working_df.columns if pd.api.types.is_numeric_dtype(working_df[c])]
            if num_cols:
                outlier_col = st.selectbox("Select Numerical Column", options=num_cols)
                iqr_mult = st.slider("IQR Multiplier", 1.0, 3.0, 1.5, 0.1)
                mask, low_b, up_b = detect_outliers_iqr(working_df, outlier_col, iqr_mult)
                outlier_cnt = int(mask.sum())
                st.write(f"Detected **{outlier_cnt}** outlier(s) (Bounds: `{round(low_b, 2)}` to `{round(up_b, 2)}`)")
                
                if outlier_cnt > 0:
                    outlier_action = st.radio("Action", ["cap", "remove"], format_func=lambda x: "Winsorize / Cap to bounds" if x == "cap" else "Remove outlier records")
                    if st.button("Handle Outliers", type="primary"):
                        new_df, affected = handle_outliers(working_df, outlier_col, outlier_action, iqr_mult)
                        record_change(f"Handled outliers in '{outlier_col}' ({outlier_action})", affected, working_df)
                        st.session_state["working_df"] = new_df
                        st.session_state["filtered_df"] = apply_filters(new_df, st.session_state.get("filter_specs", {}))
                        st.success(f"Successfully processed {affected} outliers in '{outlier_col}'!")
                        st.rerun()
            else:
                st.info("No numerical columns for outlier analysis.")

        st.markdown("#### Cleaned Dataset Preview")
        st.dataframe(working_df.head(50), use_container_width=True, height=260)

    # ---------------- TAB 2: INTERACTIVE FILTERING ----------------
    with tabs[1]:
        st.markdown("#### Dynamic Multi-Criteria Filtering Workspace")
        st.caption("Filters narrow down the working view without permanently removing records from the cleaned dataset.")

        filter_specs = st.session_state.get("filter_specs", {})

        col_search, col_reset = st.columns([4, 1])
        with col_search:
            global_search = st.text_input("🔍 Global Text Search (matches any column)", value=filter_specs.get("search_query", ""))
            filter_specs["search_query"] = global_search
        with col_reset:
            st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
            if st.button("🔄 Clear All Filters", use_container_width=True):
                clear_all_filters()
                st.rerun()

        st.markdown("---")
        filter_col1, filter_col2, filter_col3 = st.columns(3)

        # Numerical range filters
        with filter_col1:
            st.markdown("**🔢 Numerical Range Filters**")
            num_cols = [c for c in working_df.columns if pd.api.types.is_numeric_dtype(working_df[c])]
            if num_cols:
                sel_num_col = st.selectbox("Filter Numerical Column", options=["None"] + num_cols)
                if sel_num_col != "None":
                    min_val = float(working_df[sel_num_col].min()) if not working_df[sel_num_col].isna().all() else 0.0
                    max_val = float(working_df[sel_num_col].max()) if not working_df[sel_num_col].isna().all() else 100.0
                    if min_val < max_val:
                        user_range = st.slider(f"Range for {sel_num_col}", min_value=min_val, max_value=max_val, value=(min_val, max_val))
                        filter_specs["numeric_ranges"][sel_num_col] = user_range
                    else:
                        st.info(f"Column '{sel_num_col}' has a single constant value ({min_val}).")
            else:
                st.info("No numerical columns available.")

        # Categorical multiselect filters
        with filter_col2:
            st.markdown("**🏷️ Categorical Filters**")
            cat_cols = [c for c in working_df.columns if not pd.api.types.is_numeric_dtype(working_df[c]) and working_df[c].nunique() <= 50]
            if cat_cols:
                sel_cat_col = st.selectbox("Filter Categorical Column", options=["None"] + cat_cols)
                if sel_cat_col != "None":
                    options = list(working_df[sel_cat_col].dropna().unique())
                    chosen = st.multiselect(f"Select values in {sel_cat_col}", options=options, default=filter_specs.get("categorical_values", {}).get(sel_cat_col, []))
                    if chosen:
                        filter_specs["categorical_values"][sel_cat_col] = chosen
                    elif sel_cat_col in filter_specs.get("categorical_values", {}):
                        del filter_specs["categorical_values"][sel_cat_col]
            else:
                st.info("No low-cardinality categorical columns.")

        # Missing values filter
        with filter_col3:
            st.markdown("**❓ Missingness Filters**")
            cols_with_na = [c for c in working_df.columns if working_df[c].isna().any()]
            if cols_with_na:
                sel_na_col = st.selectbox("Filter by Missingness", options=["None"] + cols_with_na)
                if sel_na_col != "None":
                    na_mode = st.radio(f"Condition for {sel_na_col}", ["all", "missing_only", "non_missing_only"], format_func=lambda x: "Show All" if x == "all" else ("Only Missing" if x == "missing_only" else "Only Non-Missing"))
                    if na_mode != "all":
                        filter_specs["missing_filter"][sel_na_col] = na_mode
                    elif sel_na_col in filter_specs.get("missing_filter", {}):
                        del filter_specs["missing_filter"][sel_na_col]
            else:
                st.info("Zero missing values in active dataset.")

        # Apply updated filters
        st.session_state["filter_specs"] = filter_specs
        filtered_df = apply_filters(working_df, filter_specs)
        st.session_state["filtered_df"] = filtered_df

        st.markdown(f"#### Filtered Results ({len(filtered_df):,} of {len(working_df):,} records)")
        st.dataframe(filtered_df.head(100), use_container_width=True, height=280)

    # ---------------- TAB 3: RECORD & SCHEMA EDITING ----------------
    with tabs[2]:
        st.markdown("#### Schema Transformation & Row Editing")
        
        edit_col1, edit_col2, edit_col3 = st.columns(3)
        
        # 1. Rename Column
        with edit_col1:
            with st.expander("✏️ Rename Column", expanded=False):
                old_col = st.selectbox("Select Column to Rename", options=list(working_df.columns), key="sel_rename_old")
                new_col_name = st.text_input("New Name", value=old_col, key="txt_rename_new")
                if st.button("Apply Rename", key="btn_apply_rename", type="primary"):
                    new_df, success, msg = rename_column(working_df, old_col, new_col_name)
                    if success:
                        record_change(f"Renamed column '{old_col}' to '{new_col_name}'", 1, working_df)
                        st.session_state["working_df"] = new_df
                        st.session_state["filtered_df"] = apply_filters(new_df, st.session_state.get("filter_specs", {}))
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)

        # 2. Drop Columns
        with edit_col2:
            with st.expander("🗑️ Drop Columns", expanded=False):
                cols_to_drop = st.multiselect("Select Columns to Remove", options=list(working_df.columns), key="sel_drop_cols")
                if cols_to_drop:
                    if st.button("Delete Columns", key="btn_drop_cols", type="primary"):
                        new_df, dropped_cnt = drop_columns(working_df, cols_to_drop)
                        record_change(f"Dropped columns: {cols_to_drop}", dropped_cnt, working_df)
                        st.session_state["working_df"] = new_df
                        st.session_state["filtered_df"] = apply_filters(new_df, st.session_state.get("filter_specs", {}))
                        st.success(f"Removed {dropped_cnt} column(s)!")
                        st.rerun()

        # 3. Change Data Type
        with edit_col3:
            with st.expander("🔄 Cast Column Type", expanded=False):
                col_to_cast = st.selectbox("Select Column to Cast", options=list(working_df.columns), key="sel_cast_col")
                target_type = st.selectbox("Target Type", ["integer", "float", "string", "datetime", "boolean"], key="sel_cast_type")
                if st.button("Apply Type Cast", key="btn_apply_cast", type="primary"):
                    new_df, ok, msg = cast_column_type(working_df, col_to_cast, target_type)
                    if ok:
                        record_change(f"Cast '{col_to_cast}' to {target_type}", len(new_df), working_df)
                        st.session_state["working_df"] = new_df
                        st.session_state["filtered_df"] = apply_filters(new_df, st.session_state.get("filter_specs", {}))
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)

        # Add Row
        with st.expander("➕ Append New Record / Row", expanded=False):
            st.caption("Provide values for each column to append a single record to the working dataset:")
            row_inputs = {}
            row_cols = st.columns(min(len(working_df.columns), 4))
            for i, c in enumerate(working_df.columns):
                with row_cols[i % len(row_cols)]:
                    row_inputs[c] = st.text_input(f"Val: {c}", key=f"add_row_{c}")
            
            if st.button("Add Record", key="btn_add_record", type="primary"):
                new_df, ok, msg = add_new_row(working_df, row_inputs)
                if ok:
                    record_change("Appended 1 new row", 1, working_df)
                    st.session_state["working_df"] = new_df
                    st.session_state["filtered_df"] = apply_filters(new_df, st.session_state.get("filter_specs", {}))
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)

    # ---------------- TAB 4: AUDIT HISTORY & EXPORT ----------------
    with tabs[3]:
        st.markdown("#### 📜 Operations Audit History")
        history = st.session_state.get("audit_history", [])
        if history:
            st.dataframe(pd.DataFrame(history), use_container_width=True)
        else:
            st.info("No operations recorded yet.")

        st.markdown("#### 📥 Cleaned & Filtered Dataset Download")
        dl_col1, dl_col2 = st.columns(2)
        with dl_col1:
            csv_data = export_to_csv(filtered_df)
            st.download_button(
                "📥 Download Cleaned / Filtered CSV",
                data=csv_data,
                file_name="cleaned_filtered_dataset.csv",
                mime="text/csv",
                use_container_width=True
            )
        with dl_col2:
            excel_data = export_to_excel(filtered_df)
            st.download_button(
                "📥 Download Cleaned / Filtered Excel",
                data=excel_data,
                file_name="cleaned_filtered_dataset.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )

if __name__ == "__main__":
    init_session_state()
    render_stage_2()
