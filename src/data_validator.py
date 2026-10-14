import pandas as pd
from typing import Dict, List, Any

def validate_dataframe(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Validates dataframe health, finds potential issues like mixed types,
    all-null columns, constant columns, and duplicate column names.
    """
    issues = []
    warnings = []
    
    if df is None:
        return {"is_valid": False, "errors": ["DataFrame is None"], "warnings": []}

    if df.empty:
        return {"is_valid": False, "errors": ["DataFrame is empty (0 rows)."], "warnings": []}

    if len(df.columns) == 0:
        return {"is_valid": False, "errors": ["DataFrame has no columns."], "warnings": []}

    # Check for duplicate column names
    col_names = list(df.columns)
    if len(col_names) != len(set(col_names)):
        duplicates = [col for col in set(col_names) if col_names.count(col) > 1]
        warnings.append(f"Duplicated column headers detected: {duplicates}. It is recommended to rename them.")

    # Check for all-null columns
    all_null_cols = [c for c in df.columns if df[c].isna().all()]
    if all_null_cols:
        warnings.append(f"Columns with 100% missing values: {all_null_cols}")

    # Check for single-value constant columns
    constant_cols = [c for c in df.columns if df[c].nunique(dropna=True) == 1]
    if constant_cols:
        warnings.append(f"Single-value constant columns (no variance): {constant_cols}")

    # Check for high cardinality text columns
    for c in df.columns:
        if not pd.api.types.is_numeric_dtype(df[c]) and not pd.api.types.is_datetime64_any_dtype(df[c]):
            unique_ratio = df[c].nunique(dropna=True) / max(len(df), 1)
            if unique_ratio > 0.9 and len(df) > 50:
                warnings.append(f"Column '{c}' appears to be a unique ID or high-cardinality text (unique ratio: {round(unique_ratio*100, 1)}%).")

    return {
        "is_valid": len(issues) == 0,
        "errors": issues,
        "warnings": warnings
    }
