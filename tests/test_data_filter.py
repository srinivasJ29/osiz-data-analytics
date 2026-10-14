import pandas as pd
import pytest
from src.data_filter import apply_filters
from src.data_editor import rename_column, drop_columns, add_new_row

def test_apply_filters_search():
    df = pd.DataFrame({"Name": ["Alice", "Bob", "Charlie"], "City": ["New York", "London", "Paris"]})
    specs = {"search_query": "lon"}
    filtered = apply_filters(df, specs)
    assert len(filtered) == 1
    assert filtered.iloc[0]["Name"] == "Bob"

def test_apply_filters_numeric():
    df = pd.DataFrame({"Age": [20, 30, 40, 50]})
    specs = {"numeric_ranges": {"Age": (25, 45)}}
    filtered = apply_filters(df, specs)
    assert len(filtered) == 2
    assert list(filtered["Age"]) == [30, 40]

def test_apply_filters_categorical():
    df = pd.DataFrame({"Category": ["A", "B", "C", "A"]})
    specs = {"categorical_values": {"Category": ["A", "C"]}}
    filtered = apply_filters(df, specs)
    assert len(filtered) == 3

def test_editor_rename():
    df = pd.DataFrame({"Old": [1, 2]})
    new_df, ok, msg = rename_column(df, "Old", "New")
    assert ok is True
    assert "New" in new_df.columns
    assert "Old" not in new_df.columns

def test_editor_drop():
    df = pd.DataFrame({"A": [1], "B": [2], "C": [3]})
    new_df, cnt = drop_columns(df, ["B"])
    assert cnt == 1
    assert list(new_df.columns) == ["A", "C"]

def test_editor_add_row():
    df = pd.DataFrame({"A": [1], "B": ["x"]})
    new_df, ok, msg = add_new_row(df, {"A": 2, "B": "y"})
    assert ok is True
    assert len(new_df) == 2
