#!/usr/bin/env python3
"""
verify_components.py

Usage:
	python verify_components.py gt-09102025155202 gt-09102025155202_27092025090257

Checks that the union of the component DOT files in a folder
is equivalent to the original DOT graph.

Dependencies:
	pip install networkx pydot
"""

import argparse
import networkx as nx
import sys
import os
import glob

def read_dot(path):
	"""Read DOT into a NetworkX graph (Multi(Di)Graph)."""
	try:
		return nx.drawing.nx_pydot.read_dot(path)
	except Exception as e:
		print(f"Error reading {path}: {e}", file=sys.stderr)
		sys.exit(1)

def combine_graphs(graphs):
	"""Union of multiple NetworkX graphs (same type)."""
	if not graphs:
		raise ValueError("No component graphs provided")
	base = graphs[0].__class__()  # preserve directedness and multigraph
	for g in graphs:
		base.add_nodes_from(g.nodes(data=True))
		base.add_edges_from(g.edges(data=True))
	return base

def normalize_edges(g):
	"""Return a sorted list of edges with attributes (ignores insertion order)."""
	return sorted([(u, v, frozenset(d.items())) for u, v, d in g.edges(data=True)])

def normalize_nodes(g):
	"""Return a sorted list of nodes with attributes."""
	return sorted([(n, frozenset(d.items())) for n, d in g.nodes(data=True)])

def equivalent(g1, g2):
	"""Check if two graphs are equivalent in nodes and edges (with attributes)."""
	if g1.is_directed() != g2.is_directed():
		return False, "Directedness differs"
	if normalize_nodes(g1) != normalize_nodes(g2):
		return False, "Nodes or attributes differ"
	if normalize_edges(g1) != normalize_edges(g2):
		return False, "Edges or attributes differ"
	return True, "Graphs are equivalent"



def main():
	parser = argparse.ArgumentParser(description="Verify component DOT files reconstruct the original DOT graph")
	parser.add_argument("original", help="Original DOT file")
	parser.add_argument("components_dir", help="Directory containing component DOT files")
	args = parser.parse_args()

	components_folder= f"/home/etud/Bureau/projet/fichiers/csp/dat/{args.components_dir}"
	original_file= f"/home/etud/Bureau/projet/fichiers/csp/dat/{args.original}.dot"


	if not os.path.isdir(components_folder):
		print(f"Error: '{components_folder}' is not a directory", file=sys.stderr)
		sys.exit(1)

	# Load graphs
	G_orig = read_dot(original_file)

	comp_files = sorted(glob.glob(os.path.join(components_folder, "*.dot")))
	if not comp_files:
		print(f"Error: no .dot files found in '{components_folder}'", file=sys.stderr)
		sys.exit(1)

	comps = [read_dot(f) for f in comp_files]
	G_combined = combine_graphs(comps)

	ok, msg = equivalent(G_orig, G_combined)
	if ok:
		print("✅ Verification passed: components reconstruct the original graph.")
	else:
		print("❌ Verification failed:", msg)
		print(f"Original: {len(G_orig.nodes())} nodes, {len(G_orig.edges())} edges")
		print(f"Combined: {len(G_combined.nodes())} nodes, {len(G_combined.edges())} edges")

if __name__ == "__main__":
	main()
