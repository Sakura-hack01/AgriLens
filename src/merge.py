import pandas as pd
import os
import glob
import re
source_folder = r"C:\Users\Saket Dixit\Downloads\Agro Sentinel\data\raw"
output_file = r"C:\Users\Saket Dixit\Downloads\Agro Sentinel\data\agro_sentinel_consolidated.csv"

def extract_master_headers(filepath):
  
    print(f"  > Learning schema from: {os.path.basename(filepath)}")
    
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    dfs = pd.read_html(content, header=None)
    main_df = max(dfs, key=len)
    headers = main_df.iloc[3, :23].tolist()
    clean_headers = [str(h).replace('\n', ' ').strip() for h in headers]
    print(f"  > Headers detected: {clean_headers}")
    return clean_headers

def process_single_file(filepath, master_headers):
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        # 1. Snipe Date
        date_match = re.search(r'(\d{2}/\d{2}/\d{4})', content)
        file_date = date_match.group(1) if date_match else "Unknown"
        # 2. Read Table
        dfs = pd.read_html(content, header=None)
        if not dfs: return None
        main_df = max(dfs, key=len)
        df_chunk = main_df.iloc[8:, :23].copy()
        footer_keywords = ['Source:', 'Note:', 'Developed by', 'State civil supplies', 'NR ->']
        mask = df_chunk.iloc[:, 0].astype(str).str.contains('|'.join(footer_keywords), case=False, na=False)
        footer_indices = df_chunk.index[mask]
        
        if not footer_indices.empty:
            cut_off_index = footer_indices[0]
            df_chunk = df_chunk.loc[ : cut_off_index - 1]

        df_chunk.columns = master_headers
        df_chunk = df_chunk.dropna(subset=[master_headers[0]])
        df_chunk = df_chunk[df_chunk[master_headers[0]].astype(str).str.strip() != '']

        if df_chunk.empty: return None
        df_chunk.insert(0, 'Date', file_date)

        return df_chunk

    except Exception as e:
        print(f"  [Error] {os.path.basename(filepath)}: {e}")
        return None

print(">>> MIT FINAL MERGER (Footer Guillotine Enabled) <<<")
all_files = glob.glob(os.path.join(source_folder, "*.xls"))
all_files.sort()

if not all_files:
    print("CRITICAL: No files found.")
    exit()
try:
    master_header_list = extract_master_headers(all_files[0])
except Exception as e:
    print(f"CRITICAL: Could not extract headers. {e}")
    exit()
consolidated_data = []
print(f"Processing {len(all_files)} files...")

for filename in all_files:
    df = process_single_file(filename, master_header_list)
    if df is not None:
        consolidated_data.append(df)
      
if consolidated_data:
    final_df = pd.concat(consolidated_data, ignore_index=True)
    final_df['Date'] = pd.to_datetime(final_df['Date'], format='%d/%m/%Y', errors='coerce')
    final_df = final_df.sort_values(by=['Date'])
    
    final_df.to_csv(output_file, index=False)
    print(f"SUCCESS! Consolidated {len(consolidated_data)} files to: {output_file}")
    print(f"Final Shape: {final_df.shape}")
else:
    print("No valid data extracted.")
