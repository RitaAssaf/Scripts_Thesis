import pandas as pd
import sys
import os
import matplotlib.pyplot as plt

def compute_node_averages(input_files, output_file="averages.xlsx"):
	base_path = "/home/etud/Bureau/projet/fichiers/csp/generated_files_db/"
	results = []

	for file in input_files:
		try:
			# Ensure the file ends with .xlsx
			if not file.endswith('.xlsx'):
				file += '.xlsx'

			# Prepend base path
			file_path = os.path.join(base_path, file)

			# Read Excel file
			df = pd.read_excel(file_path)

			# Ensure required columns exist
			if "file3_nodes" not in df.columns or "file4_nodes" not in df.columns:
				print(f"Skipping {file}: missing required columns")
				continue

			# Compute averages
			avg_file3 = df["file3_nodes"].mean()
			avg_file4 = df["file4_nodes"].mean()
			avg_file5 = df["file5_nodes"].mean()

			# Store result
			results.append({
				"file_name": file,
				"avg_file3_nodes": avg_file3,
				"avg_file4_nodes": avg_file4,
				"avg_file5_nodes": avg_file5
			})

		except Exception as e:
			print(f"Error processing {file}: {e}")

	# Save results to Excel
	if results:
		result_df = pd.DataFrame(results)
		result_df.to_excel(output_file, index=False)
		print(f"Results saved to {output_file}")
	else:
		print("No valid data found.")
	return output_file

def plot_node_averages(excel_file):
	df = pd.read_excel(excel_file)

	# Ensure numeric values (replace commas with dots if needed)
	for col in ["avg_file3_nodes", "avg_file4_nodes", "avg_file5_nodes"]:
		df[col] = df[col].astype(str).str.replace(",", ".").astype(float)

	x = df["avg_file5_nodes"]
	y1 = df["avg_file3_nodes"]
	y2 = df["avg_file4_nodes"]

	plt.figure(figsize=(8, 6))
	plt.plot(x, y1, marker='o', label='Without cardinality')
	plt.plot(x, y2, marker='s', label='With cardinality')

	# Optionally label points with file names
	for i, file_name in enumerate(df["file_name"]):
		plt.text(x[i], y1[i], file_name.split(".")[0], fontsize=8, ha='right', va='bottom')
		plt.text(x[i], y2[i], file_name.split(".")[0], fontsize=8, ha='left', va='top')

	plt.xlabel("Position graph nodes")
	plt.ylabel("Equivalent Graph Nodes (avg)")
	plt.title("Effect of cardinality")
	plt.legend()
	plt.grid(True)
	plt.tight_layout()
	plt.show()



def plot_nodes_cardinality(input_files, sheet_name=0):
	file_path=''
	base_path = "/home/etud/Bureau/projet/fichiers/csp/generated_files_db/"

	for file in input_files:
		try:
			# Ensure the file ends with .xlsx
			if not file.endswith('.xlsx'):
				file += '.xlsx'

			# Prepend base path
			file_path = os.path.join(base_path, file)
		except exception as e:
			print(f'exception occured:{e}')


	df = pd.read_excel(file_path, sheet_name=sheet_name)

	# Remove rows with missing graph names
	df = df.dropna(subset=["file4_name"])


	# Extract columns
	x = df["file4_name"]
	y1 = df["file2_nodes"]
	y2 = df["file3_nodes"]
	y3 = df["file1_nodes_y"]

	# Plot
	plt.figure(figsize=(10,5))
	# plt.plot(x, y1, marker='o', label="without card")
	# plt.plot(x, y2, marker='s', label="card=4")
	# plt.plot(x, y3, marker='^', label="card=12")

	plt.plot(x, y1, marker='s', linestyle='-', linewidth=2, markersize=8, label="without card")
	plt.plot(x, y2, marker='o', linestyle='--', linewidth=2, markersize=8, label="card=4")
	plt.plot(x, y3, marker='^', linestyle=':', linewidth=2, markersize=8, label="card=12")


	# Labels and formatting
	plt.xlabel("Graph name")
	plt.ylabel("Rows/Cols Graph Nodes")
	plt.title("Comparison of nodes with without cardinality 4 and 12 per graph")
	plt.xticks(rotation=45)
	plt.legend()
	plt.tight_layout()

	plt.show()


if __name__ == "__main__":
	# Example usage: python plot_node_averages.py file1.xlsx file2.xlsx
	input_files = sys.argv[1:]  # command line arguments
	if not input_files:
		print("Please provide at least one Excel file as input.")
	else:
		# excel_file = compute_node_averages(input_files)
		# plot_node_averages(excel_file)
		plot_nodes_cardinality(input_files)