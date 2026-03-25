import os
import pandas as pd
from datetime import datetime

# --- Configuration (replace with argparse if needed) ---
#folder = "indicators_lines_cols"
folder = "indicators_pos"

subfolder = "run_23032026141936"
keyword = ""
classfile = "g"

# Paths
base_path = f"/home/etud/Bureau/projet/{folder}/{subfolder}/"
timestamp = datetime.now().strftime("%d%m%Y%H%M%S")

merged_filename = f"merged_indicators{f'_{keyword}' if keyword else ''}.xlsx"
merged_file_path = os.path.join(base_path, merged_filename)
organized_file_path = os.path.join(base_path, f"results.xlsx")



#--- Clean previous outputs if they exist ---
for path in [merged_file_path, organized_file_path]:
	if os.path.exists(path):
		try:
			os.remove(path)
			print(f"Deleted existing file: {path}")
		except Exception as e:
			print(f"Error deleting {path}: {e}")




# --- Step 1: Merge last rows from all files ---
dfs = []
for filename in os.listdir(base_path):
	if filename.endswith(".xlsx") and (keyword in filename):
		filepath = os.path.join(base_path, filename)
		try:
			df = pd.read_excel(filepath)
			if not df.empty:
				last_row = df.tail(1)  # keep last row as DataFrame
				dfs.append(last_row)
		except Exception as e:
			print(f"Error reading {filename}: {e}")

if not dfs:
	print("No valid data found to merge.")
	exit(0)

merged_df = pd.concat(dfs, ignore_index=True)

# Keep only unique combinations of selected fields
unique_cols = ["Pattern", "Target", "ILF", "Order", "Typing", "Card"]
merged_df = merged_df.drop_duplicates(subset=[col for col in unique_cols if col in merged_df.columns])
merged_df = merged_df.drop_duplicates()

# Save merged file
merged_df.to_excel(merged_file_path, index=False)
print(f"Merged file saved as: {merged_file_path}")

# --- Step 2: Organize ---
try:
	# Remove unnamed columns if any
	merged_df = merged_df.loc[:, ~merged_df.columns.str.contains('^Unnamed')]

	# Sort safely
	sort_cols = [col for col in ["Target", "Pattern"] if col in merged_df.columns]
	df_sorted = merged_df.sort_values(by=sort_cols) if sort_cols else merged_df

	# --- Step 3: Assign Target_Index based on classfile ---
	classfile_base_path='/home/etud/Bureau/projet/fichiers/csp/generated_files_db/'
	classfile_path = os.path.join(classfile_base_path, classfile)
	if os.path.exists(classfile_path):
		class_df = pd.read_excel(classfile_path)

		# Build list of groups (targets on same row)
		target_groups = []
		for _, row in class_df.iterrows():
			group = [str(x) for x in row.values if pd.notna(x)]
			if group:
				target_groups.append(group)

		# Map targets to indices
		target_to_index = {}
		current_index = 0

		for group in target_groups:
			# Check if the whole group is unassigned
			unassigned = [t for t in group if t not in target_to_index]

			if unassigned:  
				# assign new index if at least one is unassigned
				idx = current_index
				current_index += 1
			else:
				# all already mapped, reuse the first one's index
				idx = target_to_index[group[0]]

			for t in group:
				target_to_index[t] = idx


		# Assign Target_Index to df_sorted, increment for targets not in classfile
		df_sorted["Target_Index"] = df_sorted["Target"].map(lambda t: target_to_index.get(str(t), current_index))

		# Place Target_Index after Target column
		if "Target" in df_sorted.columns and "Target_Index" in df_sorted.columns:
			cols = list(df_sorted.columns)
			target_pos = cols.index("Target")
			cols.insert(target_pos + 1, cols.pop(cols.index("Target_Index")))
			df_sorted = df_sorted[cols]



	# Save final organized file
	df_sorted.to_excel(organized_file_path, index=False)
	print(f"Organized file saved as: {organized_file_path}")


except Exception as e:
	print(f"Error during organizing step: {e}")
