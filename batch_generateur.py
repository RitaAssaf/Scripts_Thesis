#!/usr/bin/env python3
"""
batch_generateur.py
Run generateur.py N times and write one row per run to Excel, including:
 - .dot file stats (per file)
 - matrix stats (once per run)
 - a summary row combining filenames and averaging matrix stats
Usage
-----
python batch_generateur.py 5 --nodes 20 --grid 10                      # writes generated_files.xlsx
python batch_generateur.py 10 --xlsx my_runs.xlsx  # custom Excel filename
"""

import argparse
import subprocess
import re
import time
from pathlib import Path
from datetime import datetime
import pandas as pd


def extract_basename(path_str):
	"""Extracts filename without extension from a path."""
	return Path(path_str).stem


# Regex patterns
DOT_PATH_RE = re.compile(r"(?P<path>[^\s'\"()]+?\.dot)")
NUM_NODES_RE = re.compile(r"num_nodes:\s*(?P<nodes>\d+)")
NUM_EDGES_RE = re.compile(r"num_edges:\s*(?P<edges>\d+)")
MAX_DEGREE_RE = re.compile(r"max_degree:\s*(?P<degree>\d+)")
NUM_STRONGLY_RE = re.compile(r"num_strongly_components:\s*(?P<strongly>\d+)")
NUM_COMPONENTS_RE = re.compile(r"num_components:\s*(?P<components>\d+)")
DOT_MATRIX_REGEX = re.compile(r"\b([a-zA-Z_]+):([-+]?\d*\.?\d+)")


def run_generateur_once(nodes: int, grid: int) -> dict:
	"""Run generateur.py once and return dict with file list and matrix stats."""
	#cmd = ["python", "generateur.py", "--nodes", str(nodes), "--grid", str(grid)]
	cmd = ["python", "generateur_format_1000.py", "--nodes", str(nodes), "--grid", str(grid)]

	result = subprocess.run(cmd, capture_output=True, text=True, check=True)
	stdout = result.stdout or ""

	# --- Matrix stats (run-level) ---
	matrix_stats = dict(DOT_MATRIX_REGEX.findall(stdout))
	for k, v in matrix_stats.items():
		try:
			matrix_stats[k] = float(v)
		except ValueError:
			pass

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
				"num_strongly_components": None,
			}
			if (mn := NUM_NODES_RE.search(line)):
				entry["num_nodes"] = int(mn.group("nodes"))
			if (me := NUM_EDGES_RE.search(line)):
				entry["num_edges"] = int(me.group("edges"))
			if (md := MAX_DEGREE_RE.search(line)):
				entry["max_degree"] = int(md.group("degree"))
			if (ms := NUM_STRONGLY_RE.search(line)):
				entry["num_strongly_components"] = int(ms.group("strongly"))
			if (mc := NUM_COMPONENTS_RE.search(line)):
				entry["num_components"] = int(mc.group("components"))
			files.append(entry)

	return {"files": files, "matrix": matrix_stats}


def flatten_runs(runs: list[dict]) -> pd.DataFrame:
	"""Flatten all runs into one DataFrame (one row per run)."""
	max_files = max((len(r["files"]) for r in runs), default=1)
	flat_rows = []

	for run in runs:
		flat = {}
		files = run["files"]
		matrix = run["matrix"]

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
				flat[prefix + "strongly_components"] = entry.get("num_strongly_components")
			else:
				# pad missing
				for field in ["name", "nodes", "edges", "degree", "components", "strongly_components"]:
					flat[prefix + field] = None

		# Add matrix stats once per run
		for key in ["m", "n", "N", "density", "row_var", "col_var", "i_mean", "j_mean", "spread", "entropy"]:
			flat[key] = matrix.get(key)

		flat_rows.append(flat)

	df = pd.DataFrame(flat_rows)
	return df


def add_summary_row(df: pd.DataFrame) -> pd.DataFrame:
	"""Add a summary row: combine file names and average matrix stats."""
	summary = {col: None for col in df.columns}

	# Combine filenames
	for col in df.columns:
		if col.endswith("_name"):
			combined = df[col].dropna().astype(str).tolist()
			summary[col] = ",".join(f'"{name}"' for name in combined)

	# Label the first name column
	first_name_col = next((c for c in df.columns if c.endswith("_name")), None)
	if first_name_col:
		summary[first_name_col] = "TOTAL → " + str(summary[first_name_col])

	# Average numeric matrix stats
	matrix_cols = ["m", "n", "N", "density", "row_var", "col_var", "i_mean", "j_mean", "spread", "entropy"]
	for col in matrix_cols:
		if col in df.columns:
			summary[col] = df[col].mean(skipna=True)

	df = pd.concat([df, pd.DataFrame([summary])], ignore_index=True)
	return df


def main():
	timestamp = datetime.now().strftime("%d%m%Y%H%M%S")

	parser = argparse.ArgumentParser(description="Batch-run generateur.py")
	parser.add_argument("n", type=int, help="Number of runs")
	parser.add_argument("--xlsx", default="generated_files", help="Excel output filename")
	parser.add_argument("--nodes", type=int, default=20, help="Number of nodes")
	parser.add_argument("--grid", type=int, default=10, help="Grid size")
	args = parser.parse_args()

	n = args.n
	nodes = args.nodes
	grid = args.grid

	if nodes == 20:
		file_name = "class_a"
	elif nodes == 40:
		file_name = "class_b"
	elif nodes == 50:
		file_name = "class_c"
	elif nodes == 60:
		file_name = "class_d"
	else:
		file_name = "file"

	excel_name = f"../generated_files_db/{file_name}_{timestamp}.xlsx"

	runs = []
	for i in range(n):
		print(f"Run {i+1}/{n}…", end="", flush=True)
		try:
			result = run_generateur_once(nodes, grid)
			runs.append(result)
			print(f" captured {len(result['files'])} file(s).")
		except subprocess.CalledProcessError as exc:
			print("\nError running generateur.py:\n", exc.stderr)
			raise SystemExit(1)
		time.sleep(0.5)

	df = flatten_runs(runs)
	df = add_summary_row(df)

	excel_path = Path(excel_name).expanduser().resolve()
	excel_path.parent.mkdir(parents=True, exist_ok=True)
	df.to_excel(excel_path, index=False)
	print(f"Saved results to {excel_path}")


if __name__ == "__main__":
	main()
