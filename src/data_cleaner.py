import pandas as pd
import numpy as np
from typing import Tuple, List, Dict, Any, Optional

def remove_duplicates(df: pd.DataFrame, subset: Optional[List[str]] = None) -> Tuple[pd.DataFrame, int]:
    """Removes duplicate rows and returns (cleaned_df, count_removed)."""
    initial_count = len(df)
    cleaned = df.drop_duplicates(subset=subset, keep='first').copy()
    removed = initial_count - len(cleaned)
    return cleaned, removed

def drop_missing_values(df: pd.DataFrame, how: str = 'any', axis: int = 0, subset: Optional[List[str]] = None) -> Tuple[pd.DataFrame, int]:
    """Drops rows (axis=0) or columns (axis=1) with missing values."""
    if axis == 0:
        initial = len(df)
        cleaned = df.dropna(how=how, subset=subset).copy()
        affected = initial - len(cleaned)
        return cleaned, affected
    else:
        initial = len(df.columns)
        cleaned = df.dropna(axis=1, how=how).copy()
        affected = initial - len(cleaned.columns)
        return cleaned, affected

def fill_missing_values(df: pd.DataFrame, column: str, strategy: str, custom_value: Any = None) -> Tuple[pd.DataFrame, int]:
    """Fills missing values in a column using mean, median, mode, constant, or forward/backward fill."""
    cleaned = df.copy()
    if column not in cleaned.columns:
        return cleaned, 0

    s = cleaned[column]
    missing_count = int(s.isna().sum())
    if missing_count == 0:
        return cleaned, 0

    if strategy == 'mean':
        if pd.api.types.is_numeric_dtype(s):
            val = s.mean()
            cleaned[column] = s.fillna(val)
        else:
            raise ValueError(f"Cannot calculate mean on non-numeric column '{column}'.")
    elif strategy == 'median':
        if pd.api.types.is_numeric_dtype(s):
            val = s.median()
            cleaned[column] = s.fillna(val)
        else:
            raise ValueError(f"Cannot calculate median on non-numeric column '{column}'.")
    elif strategy == 'mode':
        mode_vals = s.mode()
        val = mode_vals.iloc[0] if not mode_vals.empty else ""
        cleaned[column] = s.fillna(val)
    elif strategy == 'custom':
        cleaned[column] = s.fillna(custom_value)
    elif strategy == 'ffill':
        cleaned[column] = s.ffill()
    elif strategy == 'bfill':
        cleaned[column] = s.bfill()
    else:
        raise ValueError(f"Unknown fill strategy '{strategy}'")

    return cleaned, missing_count

def trim_and_case_text(df: pd.DataFrame, columns: List[str], trim_spaces: bool = True, case_transform: Optional[str] = None) -> Tuple[pd.DataFrame, int]:
    """Trims whitespace and adjusts casing (lower, upper, title) on selected string columns."""
    cleaned = df.copy()
    affected_rows = 0
    for col in columns:
        if col in cleaned.columns and (cleaned[col].dtype == 'object' or pd.api.types.is_string_dtype(cleaned[col])):
            s = cleaned[col].astype(str)
            initial_s = s.copy()
            if trim_spaces:
                s = s.str.strip()
            if case_transform == 'lower':
                s = s.str.lower()
            elif case_transform == 'upper':
                s = s.str.upper()
            elif case_transform == 'title':
                s = s.str.title()
            
            # Count where values actually changed
            changed = (s != initial_s).sum()
            affected_rows += int(changed)
            cleaned[col] = s
    return cleaned, affected_rows

def detect_outliers_iqr(df: pd.DataFrame, column: str, multiplier: float = 1.5) -> Tuple[pd.Series, float, float]:
    """Detects outliers using IQR. Returns (boolean_mask_series, lower_bound, upper_bound)."""
    s = df[column].dropna()
    if not pd.api.types.is_numeric_dtype(s) or len(s) == 0:
        return pd.Series(False, index=df.index), 0.0, 0.0
    
    q25 = float(s.quantile(0.25))
    q75 = float(s.quantile(0.75))
    iqr = q75 - q25
    lower_bound = q25 - (multiplier * iqr)
    upper_bound = q75 + (multiplier * iqr)
    
    mask = (df[column] < lower_bound) | (df[column] > upper_bound)
    return mask, lower_bound, upper_bound

def handle_outliers(df: pd.DataFrame, column: str, action: str = 'cap', multiplier: float = 1.5) -> Tuple[pd.DataFrame, int]:
    """
    Handles outliers in numerical column.
    action: 'remove' or 'cap' (winsorize)
    """
    cleaned = df.copy()
    mask, lower_bound, upper_bound = detect_outliers_iqr(cleaned, column, multiplier)
    outlier_count = int(mask.sum())
    if outlier_count == 0:
        return cleaned, 0

    if action == 'remove':
        cleaned = cleaned[~mask].copy()
    elif action == 'cap':
        cleaned[column] = cleaned[column].clip(lower=lower_bound, upper=upper_bound)
    else:
        raise ValueError(f"Unknown outlier action: {action}")

    return cleaned, outlier_count

def cast_column_type(df: pd.DataFrame, column: str, target_type: str) -> Tuple[pd.DataFrame, bool, str]:
    """
    Safely converts column type to integer, float, string, or datetime.
    Returns (cleaned_df, success, message).
    """
    cleaned = df.copy()
    if column not in cleaned.columns:
        return cleaned, False, f"Column '{column}' does not exist."

    try:
        if target_type == 'integer':
            cleaned[column] = pd.to_numeric(cleaned[column], errors='coerce').astype('Int64')
        elif target_type == 'float':
            cleaned[column] = pd.to_numeric(cleaned[column], errors='coerce').astype(float)
        elif target_type == 'string':
            cleaned[column] = cleaned[column].astype(str)
        elif target_type == 'datetime':
            cleaned[column] = pd.to_datetime(cleaned[column], errors='coerce')
        elif target_type == 'boolean':
            cleaned[column] = cleaned[column].astype(bool)
        else:
            return cleaned, False, f"Unsupported target type '{target_type}'."
        return cleaned, True, f"Successfully converted '{column}' to {target_type}."
    except Exception as e:
        return cleaned, False, f"Conversion failed: {str(e)}"
