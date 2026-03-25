#!/usr/bin/env python3
"""
split_dot_components.py

Usage:
	python components_divider.py gt-09102025155202
	python split_dot_components.py apositions-08252025091216.dot -o comp -p output_dir --prefix comp

This script:
 - reads a graph in DOT format
 - finds weakly connected components (if the graph is directed) or
   connected components (if undirected)
 - writes each component to a separate .dot file with attributes preserved

graph.dot → input DOT file

-o output_dir → place the result files in output_dir (created if missing)

-p comp → prefix for output files (comp_1.dot, comp_2.dot, …)

--numbered → use underscore numbering (comp_1.dot, comp_2.dot, …)

-v → verbose messages while running

Dependencies:
	pip install networkx pydot
(If you prefer, Graphviz is not strictly required for this script, but pydot
may need it for some installations.)
"""

import argparse
import os
import sys
import networkx as nx
from datetime import datetime
import time
import openpyxl

def read_dot_file(path):
	"""Read DOT file into a NetworkX graph using pydot interface."""
	try:
		# This uses networkx's pydot wrapper. It returns a MultiGraph/MultiDiGraph
		G = nx.drawing.nx_pydot.read_dot(path)
	except Exception as e:
		raise RuntimeError(f"Failed to read DOT file '{path}': {e}")
	# nx_pydot.read_dot sometimes returns strings 'True'/'False' etc for attrs;
	# we will keep attributes as-is (GraphViz attributes are strings normally).
	return G

def write_subgraph_dot(G_sub, out_path):
	"""
	Write a NetworkX graph to DOT using nx.nx_pydot.to_pydot,
	then saving the pydot object to file so attributes are preserved.
	"""
	try:
		p = nx.drawing.nx_pydot.to_pydot(G_sub)
		p.write_raw(out_path)
	except Exception as e:
		raise RuntimeError(f"Failed to write DOT to '{out_path}': {e}")

def split_components(G):
	"""Return list of lists of nodes for each component.
	   For directed graphs: use weakly connected components.
	   For undirected graphs: use connected components.
	"""
	if G.is_directed():
		comps = list(nx.weakly_connected_components(G))
	else:
		comps = list(nx.connected_components(G))
	# sort components by size descending for convenience (optional)
	comps.sort(key=lambda s: -len(s))
	return comps

def main():
	timestamp = datetime.now().strftime("%d%m%Y%H%M%S")
	parser = argparse.ArgumentParser(description="Split a DOT graph into component DOT files.")
	parser.add_argument("input", help="Input DOT file path")
	parser.add_argument("-d", "--outdir", default=".", help="Output directory (default: current dir)")
	parser.add_argument("-p", "--prefix", default="component", help="Output file prefix (default: 'component')")
	parser.add_argument("-n", "--numbered", action="store_true",
						help="Use numeric suffixes (component_1.dot). Default is component_{idx}.dot")
	parser.add_argument("--keep-isolated", action="store_true",
						help="Also write isolated single-node components (default: write them too anyway)")
	parser.add_argument("-v", "--verbose", action="store_true", help="Verbose progress messages")
	args = parser.parse_args()

	input_graph_path= f"/home/etud/Bureau/projet/fichiers/csp/dat/{args.input}.dot"

	output_folder = f"/home/etud/Bureau/projet/fichiers/csp/dat/{args.input}_{timestamp}"
	os.makedirs(output_folder, exist_ok=True)
	prefix = args.input

	if not os.path.isfile(input_graph_path):
		print(f"Error: input file '{args.input}' not found.", file=sys.stderr)
		sys.exit(2)
	os.makedirs(args.outdir, exist_ok=True)

	if args.verbose:
		print(f"Reading '{args.input}' ...")
	G = read_dot_file(input_graph_path)

	comps = split_components(G)
	if args.verbose:
		print(f"Found {len(comps)} components.")

	written = []
	for idx, nodes in enumerate(comps, start=1):
		if not args.keep_isolated and len(nodes) == 0:
			continue
		# induced subgraph and copy to make it independent
		sub = G.subgraph(nodes).copy()
		# Preserve whether graph is directed or not by creating same type container and
		# transferring graph-level attributes (nx_pydot.to_pydot reads graph attributes from the graph object)
		# However sub already is of same type (subgraph of DiGraph is DiGraph with same directed-ness)
		# Build filename
		filename = f"{prefix}_{idx}.dot" 
		out_path = os.path.join(output_folder, filename)
		write_subgraph_dot(sub, out_path)
		written.append(out_path)
		if args.verbose:
			print(f"Wrote component {idx}: {len(nodes)} nodes -> {out_path}")

	if args.verbose:
		print("Done.")
	else:
		for p in written:
			print(p)

if __name__ == "__main__":
	main()
