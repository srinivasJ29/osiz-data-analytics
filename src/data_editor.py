import pandas as pd
from typing import Tuple, List, Dict, Any, Optional

def rename_column(df: pd.DataFrame, old_name: str, new_name: str) -> Tuple[pd.DataFrame, bool, str]:
    """Renames a column safely."""
    new_name = new_name.strip()
    if not new_name:
        return df, False, "New column name cannot be empty."
    if old_name not in df.columns:
        return df, False, f"Column '{old_name}' not found."
    if new_name in df.columns and new_name != old_name:
        return df, False, f"A column named '{new_name}' already exists."

    cleaned = df.rename(columns={old_name: new_name}).copy()
    return cleaned, True, f"Renamed column '{old_name}' to '{new_name}'."

def drop_columns(df: pd.DataFrame, columns_to_drop: List[str]) -> Tuple[pd.DataFrame, int]:
    """Drops specified columns."""
    valid_cols = [c for c in columns_to_drop if c in df.columns]
    if not valid_cols:
        return df, 0
    cleaned = df.drop(columns=valid_cols).copy()
    return cleaned, len(valid_cols)

def select_columns(df: pd.DataFrame, columns_to_keep: List[str]) -> pd.DataFrame:
    """Subsets dataframe by keeping only specified columns."""
    valid_cols = [c for c in columns_to_keep if c in df.columns]
    if not valid_cols:
        return df
    return df[valid_cols].copy()

def delete_rows_by_indices(df: pd.DataFrame, indices: List[Any]) -> Tuple[pd.DataFrame, int]:
    """Deletes rows by index."""
    valid_idx = [idx for idx in indices if idx in df.index]
    if not valid_idx:
        return df, 0
    cleaned = df.drop(index=valid_idx).copy()
    return cleaned, len(valid_idx)

def add_new_row(df: pd.DataFrame, row_dict: Dict[str, Any]) -> Tuple[pd.DataFrame, bool, str]:
    """Appends a new row to the dataframe with type checking."""
    try:
        # Create single row dataframe with matching columns
        new_row = {}
        for col in df.columns:
            val = row_dict.get(col, None)
            new_row[col] = val

        new_row_df = pd.DataFrame([new_row])
        # Realign types where possible
        for col in df.columns:
            if pd.api.types.is_numeric_dtype(df[col]):
                new_row_df[col] = pd.to_numeric(new_row_df[col], errors='coerce')
        
        updated_df = pd.concat([df, new_row_df], ignore_index=True)
        return updated_df, True, "Successfully added new row."
    except Exception as e:
        return df, False, f"Failed to add row: {str(e)}"
