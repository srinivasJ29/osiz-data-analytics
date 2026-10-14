import pandas as pd
from typing import Dict, Any, List

def apply_filters(df: pd.DataFrame, filter_specs: Dict[str, Any]) -> pd.DataFrame:
    """
    Applies multi-dimensional filtering criteria across dataframe.
    filter_specs structure:
    {
        "search_query": "text to find anywhere",
        "numeric_ranges": { "col_name": (min_val, max_val) },
        "categorical_values": { "col_name": [selected_val_1, selected_val_2] },
        "date_ranges": { "col_name": (start_date, end_date) },
        "missing_filter": { "col_name": "all" | "missing_only" | "non_missing_only" }
    }
    """
    if df is None or df.empty:
        return df

    filtered = df.copy()

    # 1. Global text search
    search_query = filter_specs.get("search_query", "").strip()
    if search_query:
        # Search across all columns converted to string
        match_mask = pd.Series(False, index=filtered.index)
        for col in filtered.columns:
            col_str = filtered[col].astype(str).str.lower()
            match_mask = match_mask | col_str.str.contains(search_query.lower(), na=False, regex=False)
        filtered = filtered[match_mask]

    # 2. Numeric range filters
    numeric_ranges = filter_specs.get("numeric_ranges", {})
    for col, (min_val, max_val) in numeric_ranges.items():
        if col in filtered.columns and pd.api.types.is_numeric_dtype(filtered[col]):
            if min_val is not None:
                filtered = filtered[filtered[col] >= min_val]
            if max_val is not None:
                filtered = filtered[filtered[col] <= max_val]

    # 3. Categorical multiselect filters
    cat_filters = filter_specs.get("categorical_values", {})
    for col, selected_vals in cat_filters.items():
        if col in filtered.columns and selected_vals:
            # Match stringified values or null if specified
            filtered = filtered[filtered[col].isin(selected_vals)]

    # 4. Date range filters
    date_ranges = filter_specs.get("date_ranges", {})
    for col, (start_dt, end_dt) in date_ranges.items():
        if col in filtered.columns:
            date_col = pd.to_datetime(filtered[col], errors='coerce')
            if start_dt is not None:
                filtered = filtered[date_col >= pd.to_datetime(start_dt)]
            if end_dt is not None:
                filtered = filtered[date_col <= pd.to_datetime(end_dt)]

    # 5. Missing value filters
    missing_filters = filter_specs.get("missing_filter", {})
    for col, mode in missing_filters.items():
        if col in filtered.columns:
            if mode == "missing_only":
                filtered = filtered[filtered[col].isna()]
            elif mode == "non_missing_only":
                filtered = filtered[filtered[col].notna()]

    return filtered
