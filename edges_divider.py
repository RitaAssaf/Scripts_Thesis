import re
import sys

def parse_graph(file_path):
	with open(file_path, "r") as f:
		content = f.read()

	# Regex to match edges: e.g. 0 -> 1 [label="h", ...];
	edge_pattern = re.compile(r'(\w+)\s*->\s*(\w+)\s*\[.*label\s*=\s*"(h|v)".*?\]')
	
	h_edges = []
	v_edges = []

	for match in edge_pattern.finditer(content):
		src, dst, label = match.groups()
		edge = (src, dst)
		if label == "h":
			h_edges.append(edge)
		elif label == "v":
			v_edges.append(edge)

	return h_edges, v_edges


if __name__ == "__main__":
	# if len(sys.argv) != 2:
	# 	print("Usage: python parse_graph.py <graph_file.dot>")
	# 	sys.exit(1)

	# graph_file = sys.argv[1]
	graph_file= f"/home/etud/Bureau/projet/fichiers/csp/dat/gt-09102025155202_27092025090257/gt-09102025155202_1.dot"

	h_edges, v_edges = parse_graph(graph_file)

	print("Horizontal edges (h):", h_edges)
	print("Vertical edges (v):", v_edges)
