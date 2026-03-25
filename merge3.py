import os
import pandas as pd
import argparse
from datetime import datetime

# python merge3.py --folder indicators_pos --subfolder

# Argument parsing
parser = argparse.ArgumentParser(description='Merge last rows from Excel files and organize by pattern.')
parser.add_argument('--folder', type=str, required=True, help='Name of the folder inside /projet/ containing Excel files')
parser.add_argument('--subfolder', type=str, required=True, help='Name of the folder inside /projet/ containing Excel files')
parser.add_argument('--keyword', type=str, default="", help='Optional keyword to filter filenames')
args = parser.parse_args()

folder = args.folder
subfolder = args.subfolder
keyword = args.keyword

# Paths
base_path = f"/home/etud/Bureau/projet/{folder}/{subfolder}/"
timestamp = datetime.now().strftime("%d%m%Y%H%M%S")

merged_filename = f"merged_indicators{f'_{keyword}' if keyword else ''}.xlsx"
merged_file_path = os.path.join(base_path, merged_filename)
organized_file_path = os.path.join(base_path, f"results.xlsx")

# --- Step 1: Merge last rows from all files ---
dfs = []
for filename in os.listdir(base_path):
	if filename.endswith(".xlsx") and (keyword in filename):
		filepath = os.path.join(base_path, filename)
		try:
			df = pd.read_excel(filepath)
			if not df.empty:
				last_row = df.tail(1)   # keep last row as DataFrame
				dfs.append(last_row)
		except Exception as e:
			print(f"Error reading {filename}: {e}")

if not dfs:
	print("No valid data found to merge.")
	exit(0)

# concat automatically aligns columns (union of all headers)
merged_df = pd.concat(dfs, ignore_index=True)

# --- Keep only unique combinations of certain fields ---
unique_cols = ["Pattern","Target","ILF", "Order", "Typing", "Card"]
merged_df = merged_df.drop_duplicates(subset=[col for col in unique_cols if col in merged_df.columns])


# Remove duplicate rows
merged_df = merged_df.drop_duplicates()

# Save merged file
merged_df.to_excel(merged_file_path, index=False)
print(f"Merged file saved as: {merged_file_path}")

# --- Step 2: Organize ---
try:
	# Remove unnamed columns if any
	merged_df = merged_df.loc[:, ~merged_df.columns.str.contains('^Unnamed')]

	# Sorting safely (only if columns exist)
	sort_cols = [col for col in ["Target", "Pattern"] if col in merged_df.columns]
	if sort_cols:
		df_sorted = merged_df.sort_values(by=sort_cols)
	else:
		df_sorted = merged_df

	df_sorted.to_excel(organized_file_path, index=False)
	print(f"Organized file saved as: {organized_file_path}")
except Exception as e:
	print(f"Error during organizing step: {e}")
