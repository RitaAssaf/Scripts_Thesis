import pandas as pd
import argparse

# Usage:
# python organize_excel.py --folder indicators_lines_cols --file merged_indicators

parser = argparse.ArgumentParser(description='Organize each sheet in Excel by the "Pattern" column.')
parser.add_argument('--file', type=str, required=True, help='Name of the file (without .xlsx extension)')
parser.add_argument('--folder', type=str, required=True, help='Name of the folder')

args = parser.parse_args()
file = args.file
folder = args.folder

# Input and output file paths
input_file = f"/home/etud/Bureau/projet/{folder}/{file}.xlsx"
output_file = f"/home/etud/Bureau/projet/{folder}/grouped_by_pattern.xlsx"

# Load all sheets from the Excel file
xls = pd.read_excel(input_file, sheet_name=None)  # dict of DataFrames

# Prepare writer for the output Excel
with pd.ExcelWriter(output_file) as writer:
	for sheet_name, df in xls.items():
		if 'Pattern' not in df.columns:
			print(f"Skipping sheet '{sheet_name}' (no 'Pattern' column).")
			continue

		# Determine the order of first appearance of each unique pattern
		pattern_order = df['Pattern'].dropna().drop_duplicates()

		# Sort the DataFrame by the order of first occurrence of each 'Pattern'
		df['Pattern'] = pd.Categorical(df['Pattern'], categories=pattern_order, ordered=True)
		df_sorted = df.sort_values('Pattern')

		# Save the sorted sheet
		df_sorted.to_excel(writer, sheet_name=sheet_name, index=False)
		print(f"Processed sheet '{sheet_name}'.")

print(f"All sheets sorted by 'Pattern' column and saved to: {output_file}")
