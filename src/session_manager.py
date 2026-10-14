import streamlit as st
import pandas as pd
from typing import Dict, Any, List, Optional
from datetime import datetime

SESSION_DEFAULTS = {
    "original_df": None,
    "working_df": None,
    "filtered_df": None,
    "metadata": None,
    "audit_history": [],
    "undo_stack": [],
    "filter_specs": {
        "search_query": "",
        "numeric_ranges": {},
        "categorical_values": {},
        "date_ranges": {},
        "missing_filter": {}
    },
    "current_stage": 1,
}

def init_session_state():
    """Initializes Streamlit session state keys with secure defaults."""
    for key, val in SESSION_DEFAULTS.items():
        if key not in st.session_state:
            st.session_state[key] = val

def set_stage(stage_num: int):
    """Sets the active application workflow stage."""
    st.session_state["current_stage"] = stage_num

def record_change(action: str, affected_count: int, previous_df: pd.DataFrame):
    """
    Saves an undo checkpoint and updates the audit log.
    Limits undo history to 10 entries to preserve memory.
    """
    if "undo_stack" not in st.session_state:
        st.session_state["undo_stack"] = []
    if "audit_history" not in st.session_state:
        st.session_state["audit_history"] = []

    # Push clone to undo stack
    st.session_state["undo_stack"].append(previous_df.copy())
    if len(st.session_state["undo_stack"]) > 10:
        st.session_state["undo_stack"].pop(0)

    # Record audit log
    entry = {
        "action": action,
        "affected": affected_count,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    st.session_state["audit_history"].append(entry)

def undo_last_change() -> bool:
    """Restores the most recent working dataset state."""
    if st.session_state.get("undo_stack"):
        prev = st.session_state["undo_stack"].pop()
        st.session_state["working_df"] = prev
        # Also re-sync filtered_df
        from src.data_filter import apply_filters
        st.session_state["filtered_df"] = apply_filters(prev, st.session_state.get("filter_specs", {}))
        
        # Log undo
        st.session_state["audit_history"].append({
            "action": "Undo Operation",
            "affected": 1,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        return True
    return False

def reset_to_original() -> bool:
    """Reverts all cleaning and editing modifications back to original upload."""
    if st.session_state.get("original_df") is not None:
        orig = st.session_state["original_df"].copy()
        record_change("Reset to Original Dataset", len(orig), st.session_state["working_df"])
        st.session_state["working_df"] = orig
        from src.data_filter import apply_filters
        st.session_state["filtered_df"] = apply_filters(orig, st.session_state.get("filter_specs", {}))
        return True
    return False

def clear_all_filters():
    """Resets all active filter specifications to empty."""
    st.session_state["filter_specs"] = {
        "search_query": "",
        "numeric_ranges": {},
        "categorical_values": {},
        "date_ranges": {},
        "missing_filter": {}
    }
    if st.session_state.get("working_df") is not None:
        st.session_state["filtered_df"] = st.session_state["working_df"].copy()
