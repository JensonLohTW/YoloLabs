
import pandas as pd

excel_path = "excel_demo/demo.xlsx"
xl = pd.ExcelFile(excel_path)

print(f"Sheet names: {xl.sheet_names}")

for sheet in xl.sheet_names:
    df = pd.read_excel(excel_path, sheet_name=sheet, nrows=5)
    print(f"\nSheet: {sheet}")
    print(f"Columns: {df.columns.tolist()}")
    print(df.head(2))
