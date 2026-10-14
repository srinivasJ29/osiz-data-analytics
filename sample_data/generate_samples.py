import os
import pandas as pd
import numpy as np

def generate_sample_sales_dataset():
    np.random.seed(42)
    n_rows = 150
    
    categories = ['Electronics', 'Home & Kitchen', 'Apparel', 'Books', 'Fitness']
    regions = ['North America', 'Europe', 'Asia Pacific', 'Latin America']
    payment_methods = ['Credit Card', 'PayPal', 'Direct Debit', 'Crypto']
    
    dates = pd.date_range(start='2024-01-01', periods=n_rows, freq='D')
    
    df = pd.DataFrame({
        'Transaction_ID': [f'TXN_{1000+i}' for i in range(n_rows)],
        'Date': dates,
        'Category': np.random.choice(categories, size=n_rows),
        'Region': np.random.choice(regions, size=n_rows),
        'Payment_Method': np.random.choice(payment_methods, size=n_rows),
        'Quantity': np.random.randint(1, 20, size=n_rows),
        'Unit_Price': np.round(np.random.uniform(10.0, 500.0, size=n_rows), 2),
        'Customer_Rating': np.round(np.random.uniform(1.0, 5.0, size=n_rows), 1),
    })
    
    df['Total_Amount'] = np.round(df['Quantity'] * df['Unit_Price'], 2)
    
    # Introduce deliberate real-world data imperfections for demonstration
    # 1. Missing values
    df.loc[5:8, 'Customer_Rating'] = np.nan
    df.loc[20:22, 'Payment_Method'] = np.nan
    
    # 2. Duplicate rows
    dup_rows = df.iloc[[10, 11]].copy()
    df = pd.concat([df, dup_rows], ignore_index=True)
    
    # 3. Outlier values
    df.loc[15, 'Unit_Price'] = 4500.0
    df.loc[15, 'Total_Amount'] = 4500.0 * df.loc[15, 'Quantity']
    
    # 4. Leading/trailing whitespace
    df.loc[30, 'Category'] = '  Electronics  '
    
    os.makedirs('sample_data', exist_ok=True)
    csv_path = os.path.join('sample_data', 'sample_ecommerce_data.csv')
    excel_path = os.path.join('sample_data', 'sample_ecommerce_data.xlsx')
    
    df.to_csv(csv_path, index=False)
    df.to_excel(excel_path, index=False)
    print(f"Sample datasets generated:\n- {csv_path}\n- {excel_path}")

if __name__ == '__main__':
    generate_sample_sales_dataset()
