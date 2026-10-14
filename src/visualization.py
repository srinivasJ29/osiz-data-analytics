import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, Any, List, Optional

# Premium color templates
THEME_PALETTES = {
    "Deep Navy & Blue": ["#1e3a8a", "#3b82f6", "#60a5fa", "#93c5fd", "#cbd5e1"],
    "Emerald Teal": ["#064e3b", "#059669", "#10b981", "#6ee7b7", "#a7f3d0"],
    "Sunset Warmth": ["#991b1b", "#ea580c", "#f59e0b", "#fbbf24", "#fde68a"],
    "Modern Slate": ["#0f172a", "#334155", "#64748b", "#94a3b8", "#cbd5e1"]
}

def recommend_charts(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    Analyzes schema and suggests appropriate chart configurations.
    """
    if df is None or df.empty:
        return []

    recommendations = []
    num_cols = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]
    cat_cols = [c for c in df.columns if not pd.api.types.is_numeric_dtype(df[c]) and not pd.api.types.is_datetime64_any_dtype(df[c])]
    date_cols = [c for c in df.columns if pd.api.types.is_datetime64_any_dtype(df[c])]

    # Also detect object columns that look like dates
    for c in cat_cols:
        if "date" in c.lower() or "time" in c.lower() or "year" in c.lower():
            date_cols.append(c)

    # 1. Histogram for first numerical column
    if num_cols:
        recommendations.append({
            "title": f"Distribution Analysis of {num_cols[0]}",
            "type": "Histogram",
            "x": num_cols[0],
            "y": None,
            "color": None,
            "description": "Examine distribution frequency and skewness."
        })

    # 2. Bar chart / Donut chart for first categorical column
    if cat_cols:
        c = cat_cols[0]
        n_unique = df[c].nunique()
        chart_type = "Donut / Pie Chart" if n_unique <= 6 else "Bar Chart"
        recommendations.append({
            "title": f"Category Breakdown: {c}",
            "type": chart_type,
            "x": c,
            "y": None,
            "color": None,
            "description": f"Frequency distribution across {n_unique} unique classes."
        })

    # 3. Two numerical columns -> Scatter plot
    if len(num_cols) >= 2:
        recommendations.append({
            "title": f"Correlation: {num_cols[0]} vs {num_cols[1]}",
            "type": "Scatter Plot",
            "x": num_cols[0],
            "y": num_cols[1],
            "color": cat_cols[0] if cat_cols else None,
            "description": "Explore relationship, clusters, and trend lines between two continuous features."
        })

    # 4. Correlation Heatmap
    if len(num_cols) >= 3:
        recommendations.append({
            "title": "Multivariate Correlation Matrix",
            "type": "Correlation Heatmap",
            "x": None,
            "y": None,
            "color": None,
            "description": "Pearson correlation matrix across all numerical variables."
        })

    # 5. Categorical vs Numerical -> Box plot or Grouped Bar
    if cat_cols and num_cols:
        recommendations.append({
            "title": f"Variance of {num_cols[0]} across {cat_cols[0]}",
            "type": "Box Plot",
            "x": cat_cols[0],
            "y": num_cols[0],
            "color": cat_cols[0],
            "description": "Identify outliers and medians across categorical cohorts."
        })

    # 6. Time-series if date exists
    if date_cols and num_cols:
        recommendations.append({
            "title": f"Temporal Trend: {num_cols[0]} over {date_cols[0]}",
            "type": "Line Chart",
            "x": date_cols[0],
            "y": num_cols[0],
            "color": None,
            "description": "Chronological tracking of quantitative measurements."
        })

    return recommendations

def create_chart(
    df: pd.DataFrame,
    chart_type: str,
    x_col: Optional[str] = None,
    y_col: Optional[str] = None,
    color_col: Optional[str] = None,
    title: Optional[str] = None,
    theme: str = "Deep Navy & Blue",
    agg_func: str = "sum"
) -> go.Figure:
    """
    Renders customizable, publication-quality Plotly figures.
    """
    palette = THEME_PALETTES.get(theme, THEME_PALETTES["Deep Navy & Blue"])
    primary_color = palette[0]
    fig = go.Figure()

    if df is None or df.empty:
        fig.add_annotation(text="No data available for plotting.", showarrow=False, font=dict(size=14, color="#64748b"))
        return fig

    chart_title = title or f"{chart_type}"

    try:
        if chart_type == "Histogram":
            if not x_col or x_col not in df.columns:
                raise ValueError("X-axis column required for Histogram.")
            fig = px.histogram(
                df, x=x_col, color=color_col,
                color_discrete_sequence=palette,
                title=chart_title,
                marginal="box",
                opacity=0.85
            )

        elif chart_type == "Box Plot":
            if not y_col or y_col not in df.columns:
                raise ValueError("Y-axis numerical column required for Box Plot.")
            fig = px.box(
                df, x=x_col, y=y_col, color=color_col,
                color_discrete_sequence=palette,
                title=chart_title,
                points="outliers"
            )

        elif chart_type == "Scatter Plot":
            if not x_col or not y_col:
                raise ValueError("Both X-axis and Y-axis are required for Scatter Plot.")
            fig = px.scatter(
                df, x=x_col, y=y_col, color=color_col,
                color_discrete_sequence=palette,
                title=chart_title,
                trendline="ols" if (len(df) > 5 and color_col is None and pd.api.types.is_numeric_dtype(df[x_col]) and pd.api.types.is_numeric_dtype(df[y_col])) else None
            )

        elif chart_type == "Line Chart":
            if not x_col or not y_col:
                raise ValueError("Both X-axis and Y-axis are required for Line Chart.")
            # If line has duplicates on X, group by
            sorted_df = df.sort_values(by=x_col)
            fig = px.line(
                sorted_df, x=x_col, y=y_col, color=color_col,
                color_discrete_sequence=palette,
                title=chart_title,
                markers=True
            )

        elif chart_type in ["Bar Chart", "Donut / Pie Chart"]:
            if not x_col:
                raise ValueError("Category column required.")
            
            if y_col and y_col in df.columns and pd.api.types.is_numeric_dtype(df[y_col]):
                # Aggregate y by x
                if agg_func == "mean":
                    agg_df = df.groupby(x_col)[y_col].mean().reset_index()
                elif agg_func == "median":
                    agg_df = df.groupby(x_col)[y_col].median().reset_index()
                else:
                    agg_df = df.groupby(x_col)[y_col].sum().reset_index()
                val_col = y_col
            else:
                agg_df = df[x_col].value_counts().reset_index()
                agg_df.columns = [x_col, "Count"]
                val_col = "Count"

            if chart_type == "Donut / Pie Chart":
                fig = px.pie(
                    agg_df.head(10), names=x_col, values=val_col,
                    color_discrete_sequence=palette,
                    hole=0.45,
                    title=chart_title
                )
            else:
                fig = px.bar(
                    agg_df.head(25), x=x_col, y=val_col,
                    color=color_col if color_col in agg_df.columns else None,
                    color_discrete_sequence=palette,
                    title=chart_title
                )

        elif chart_type == "Correlation Heatmap":
            num_cols = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]
            if len(num_cols) < 2:
                fig.add_annotation(text="At least 2 numerical columns are required for correlation matrix.", showarrow=False)
                return fig
            corr = df[num_cols].corr()
            fig = px.imshow(
                corr, text_auto=True, aspect="auto",
                color_continuous_scale="RdBu_r",
                title=chart_title
            )

    except Exception as e:
        fig = go.Figure()
        fig.add_annotation(text=f"Error rendering chart: {str(e)}", showarrow=False, font=dict(color="#ef4444"))

    # Apply modern styling
    fig.update_layout(
        template="plotly_white",
        title_font=dict(size=18, family="Arial, sans-serif", color="#0f172a"),
        margin=dict(l=40, r=40, t=50, b=40),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    return fig
