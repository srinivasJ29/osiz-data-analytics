# Sample Datasets for Smart Data Analyzer

This folder contains pre-configured synthetic datasets designed specifically for demonstrating and testing all features of the **Smart Data Analyzer**:

1. `sample_ecommerce_data.csv` (CSV format)
2. `sample_ecommerce_data.xlsx` (Excel format)

### Included Data Patterns
- **Dimensions**: 152 rows, 9 columns
- **Features**: Numerical (`Quantity`, `Unit_Price`, `Customer_Rating`, `Total_Amount`), Categorical (`Category`, `Region`, `Payment_Method`), Temporal (`Date`), and Identifiers (`Transaction_ID`).
- **Defects for Cleaning Stage**:
  - Duplicate rows (indexes 10 & 11 duplicated)
  - Missing values (in `Customer_Rating` and `Payment_Method`)
  - Outlier values (in `Unit_Price`)
  - Unsanitized whitespace (in `Category`)
