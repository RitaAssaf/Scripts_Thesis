#!/usr/bin/env python3
"""
python components_divider_1.py gt-09102025155202

Splits a DOT graph into weakly/connected components.
Each component is renumbered 0..n-1 and written explicitly with:
	id [label="id"];
	{ rank=same; ... };
	edges with attributes
"""

import argparse
import os
import sys
import networkx as nx
from datetime import datetime

def read_dot_file(path):
	"""Read DOT file into a NetworkX graph using pydot."""
	try:
		G = nx.drawing.nx_pydot.read_dot(path)
	except Exception as e:
		raise RuntimeError(f"Failed to read DOT file '{path}': {e}")
	return G

def split_components(G):
	"""Return list of node sets for each component."""
	if G.is_directed():
		comps = list(nx.weakly_connected_components(G))
	else:
		comps = list(nx.connected_components(G))
	comps.sort(key=lambda s: -len(s))
	return comps

def write_component_explicit(sub, out_path, directed=True):
	"""Write a subgraph in explicit DOT format."""
	with open(out_path, "w") as f:
		graph_type = "digraph" if directed else "graph"
		edge_op = "->" if directed else "--"
		f.write(f"{graph_type} G {{\n")

		# Add nodes with label
		for n in sorted(sub.nodes()):
			f.write(f'    {n} [label="{n}"];\n')

		f.write("\n")

		# Add edges with attributes
		for u, v, attrs in sub.edges(data=True):
			attr_str = ""
			if attrs:
				clean_pairs = []
				for k, val in attrs.items():
					# Remove extra quotes if present
					v_clean = str(val).strip('"')
					clean_pairs.append(f'{k}="{v_clean}"')
				attr_str = " [" + ", ".join(clean_pairs) + "]"
			f.write(f"    {u} {edge_op} {v}{attr_str};\n")

		f.write("}\n")



def renumber_subgraph(G_sub):
	"""
	Relabel nodes of a subgraph from 0..n-1.
	"""
	mapping = {old: str(new) for new, old in enumerate(G_sub.nodes())}
	return nx.relabel_nodes(G_sub, mapping, copy=True)

def main():
	timestamp = datetime.now().strftime("%d%m%Y%H%M%S")

	parser = argparse.ArgumentParser(description="Split DOT graph into renumbered explicit component DOT files.")
	parser.add_argument("input", help="Input DOT file name (without .dot extension)")
	parser.add_argument("-v", "--verbose", action="store_true", help="Verbose messages")
	args = parser.parse_args()

	input_graph_path = f"/home/etud/Bureau/projet/fichiers/csp/dat/{args.input}.dot"
	output_folder = f"/home/etud/Bureau/projet/fichiers/csp/dat/{args.input}"
	#output_folder = f"/home/etud/Bureau/projet/fichiers/csp/dat/gt-09102025155202_27092025171614"

   
	os.makedirs(output_folder, exist_ok=True)

	if not os.path.isfile(input_graph_path):
		print(f"Error: input file '{input_graph_path}' not found.", file=sys.stderr)
		sys.exit(2)

	if args.verbose:
		print(f"Reading '{input_graph_path}' ...")

	G = read_dot_file(input_graph_path)
	comps = split_components(G)

	if args.verbose:
		print(f"Found {len(comps)} components.")

	written = []
	for idx, nodes in enumerate(comps, start=1):
		sub = G.subgraph(nodes).copy()
		sub = renumber_subgraph(sub)
		filename = f"{args.input}_{idx}.dot"
		out_path = os.path.join(output_folder, filename)
		write_component_explicit(sub, out_path, directed=G.is_directed())
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
