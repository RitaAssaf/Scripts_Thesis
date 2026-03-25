#!/usr/bin/env python3
"""
Wrapper script to run components_divider_1.py on one or more DOT graphs,
capture the generated subcomponent files, and save them in Excel.
Supports comma-separated arguments like:
python3 run_components_divider.py "gt-08252025091213","gt-08252025091214","gt-08252025091215"
"""
from datetime import datetime
import pandas as pd
import re
import subprocess
import sys
import os
from datetime import datetime
import pandas as pd



def run_rows_cols_generator(input_graph):
	"""
	Run components_divider_1.py with the given input graph.
	Parse the verbose output to extract component number, node count, and file path.
	"""
	path = input_graph.split("/")
	cmd = ["python3", "rows_columns_generator.py", "--position_graph_folder", path[8]
		, "--position_graph", path[9].replace(".dot", "")]

	try:
		result = subprocess.run(
			cmd,
			text=True,
			capture_output=True,
			check=True
		)
	except subprocess.CalledProcessError as e:
		print(f"[ERROR] Failed to run components_divider_1.py for {input_graph}:\n{e.stderr}", file=sys.stderr)
		return []

	details = []
	for line in result.stdout.splitlines():
		# Match "Wrote component 1: 11 nodes -> /path/to/file.dot"
		match = re.match(
			r"DOT saved in\s*:'([^']+)'\s*,\s*num_nodes:(\d+),\s*num_edges:(\d+),\s*max_degree:\s*(\d+),\s*num_components:\s*(\d+)",
			line.strip()
		)
		if match:
			path = match.group(1).strip()
			num_nodes = int(match.group(2))
			num_edges = int(match.group(3))
			max_degree = int(match.group(4))
			num_components = int(match.group(5))

			details.append( path)

	return details


def run_component_splitter(input_graph, verbose=False):
	"""
	Run components_divider_1.py with the given input graph.
	Parse the verbose output to extract component number, node count, and file path.
	"""
	cmd = ["python3", "components_divider_1.py", input_graph, "-v"]

	try:
		result = subprocess.run(
			cmd,
			text=True,
			capture_output=True,
			check=True
		)
	except subprocess.CalledProcessError as e:
		print(f"[ERROR] Failed to run components_divider_1.py for {input_graph}:\n{e.stderr}", file=sys.stderr)
		return []

	details = []
	for line in result.stdout.splitlines():
		# Match "Wrote component 1: 11 nodes -> /path/to/file.dot"
		match = re.match(r"Wrote component (\d+): (\d+) nodes -> (.+\.dot)", line.strip())
		if match:
			comp_num = int(match.group(1))
			node_count = int(match.group(2))
			path = match.group(3).strip()
			details.append((input_graph, comp_num, node_count, path))

	return details
import os
import pandas as pd
from datetime import datetime

def save_to_excel(all_results, output_dir="logs"):
	"""
	Save all parent graphs and their generated subcomponents into a single Excel file.
	"""
	os.makedirs(output_dir, exist_ok=True)
	timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
	excel_path = os.path.join(output_dir, f"subcomponents_{timestamp}.xlsx")

	# Flatten list of results
	rows = []
	for records in all_results.values():
		for parent, comp_num, node_count, path, lctr, glc_card in records:
			rows.append({
				"Parent Graph": parent,
				"Component Number": comp_num,
				"Node Count": node_count,
				"Subcomponent": path.split("dat/")[1].replace('.dot',''),
				"lctr": lctr.split("lcres/")[1].replace('.dot',''),
				"glc_card": glc_card.split("lcres/")[1].replace('.dot','')
			})

	# Create DataFrame
	df = pd.DataFrame(rows)

	# Create a summary row: concatenate values under each column
	summary_row = {}
	for col in df.columns:
		combined = df[col].dropna().astype(str).tolist()
		summary_row[col] = ",".join(f'"{name}"' for name in combined)

	# Append the summary row to the DataFrame
	df = pd.concat([df, pd.DataFrame([summary_row])], ignore_index=True)

	# Save to Excel
	df.to_excel(excel_path, index=False, sheet_name="subcomponents")

	return excel_path


def main():
	#files from class_b_25082025091213
	graph_names = ["gt-08252025091213","gt-08252025091214","gt-08252025091215","gt-08252025091216","gt-08252025091217","gt-08252025091218","gt-08252025091219","gt-08252025091220","gt-08252025091221","gt-08252025091221","gt-08252025091222","gt-08252025091223","gt-08252025091224","gt-08252025091225","gt-08252025091226","gt-08252025091227","gt-08252025091228","gt-08252025091229","gt-08252025091230","gt-08252025091231"]
	verbose = True
	all_results = {}
	for graph in graph_names:
		print(f"[INFO] Running component splitter on {graph}.dot ...")
		files = run_component_splitter(graph, verbose=verbose)
		if files:
			print(f"[INFO] Generated {len(files)} subcomponents for {graph}")
			all_results[graph] = files
		else:
			print(f"[WARNING] No subcomponents found for {graph}")

	if not all_results:
		print("[WARNING] Nothing to save.")
		sys.exit(0)

	dict_rows_cols = {}


	for parent, records in all_results.items():
		new_records = []
		for _, comp_num, node_count, path in records:  # _ = parent (ignored)
			rows_files = run_rows_cols_generator(path)

			if len(rows_files) == 2:
				lctr, glc_card = rows_files
			else:
				lctr, glc_card = None, None

			new_records.append((parent, comp_num, node_count, path, lctr, glc_card))

		dict_rows_cols[parent] = new_records



	excel_path = save_to_excel(dict_rows_cols)
	print(f"[INFO] All results saved in {excel_path}")

if __name__ == "__main__":
	main()
