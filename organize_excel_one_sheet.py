import pandas as pd
import argparse
#python organize_excel.py --folder indicators_lines_cols --file merged_indicators
parser = argparse.ArgumentParser(description='Process graph matching parameters.')
parser.add_argument('--file', type=str, required=True, help='Name of the  file (without .dot extension)')
parser.add_argument('--folder', type=str, required=True, help='Name of the folder')

args = parser.parse_args()	
file = args.file
folder = args.folder

# Input and output file paths
input_file = f"/home/etud/Bureau/projet/{folder}/{file}.xlsx"
output_file = f"/home/etud/Bureau/projet/{folder}/grouped_by_pattern.xlsx"

# Load Excel file
df = pd.read_excel(input_file)

# Determine the order of first appearance of each unique pattern
pattern_order = df['Pattern'].dropna().drop_duplicates()

# Sort the DataFrame by the order of first occurrence of each 'Pattern'
df['Pattern'] = pd.Categorical(df['Pattern'], categories=pattern_order, ordered=True)
df_sorted = df.sort_values('Pattern')


# Sort by Pattern (first-seen order), then ILF (FAUX before VRAI)
df_sorted = df.sort_values(by=['Pattern'])


# Save to a new Excel file
df_sorted.to_excel(output_file, index=False)

print(f"Rows grouped by 'Pattern' in first-seen order. Saved to: {output_file}")
