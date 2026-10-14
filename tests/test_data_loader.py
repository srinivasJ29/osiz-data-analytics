import io
import pandas as pd
import pytest
from src.data_loader import load_dataset, get_dataset_metadata
from src.data_validator import validate_dataframe

def test_load_valid_csv():
    csv_content = io.StringIO("Name,Age,Salary\nAlice,30,70000\nBob,25,50000\n")
    df, err = load_dataset(csv_content, "test.csv")
    assert err is None
    assert df is not None
    assert len(df) == 2
    assert list(df.columns) == ["Name", "Age", "Salary"]

def test_load_valid_excel():
    excel_path = "sample_data/sample_ecommerce_data.xlsx"
    df, err = load_dataset(excel_path, "sample_ecommerce_data.xlsx")
    assert err is None
    assert df is not None
    assert len(df) > 0

def test_load_invalid_extension():
    f = io.StringIO("hello")
    df, err = load_dataset(f, "test.txt")
    assert df is None
    assert "Unsupported file extension" in err

def test_load_empty_csv():
    f = io.StringIO("")
    df, err = load_dataset(f, "empty.csv")
    assert df is None
    assert "empty" in err.lower() or "failed" in err.lower()

def test_metadata_extraction():
    df = pd.DataFrame({
        "A": [1, 2, 2, None],
        "B": ["x", "y", "y", "z"]
    })
    meta = get_dataset_metadata(df, "test.csv")
    assert meta["total_rows"] == 4
    assert meta["total_cols"] == 2
    assert "A" in meta["numerical_columns"]
    assert "B" in meta["categorical_columns"]

def test_validator():
    df = pd.DataFrame({"A": [1, 2, 3]})
    res = validate_dataframe(df)
    assert res["is_valid"] is True
    assert len(res["errors"]) == 0
