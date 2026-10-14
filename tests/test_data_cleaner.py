import pandas as pd
import numpy as np
import pytest
from src.data_cleaner import (
    remove_duplicates, drop_missing_values, fill_missing_values,
    trim_and_case_text, detect_outliers_iqr, handle_outliers, cast_column_type
)

def test_remove_duplicates():
    df = pd.DataFrame({"A": [1, 1, 2], "B": ["x", "x", "y"]})
    cleaned, removed = remove_duplicates(df)
    assert removed == 1
    assert len(cleaned) == 2

def test_drop_missing_values():
    df = pd.DataFrame({"A": [1, None, 3], "B": [4, 5, 6]})
    cleaned, dropped = drop_missing_values(df, axis=0)
    assert dropped == 1
    assert len(cleaned) == 2

def test_fill_missing_values():
    df = pd.DataFrame({"A": [10.0, 20.0, None]})
    cleaned, count = fill_missing_values(df, "A", strategy="mean")
    assert count == 1
    assert cleaned["A"].iloc[2] == 15.0

def test_trim_and_case_text():
    df = pd.DataFrame({"A": ["  Hello ", " WORLD "]})
    cleaned, count = trim_and_case_text(df, ["A"], trim_spaces=True, case_transform="lower")
    assert cleaned["A"].iloc[0] == "hello"
    assert cleaned["A"].iloc[1] == "world"

def test_outlier_detection_and_handling():
    df = pd.DataFrame({"A": [10, 11, 12, 10, 11, 12, 1000]})
    mask, low, up = detect_outliers_iqr(df, "A")
    assert mask.sum() == 1
    capped_df, affected = handle_outliers(df, "A", action="cap")
    assert affected == 1
    assert capped_df["A"].max() <= up

def test_cast_column_type():
    df = pd.DataFrame({"A": ["1", "2", "3"]})
    cleaned, ok, msg = cast_column_type(df, "A", "integer")
    assert ok is True
    assert pd.api.types.is_integer_dtype(cleaned["A"])
