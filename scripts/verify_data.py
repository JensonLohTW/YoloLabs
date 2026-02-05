import pandas as pd
import sys
import os

EXCEL_PATH = '/Users/jeeshyang/Workspace/Work/YoloLabs/excel_demo/25CH0128-TSMC AP7P2 Chemical package (stage 1)_設備 ( 掛牌 )_260202 ( DCR ).xlsx'
CSV_PATH = '/Users/jeeshyang/Workspace/Work/YoloLabs/result_images/combined_results.csv'

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
    
    # Check for duplicates in CSV
    csv_counts = pd.Series(csv_tags).value_counts()
    csv_duplicates = csv_counts[csv_counts > 1].index.tolist()
    
    print(f"Loaded {len(csv_tags)} tags from CSV.")
    if csv_duplicates:
        print(f"Found {len(csv_duplicates)} duplicates in CSV.")

    print(f"Loading Excel from {EXCEL_PATH}...")
    try:
        xls = pd.ExcelFile(EXCEL_PATH)
    except Exception as e:
        print(f"Error reading Excel: {e}")
        sys.exit(1)
        
    excel_tags = []
    
    # Sheets to exclude
    sheets_to_skip = ['歷程', '總表']
    
    for sheet_name in xls.sheet_names:
        if sheet_name in sheets_to_skip:
            continue
            
        print(f"Processing sheet: {sheet_name}")
        
        # Read sheet without header to access by index
        df_sheet = pd.read_excel(xls, sheet_name=sheet_name, header=None)
        
        # Ensure we have enough rows
        if len(df_sheet) < 3:
            print(f"  Skipping sheet {sheet_name}: Not enough rows.")
            continue
            
        # Inspect Row 1 (index 1) for headers "Valve"
        # We need to be careful about what row the headers are on.
        # From previous inspection: Row 1 had "Valve" "Number".
        header_row_index = 1
        header_row = df_sheet.iloc[header_row_index]
        
        # Find columns where header contains 'Valve'
        valve_indices = []
        for idx, val in header_row.items():
            if isinstance(val, str) and 'Valve' in val:
                valve_indices.append(idx)
        
        print(f"  Found 'Valve' columns at indices: {valve_indices}")
        
        for v_idx in valve_indices:
            # Assumes Type is at v_idx, Number is at v_idx + 1
            if v_idx + 1 >= len(df_sheet.columns):
                print(f"  Warning: Valve column at {v_idx} has no following column.")
                continue
                
            # Extract data starting from row after header (index 2)
            type_vals = df_sheet.iloc[header_row_index+1:, v_idx]
            num_vals = df_sheet.iloc[header_row_index+1:, v_idx+1]
            
            for t_val, n_val in zip(type_vals, num_vals):
                t_str = normalize_tag(t_val)
                n_str = normalize_tag(n_val)
                
                # Check if end of list (often represented by NaN or empty or specific keywords)
                if not t_str or not n_str:
                    continue
                    
                # Sometimes there are trailing summary rows or empty rows
                
                tag = f"{t_str} {n_str}"
                excel_tags.append(tag)
                    
    print(f"Loaded {len(excel_tags)} tags from Excel.")
    
    # Check for duplicates in Excel
    excel_counts = pd.Series(excel_tags).value_counts()
    excel_duplicates = excel_counts[excel_counts > 1].index.tolist()
    
    if excel_duplicates:
        print(f"Found {len(excel_duplicates)} duplicates in Excel.")
        
    excel_set = set(excel_tags)
    csv_set = set(csv_tags)
    
    missing_in_csv = excel_set - csv_set
    extra_in_csv = csv_set - excel_set
    
    # Generate Report
    report_lines = []
    report_lines.append(f"# 比對結果報告")
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
    
    with open('verification_report.md', 'w', encoding='utf-8') as f:
        f.write(report_content)
        
    print("Report generated: verification_report.md")

if __name__ == "__main__":
    main()
