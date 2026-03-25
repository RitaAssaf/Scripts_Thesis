#!/usr/bin/env python3
"""
batch_generateur.py
Run generateur.py on a list of position graph
Usage
-----
python batch_rows_cols_generator.py --graph_filenames

"""

import argparse
import subprocess
import re
import time
from pathlib import Path
from datetime import datetime
import pandas as pd
import os

def extract_basename(path_str):
	"""Extracts filename without extension from a path."""
	return Path(path_str).stem


# Regex patterns
DOT_PATH_RE = re.compile(r"(?P<path>[^\s'\"()]+?\.dot)")
NUM_NODES_RE = re.compile(r"num_nodes:\s*(?P<nodes>\d+)")
NUM_EDGES_RE = re.compile(r"num_edges:\s*(?P<edges>\d+)")
MAX_DEGREE_RE = re.compile(r"max_degree:\s*(?P<degree>\d+)")
NUM_COMPONENTS_RE = re.compile(r"num_components:\s*(?P<components>\d+)")
POS_GRAPH_RE = re.compile(r"position_graph:\s*(?P<position>[^\s]+)")


def run_generateur_once(graph) -> dict:
	"""Run generateur.py once and return dict with file list and matrix stats."""
	cmd = ["python", "rows_columns_generator.py", "--position_graph", str(graph)]

	result = subprocess.run(cmd, capture_output=True, text=True, check=True)
	stdout = result.stdout or ""

	match = POS_GRAPH_RE.search(stdout)
	posfilename = match.group("position") if match else None

	# --- File stats (.dot files) ---
	files = []
	for line in stdout.splitlines():
		for m in DOT_PATH_RE.finditer(line):
			entry = {
				"filename": extract_basename(m.group("path")),
				"num_nodes": None,
				"num_edges": None,
				"max_degree": None,
				"num_components": None,
			}
			if (mn := NUM_NODES_RE.search(line)):
				entry["num_nodes"] = int(mn.group("nodes"))
			if (me := NUM_EDGES_RE.search(line)):
				entry["num_edges"] = int(me.group("edges"))
			if (md := MAX_DEGREE_RE.search(line)):
				entry["max_degree"] = int(md.group("degree"))
			if (mc := NUM_COMPONENTS_RE.search(line)):
				entry["num_components"] = int(mc.group("components"))
			files.append(entry)

	return {"files": files, "posfilename": posfilename}


def flatten_runs(runs: list[dict]) -> pd.DataFrame:
	"""Flatten all runs into one DataFrame (one row per run)."""
	max_files = max((len(r["files"]) for r in runs), default=1)
	flat_rows = []

	for run in runs:
		flat = {}
		files = run["files"]
		posfilename = run["posfilename"]

		# Add per-file info
		for i in range(max_files):
			prefix = f"file{i+1}_"
			if i < len(files):
				entry = files[i]
				flat[prefix + "name"] = entry.get("filename")
				flat[prefix + "nodes"] = entry.get("num_nodes")
				flat[prefix + "edges"] = entry.get("num_edges")
				flat[prefix + "degree"] = entry.get("max_degree")
				flat[prefix + "components"] = entry.get("num_components")
			else:
				# pad missing
				for field in ["name", "nodes", "edges", "degree", "components"]:
					flat[prefix + field] = None

		flat["position graph"]=posfilename
		flat_rows.append(flat)

	df = pd.DataFrame(flat_rows)
	return df

def add_summary_row_0(df: pd.DataFrame) -> pd.DataFrame:
	"""Add a summary row: combine file names and average matrix stats."""
	summary = {col: pd.NA for col in df.columns}

	# Combine filenames
	for col in df.columns:
		base_col = col.removesuffix("_x").removesuffix("_y")

		if base_col.endswith("_name"):
			combined = df[col].dropna().astype(str).tolist()
			summary[col] = ",".join(f'"{name}"' for name in combined)

	# Label the first name column
	first_name_col = next((c for c in df.columns if c.endswith("_name")), None)
	if first_name_col:
		summary[first_name_col] = "TOTAL → " + str(summary[first_name_col])

	# Average numeric matrix stats
	matrix_cols = ["m", "n", "N", "density", "row_var", "col_var",
				   "i_mean", "j_mean", "spread", "entropy"]

	for col in matrix_cols:
		if col in df.columns:
			summary[col] = df[col].mean(skipna=True)
	summary_df = pd.DataFrame([summary], index=[0])
	df = pd.concat([df, summary_df], ignore_index=True)
	return df


def add_summary_row(df: pd.DataFrame) -> pd.DataFrame:
	"""Add a summary row: combine file names and average matrix stats."""

	summary = {}

	# ----------------------------
	# Combine filenames
	# ----------------------------
	for col in df.columns:
		base_col = col.removesuffix("_x").removesuffix("_y") 
		if base_col.endswith("_name"):
			combined = df[col].dropna().astype(str).tolist()
			if combined:
				summary[col] = ",".join(f'"{name}"' for name in combined)

	# ----------------------------
	# Average numeric matrix stats
	# ----------------------------
	matrix_cols = [
		"m", "n", "N", "density",
		"row_var", "col_var",
		"i_mean", "j_mean",
		"spread", "entropy"
	]

	for col in matrix_cols:
		if col in df.columns:
			summary[col] = df[col].mean(skipna=True)

	# ----------------------------
	# Append row
	# ----------------------------
	if summary:
		summary_df = pd.DataFrame([summary])
		df = pd.concat([df, summary_df], ignore_index=True)

	return df

def main():
	timestamp = datetime.now().strftime("%d%m%Y%H%M%S")

	parser = argparse.ArgumentParser(description="Batch-run generateur.py")
	parser.add_argument("--graph_filenames", default="generated_files", help="graph_filenames")
	args = parser.parse_args()


	graph_filenames = args.graph_filenames
	graph_filenames_list = args.graph_filenames.split(",") if args.graph_filenames else []

	excel_name = f"../generated_files_db/file_rowscols_{timestamp}.xlsx"

	runs = []
	for graph in graph_filenames_list:
		print(f"Rows/cols for {graph}", end="", flush=True)
		try:
			result = run_generateur_once(graph)
			runs.append(result)
			print(f" captured {len(result['files'])} file(s).")
		except subprocess.CalledProcessError as exc:
			print("\nError running generateur.py:\n", exc.stderr)
			raise SystemExit(1)
		time.sleep(0.5)

	df2 = flatten_runs(runs)
	

	folder = "/home/etud/Bureau/projet/fichiers/csp/generated_files_db/"
	file_class_desc=  os.path.join(folder, "file_25112025133728.xlsx")


	df1 = pd.read_excel(file_class_desc)  # contains column file4_name

	# Clean column names (important!)
	df1.columns = df1.columns.str.strip()
	df2.columns = df2.columns.str.strip()

	# Clean join columns (remove spaces, force string)
	df1["file4_name"] = df1["file4_name"].astype(str).str.strip()
	df2["position graph"] = df2["position graph"].astype(str).str.strip()

	# Rename column so names match (easier join)
	df2 = df2.rename(columns={"position graph": "file4_name"})

	# Inner join
	merged = pd.merge(df1, df2, on="file4_name", how="inner")

	merged = add_summary_row(merged)

	excel_path = Path(excel_name).expanduser().resolve()
	excel_path.parent.mkdir(parents=True, exist_ok=True)
	#df.to_excel(excel_path, index=False)

	merged.to_excel(excel_path, index=False)

	print(f"Saved results to {excel_path}")


if __name__ == "__main__":
	main()
