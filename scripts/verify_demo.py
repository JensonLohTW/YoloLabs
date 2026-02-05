import pandas as pd
import sys
import os

EXCEL_PATH = '/Users/jeeshyang/Workspace/Work/YoloLabs/excel_demo/demo.xlsx'
CSV_PATH = '/Users/jeeshyang/Workspace/Work/YoloLabs/result_images/combined_results.csv'
REPORT_PATH = 'verification_report.md'

def normalize_tag(tag):
    if pd.isna(tag):
        return None
    return str(tag).strip()

def main():
    print(f"Loading CSV from {CSV_PATH}...")
    try:
        df_csv = pd.read_csv(CSV_PATH)
    except Exception as e:
        print(f"Error reading CSV: {e}")
        sys.exit(1)
    
    if '識別內容' not in df_csv.columns:
        print("Error: Column '識別內容' not found in CSV.")
        sys.exit(1)
        
    csv_tags_raw = df_csv['識別內容'].dropna().apply(normalize_tag).tolist()
    csv_tags = [t for t in csv_tags_raw if t]
    csv_counts = pd.Series(csv_tags).value_counts()
    csv_duplicates = csv_counts[csv_counts > 1].index.tolist()
    
    print(f"Loaded {len(csv_tags)} tags from CSV.")

    print(f"Loading Excel from {EXCEL_PATH}...")
    try:
        df_excel = pd.read_excel(EXCEL_PATH, header=0)
    except Exception as e:
        print(f"Error reading Excel: {e}")
        sys.exit(1)
        
    excel_tags = []
    
    # Check if required columns exist
    if 'Valve' not in df_excel.columns or 'Number' not in df_excel.columns:
        print("Error: Columns 'Valve' and 'Number' not found in Excel.")
        print(f"Available columns: {df_excel.columns.tolist()}")
        sys.exit(1)

    for index, row in df_excel.iterrows():
        t_val = row['Valve']
        n_val = row['Number']
        
        t_str = normalize_tag(t_val)
        n_str = normalize_tag(n_val)
        
        if not t_str or not n_str:
            continue
            
        tag = f"{t_str} {n_str}"
        excel_tags.append(tag)
                    
    print(f"Loaded {len(excel_tags)} tags from Excel.")
    
    excel_counts = pd.Series(excel_tags).value_counts()
    excel_duplicates = excel_counts[excel_counts > 1].index.tolist()
    
    excel_set = set(excel_tags)
    csv_set = set(csv_tags)
    
    missing_in_csv = excel_set - csv_set
    extra_in_csv = csv_set - excel_set
    
    # Generate Report
    report_lines = []
    report_lines.append(f"# 比對結果報告 (Demo)")
    report_lines.append(f"**Excel 檔案**: `{os.path.basename(EXCEL_PATH)}`")
    report_lines.append(f"**CSV 檔案**: `{os.path.basename(CSV_PATH)}`")
    report_lines.append("")
    report_lines.append("## 摘要")
    report_lines.append(f"- **Excel 總項目數**: {len(excel_tags)}")
    report_lines.append(f"- **Excel 唯一項目數**: {len(excel_set)}")
    report_lines.append(f"- **CSV 總項目數**: {len(csv_tags)}")
    report_lines.append(f"- **CSV 唯一項目數**: {len(csv_set)}")
    report_lines.append("")
    report_lines.append("## 異常項目")
    
    if excel_duplicates:
        report_lines.append("### Excel 中的重複項目")
        for item in excel_duplicates:
            report_lines.append(f"- `{item}` (出現次數: {excel_counts[item]})")
    else:
         report_lines.append("### Excel 中的重複項目")
         report_lines.append("- 無")

    if csv_duplicates:
        report_lines.append("### CSV 中的重複識別")
        for item in csv_duplicates:
            report_lines.append(f"- `{item}` (出現次數: {csv_counts[item]})")
    else:
         report_lines.append("### CSV 中的重複識別")
         report_lines.append("- 無")

    report_lines.append("")
    report_lines.append("## 比對詳細結果")
    
    if missing_in_csv:
        report_lines.append(f"### 缺失項目 (Excel 有但 CSV 無) - 共 {len(missing_in_csv)} 筆")
        for item in sorted(list(missing_in_csv)):
            report_lines.append(f"- [ ] `{item}`")
    else:
        report_lines.append("### 缺失項目")
        report_lines.append("- 無 (所有 Excel 項目均在 CSV 中找到)")

    if extra_in_csv:
        report_lines.append(f"### 多餘項目 (CSV 有但 Excel 無) - 共 {len(extra_in_csv)} 筆")
        for item in sorted(list(extra_in_csv)):
            report_lines.append(f"- `{item}`")
    else:
        report_lines.append("### 多餘項目")
        report_lines.append("- 無")
        
    report_content = "\n".join(report_lines)
    
    with open(REPORT_PATH, 'w', encoding='utf-8') as f:
        f.write(report_content)
        
    print(f"Report generated: {REPORT_PATH}")

if __name__ == "__main__":
    main()
