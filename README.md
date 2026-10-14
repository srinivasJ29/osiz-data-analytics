# Smart Data Analyzer

A complete, production-grade web application for dataset upload, interactive data inspection, automated data cleaning, multi-dimensional filtering, dynamic analytics/visualizations, and publication-ready PDF/Word/Excel/CSV analytical report generation.

## 🌟 Key Features
- **Stage 1: Dataset Upload & Inspection**: Supports CSV and Excel (.xlsx, .xls) files. Automatic schema inference, missing value detection, duplicate row identification, statistical profiling, and data safety isolation.
- **Stage 2: Data Cleaning & Filtering**: 
  - Null handling (drop, mean, median, mode, constant filling)
  - Duplicate removal & whitespace trimming / text case standardization
  - Outlier detection (IQR method) & winsorization / removal
  - Multi-column interactive filtering (Text search, numeric ranges, categorical multiselect, date ranges, missingness)
  - In-place cell/row editing, record additions, and column type casting with rollback history & undo.
- **Stage 3: Interactive Visualizations & Analytics**: 
  - Summary KPI cards
  - Smart automatic chart recommendation engine
  - Plotly interactive histograms, box plots, scatter matrices, heatmaps, bar charts, time-series line charts
  - Statistical insights generation (correlations, extrema, distribution skewness)
- **Stage 4: Analytical Report Generation**:
  - Downloadable PDF report with styled title page, executive summary, tables, and analytical observations
  - Cleaned & filtered CSV / Excel exports
  - Word (.docx) analytical report export

## 🚀 Setup & Launch (Windows PowerShell)

```powershell
# 1. Create a virtual environment (optional but recommended)
python -m venv .venv
.venv\Scripts\Activate.ps1

# 2. Install dependencies
python -m pip install -r requirements.txt

# 3. Launch application
python -m streamlit run app.py
```

## 🧪 Testing

Execute automated unit and integration tests:
```powershell
python -m pytest tests/ -v
```
