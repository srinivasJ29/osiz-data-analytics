import io
import pandas as pd
from typing import Tuple, Dict, Any, Optional

MAX_FILE_SIZE_BYTES = 50 * 1024 * 1024  # 50 MB safety threshold

def load_dataset(file_obj_or_path, filename: str) -> Tuple[Optional[pd.DataFrame], Optional[str]]:
    """
    Load dataset from CSV or Excel file safely.
    Returns (DataFrame, error_message).
    """
    try:
        lower_name = filename.lower()
        if not (lower_name.endswith('.csv') or lower_name.endswith('.xlsx') or lower_name.endswith('.xls')):
            return None, f"Unsupported file extension for '{filename}'. Only .csv, .xlsx, and .xls are supported."

        if hasattr(file_obj_or_path, 'size') and file_obj_or_path.size > MAX_FILE_SIZE_BYTES:
            return None, f"File size exceeds safety limit of {MAX_FILE_SIZE_BYTES // (1024*1024)} MB."

        if lower_name.endswith('.csv'):
            # Try utf-8 first, fallback to latin-1
            try:
                df = pd.read_csv(file_obj_or_path, encoding='utf-8')
            except UnicodeDecodeError:
                if hasattr(file_obj_or_path, 'seek'):
                    file_obj_or_path.seek(0)
                df = pd.read_csv(file_obj_or_path, encoding='latin-1')
        else:
            df = pd.read_excel(file_obj_or_path)

        if df.empty:
            return None, "The uploaded dataset is empty (contains 0 records)."

        # Ensure column names are strings and handle unnamed/duplicates cleanly
        df.columns = [str(c).strip() if str(c).strip() else f"Unnamed_{i}" for i, c in enumerate(df.columns)]
        
        return df, None
    except Exception as e:
        return None, f"Failed to parse file: {str(e)}"

def get_dataset_metadata(df: pd.DataFrame, filename: str, file_size: int = 0) -> Dict[str, Any]:
    """
    Extract comprehensive metadata, column profiles, missing counts, and duplicate counts.
    """
    total_rows = len(df)
    total_cols = len(df.columns)
    duplicate_rows = int(df.duplicated().sum())

    col_profiles = []
    for col in df.columns:
        s = df[col]
        missing_count = int(s.isna().sum())
        missing_pct = round((missing_count / total_rows * 100), 2) if total_rows > 0 else 0
        unique_count = int(s.nunique(dropna=True))
        inferred_dtype = str(s.dtype)
        
        # Determine broad data type category
        if pd.api.types.is_numeric_dtype(s):
            kind = "Numerical"
        elif pd.api.types.is_datetime64_any_dtype(s):
            kind = "Datetime"
        elif pd.api.types.is_bool_dtype(s):
            kind = "Boolean"
        else:
            kind = "Categorical"

        col_profiles.append({
            "Column": col,
            "Type": kind,
            "Raw Dtype": inferred_dtype,
            "Missing Count": missing_count,
            "Missing %": missing_pct,
            "Unique Values": unique_count
        })

    num_cols = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]
    cat_cols = [c for c in df.columns if not pd.api.types.is_numeric_dtype(df[c])]

    return {
        "filename": filename,
        "file_size": file_size,
        "total_rows": total_rows,
        "total_cols": total_cols,
        "duplicate_rows": duplicate_rows,
        "column_profiles": pd.DataFrame(col_profiles),
        "numerical_columns": num_cols,
        "categorical_columns": cat_cols
    }
