import pandas as pd
import pytest
from src.report_generator import generate_pdf_report, generate_word_report, export_to_csv, export_to_excel
from src.data_loader import get_dataset_metadata
from src.analytics import compute_numerical_summary, generate_automated_insights

def test_export_csv():
    df = pd.DataFrame({"A": [1, 2], "B": ["x", "y"]})
    csv_bytes = export_to_csv(df)
    assert isinstance(csv_bytes, bytes)
    assert len(csv_bytes) > 0
    assert b"A,B" in csv_bytes

def test_export_excel():
    df = pd.DataFrame({"A": [1, 2], "B": ["x", "y"]})
    excel_bytes = export_to_excel(df)
    assert isinstance(excel_bytes, bytes)
    assert len(excel_bytes) > 0

def test_generate_pdf_report():
    df = pd.DataFrame({"Metric1": [10, 20, 30], "Cat": ["A", "B", "C"]})
    meta = get_dataset_metadata(df, "test.csv")
    stats_df = compute_numerical_summary(df)
    insights = generate_automated_insights(df)
    audit = [{"action": "Test Action", "affected": 2, "timestamp": "2026-10-12 12:00:00"}]

    pdf_bytes = generate_pdf_report(
        metadata=meta,
        stats_df=stats_df,
        insights=insights,
        audit_history=audit,
        scope_name="Cleaned",
        report_title="Test Analytical Report",
        author_name="QA Engineer"
    )
    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 1000
    assert pdf_bytes.startswith(b"%PDF")

def test_generate_word_report():
    df = pd.DataFrame({"Metric1": [10, 20, 30], "Cat": ["A", "B", "C"]})
    meta = get_dataset_metadata(df, "test.csv")
    stats_df = compute_numerical_summary(df)
    insights = generate_automated_insights(df)
    audit = [{"action": "Test Action", "affected": 2, "timestamp": "2026-10-12 12:00:00"}]

    word_bytes = generate_word_report(
        metadata=meta,
        stats_df=stats_df,
        insights=insights,
        audit_history=audit,
        scope_name="Cleaned",
        report_title="Test Analytical Report",
        author_name="QA Engineer"
    )
    assert isinstance(word_bytes, bytes)
    assert len(word_bytes) > 1000
