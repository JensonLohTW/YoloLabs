
import pandas as pd
from pathlib import Path
import sys

def normalize_text(text):
    """Normalize text for comparison (upper case, strip spaces)."""
    if pd.isna(text): 
        return ""
    return str(text).strip().upper()

def compare_results():
    excel_path = "excel_demo/demo.xlsx"
    csv_dir = Path("result_images")
    
    print(f"Loading Excel: {excel_path}")
    try:
        xl = pd.ExcelFile(excel_path)
    except Exception as e:
        print(f"Error loading Excel: {e}")
        return

    report = []
    report.append("# Verification Comparison Report\n")
    
    total_missing = 0
    total_extra = 0
    total_match = 0
    
    # Iterate through sheets "工作表1" to "工作表8"
    for i in range(1, 9):
        sheet_name = f"工作表{i}"
        if sheet_name not in xl.sheet_names:
            print(f"Warning: Sheet {sheet_name} not found.")
            continue
            
        print(f"Processing {sheet_name}...")
        
        # Load Excel Sheet
        df_excel = pd.read_excel(excel_path, sheet_name=sheet_name)
        
        # Create set of expected labels (Valve + Number)
        # Handle potential missing columns if data is messy, but based on inspection looks consistent
        expected_items = set()
        for _, row in df_excel.iterrows():
            valve = normalize_text(row.get('Valve', ''))
            number = normalize_text(row.get('Number', ''))
            if valve and number:
                expected_items.add(f"{valve} {number}")
            elif valve: # Handle case with only one part if valid
                expected_items.add(valve)
            elif number:
                expected_items.add(number)
                
        # Find corresponding CSV
        # Pattern: *page-0000{i}_results.csv
        page_num_str = f"page-{i:05d}"
        csv_files = list(csv_dir.glob(f"*{page_num_str}_results.csv"))
        
        if not csv_files:
            report.append(f"## {sheet_name} (Page {i})")
            report.append(f"> ❌ **CSV File Not Found** for {page_num_str}\n")
            continue
            
        csv_path = csv_files[0]
        report.append(f"## {sheet_name} vs {csv_path.name}")
        
        # Load CSV
        try:
            df_csv = pd.read_csv(csv_path)
        except Exception as e:
            report.append(f"> ❌ **Error reading CSV**: {e}\n")
            continue
            
        found_items = set()
        if '識別內容' in df_csv.columns:
            for _, row in df_csv.iterrows():
                text = normalize_text(row['識別內容'])
                if text:
                    found_items.add(text)
        
        # Compare
        missing = sorted(list(expected_items - found_items))
        extra = sorted(list(found_items - expected_items))
        matched = expected_items.intersection(found_items)
        
        total_missing += len(missing)
        total_extra += len(extra)
        total_match += len(matched)
        
        # Report Stats
        report.append(f"- **Expected (Excel)**: {len(expected_items)}")
        report.append(f"- **Found (CSV)**: {len(found_items)}")
        report.append(f"- **Matched**: {len(matched)}")
        
        if not missing and not extra:
            report.append("> ✅ **Perfect Match**\n")
        else:
            if missing:
                report.append(f"> ❌ **Missing ({len(missing)})**: {', '.join(missing)}")
            if extra:
                report.append(f"> ⚠️ **Extra ({len(extra)})**: {', '.join(extra)}")
            report.append("") # Newline
            
    # Summary
    report.insert(1, f"**Summary**: {total_match} Matched, {total_missing} Missing, {total_extra} Extra\n")
    
    # Print and Save
    report_text = "\n".join(report)
    print("\n" + report_text)
    
    with open("verification_report.md", "w") as f:
        f.write(report_text)
    print(f"\nReport saved to verification_report.md")

if __name__ == "__main__":
    compare_results()
