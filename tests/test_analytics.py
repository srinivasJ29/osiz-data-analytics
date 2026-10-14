import pandas as pd
import pytest
from src.analytics import compute_dataset_kpis, compute_numerical_summary, compute_categorical_summary, generate_automated_insights
from src.visualization import recommend_charts, create_chart

def test_compute_kpis():
    df = pd.DataFrame({"A": [1, 2, None], "B": ["x", "y", "x"]})
    kpis = compute_dataset_kpis(df)
    assert kpis["total_rows"] == 3
    assert kpis["total_cols"] == 2
    assert kpis["missing_cells"] == 1

def test_numerical_summary():
    df = pd.DataFrame({"Score": [10.0, 20.0, 30.0]})
    summary = compute_numerical_summary(df)
    assert not summary.empty
    assert summary.iloc[0]["Mean"] == 20.0
    assert summary.iloc[0]["Min"] == 10.0
    assert summary.iloc[0]["Max"] == 30.0

def test_categorical_summary():
    df = pd.DataFrame({"Dept": ["HR", "IT", "IT", "Sales"]})
    summary = compute_categorical_summary(df)
    assert not summary.empty
    assert summary.iloc[0]["Top Category"] == "IT"
    assert summary.iloc[0]["Top Frequency"] == 2

def test_automated_insights():
    df = pd.DataFrame({"A": [1, 2, 3], "B": [10, 20, 30]})
    insights = generate_automated_insights(df)
    assert len(insights) > 0
    # Should detect strong correlation
    has_corr = any("Correlation" in ins["title"] for ins in insights)
    assert has_corr is True

def test_recommend_charts():
    df = pd.DataFrame({"Value": [1, 2, 3], "Category": ["A", "B", "C"]})
    recs = recommend_charts(df)
    assert len(recs) >= 2

def test_create_chart():
    df = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]})
    fig = create_chart(df, "Scatter Plot", x_col="A", y_col="B")
    assert fig is not None
