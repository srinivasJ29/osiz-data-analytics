import pandas as pd
import numpy as np
from typing import Dict, Any, List

def compute_dataset_kpis(df: pd.DataFrame, original_df: pd.DataFrame = None) -> Dict[str, Any]:
    """Computes high-level KPI cards data."""
    if df is None or df.empty:
        return {
            "total_rows": 0,
            "total_cols": 0,
            "num_numerical": 0,
            "num_categorical": 0,
            "missing_cells": 0,
            "duplicate_rows": 0,
            "retention_pct": 0.0
        }

    total_rows = len(df)
    total_cols = len(df.columns)
    num_cols = sum(1 for c in df.columns if pd.api.types.is_numeric_dtype(df[c]))
    cat_cols = total_cols - num_cols
    missing_cells = int(df.isna().sum().sum())
    duplicate_rows = int(df.duplicated().sum())

    orig_rows = len(original_df) if original_df is not None and not original_df.empty else total_rows
    retention_pct = round((total_rows / orig_rows * 100), 1) if orig_rows > 0 else 100.0

    return {
        "total_rows": total_rows,
        "total_cols": total_cols,
        "num_numerical": num_cols,
        "num_categorical": cat_cols,
        "missing_cells": missing_cells,
        "duplicate_rows": duplicate_rows,
        "retention_pct": retention_pct
    }

def compute_numerical_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Computes detailed statistical summary for numerical columns."""
    num_cols = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]
    if not num_cols:
        return pd.DataFrame()

    stats = []
    for col in num_cols:
        s = df[col].dropna()
        if len(s) == 0:
            continue
        stats.append({
            "Column": col,
            "Count": int(s.count()),
            "Mean": round(float(s.mean()), 2),
            "Std Dev": round(float(s.std()), 2) if len(s) > 1 else 0.0,
            "Min": round(float(s.min()), 2),
            "25% (Q1)": round(float(s.quantile(0.25)), 2),
            "Median (50%)": round(float(s.median()), 2),
            "75% (Q3)": round(float(s.quantile(0.75)), 2),
            "Max": round(float(s.max()), 2),
            "Skewness": round(float(s.skew()), 2) if len(s) > 2 else 0.0
        })
    return pd.DataFrame(stats)

def compute_categorical_summary(df: pd.DataFrame, max_cardinality: int = 100) -> pd.DataFrame:
    """Computes summary statistics for categorical columns."""
    cat_cols = [c for c in df.columns if not pd.api.types.is_numeric_dtype(df[c])]
    if not cat_cols:
        return pd.DataFrame()

    stats = []
    for col in cat_cols:
        s = df[col].dropna()
        unique_cnt = int(s.nunique())
        top_val = str(s.mode().iloc[0]) if not s.empty else "N/A"
        top_freq = int(s.value_counts().iloc[0]) if not s.empty else 0
        freq_pct = round((top_freq / len(df) * 100), 1) if len(df) > 0 else 0.0
        stats.append({
            "Column": col,
            "Unique Count": unique_cnt,
            "Top Category": top_val,
            "Top Frequency": top_freq,
            "Top Category %": freq_pct
        })
    return pd.DataFrame(stats)

def generate_automated_insights(df: pd.DataFrame) -> List[Dict[str, str]]:
    """
    Analyzes patterns and generates factual, data-driven analytical insights.
    """
    insights = []
    if df is None or df.empty:
        return [{"type": "info", "title": "No Data", "text": "Dataset is empty. Upload or filter data to view insights."}]

    total_rows = len(df)
    
    # 1. Missing data insight
    null_counts = df.isna().sum()
    cols_with_nulls = null_counts[null_counts > 0]
    if not cols_with_nulls.empty:
        worst_null_col = cols_with_nulls.idxmax()
        worst_null_count = cols_with_nulls.max()
        pct = round(worst_null_count / total_rows * 100, 1)
        insights.append({
            "type": "warning",
            "title": "Data Completeness Evaluation",
            "text": f"Incomplete data records identified across {len(cols_with_nulls)} attribute(s). The highest proportion of missing values resides in '{worst_null_col}', comprising {worst_null_count:,} records ({pct}% of total sample)."
        })
    else:
        insights.append({
            "type": "success",
            "title": "Data Completeness Evaluation",
            "text": "Full integrity verified across all examined attributes with zero null or omitted records."
        })


    # 2. Duplicate rows insight
    dups = int(df.duplicated().sum())
    if dups > 0:
        insights.append({
            "type": "warning",
            "title": "Duplicate Rows",
            "text": f"Identified {dups} duplicate record(s) ({round(dups / total_rows * 100, 1)}% of total rows)."
        })

    # 3. Correlation insights
    num_cols = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]
    if len(num_cols) >= 2:
        corr_matrix = df[num_cols].corr()
        # Find highest positive & negative non-diagonal correlations
        pairs = []
        for i in range(len(num_cols)):
            for j in range(i + 1, len(num_cols)):
                c1, c2 = num_cols[i], num_cols[j]
                val = corr_matrix.loc[c1, c2]
                if not np.isnan(val):
                    pairs.append((c1, c2, float(val)))
        
        if pairs:
            # Sort by absolute correlation
            pairs.sort(key=lambda x: abs(x[2]), reverse=True)
            top_pair = pairs[0]
            strength = "strong" if abs(top_pair[2]) >= 0.7 else ("moderate" if abs(top_pair[2]) >= 0.4 else "weak")
            direction = "positive" if top_pair[2] > 0 else "inverse"
            insights.append({
                "type": "info",
                "title": "Prominent Correlation",
                "text": f"Strongest relationship observed between '{top_pair[0]}' and '{top_pair[1]}' (Pearson r = {round(top_pair[2], 2)}), representing a {strength} {direction} correlation."
            })

    # 4. Outliers & Skewness
    for col in num_cols[:3]: # Top numerical cols
        s = df[col].dropna()
        if len(s) > 10:
            skew = s.skew()
            if abs(skew) > 1.5:
                direction = "right (positively)" if skew > 0 else "left (negatively)"
                insights.append({
                    "type": "info",
                    "title": f"Distribution Asymmetry: {col}",
                    "text": f"'{col}' is highly skewed to the {direction} (skewness = {round(skew, 2)}). Median ({round(s.median(), 2)}) may be more representative than Mean ({round(s.mean(), 2)})."
                })

    # 5. Dominant category in categorical columns
    cat_cols = [c for c in df.columns if not pd.api.types.is_numeric_dtype(df[c])]
    for col in cat_cols[:2]:
        s = df[col].dropna()
        if len(s) > 0:
            val_counts = s.value_counts()
            top_item = val_counts.index[0]
            top_share = (val_counts.iloc[0] / len(s)) * 100
            if top_share > 50:
                insights.append({
                    "type": "info",
                    "title": f"Dominant Category: {col}",
                    "text": f"In '{col}', '{top_item}' accounts for {round(top_share, 1)}% of all non-empty entries ({val_counts.iloc[0]} occurrences)."
                })

    return insights
