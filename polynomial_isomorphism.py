import networkx as nx
from pathlib import Path
import pydot
import argparse
import os


#python polynomial_isomorphism.py  --pattern pan_apositions-09212025143931 --target apositions-09202025095858

def load(instance, graph, id, node_dict={}):
	"""
	Load graph attributes from a DOT-loaded NetworkX graph into instance.
	"""
	edges = graph.edges
	labels = nx.get_node_attributes(graph, 'label')
	types = nx.get_node_attributes(graph, 'type')
	preceds = nx.get_node_attributes(graph, 'preceds')
	cards = nx.get_node_attributes(graph, 'card')
	realnames = nx.get_node_attributes(graph, 'realname')

	# Create a mapping of node labels to indices
	label_to_index = {label: int(node) for node, label in labels.items()}

	# Build preced_t list of lists based on preceds attribute
	preced_t = []
	for i in range(len(labels)):
		node_name = str(i)
		if node_name in preceds:
			preced_indices = [
				label_to_index[succ] for succ in preceds[node_name].split(',') if succ
			]
			preced_t.append(preced_indices)
		else:
			preced_t.append([])

	instance[f'preced_t_{id}'] = preced_t

	# Set instance data
	instance[f'NV_{id}'] = graph.number_of_nodes()
	instance[f'NE_{id}'] = graph.number_of_edges()
	instance[f'V{id}'] = [name for name in labels.values()]
	instance[f'type{id}'] = [t for t in types.values()]
	instance[f'E{id}'] = [(int(u), int(v)) for u, v, *rest in graph.edges(data=True)]

	instance[f'A{id}'] = []
	instance[f'realnames{id}'] = [name for name in realnames.values()]
	instance[f'card{id}'] = [int(c) for c in cards.values()]


# -------- Directed Square Subgraph Isomorphism -------- #

def find_square_isomorphisms_digraph(graph: nx.DiGraph, side: int = 1):
	"""
	Find all directed square cycles (axis-aligned) in a directed grid-like graph.

	Parameters
	----------
	graph : nx.DiGraph
		Directed graph loaded from DOT, assumed to represent a grid graph.
		Nodes must have integer coordinates as attributes 'x','y'
		(or encodable from labels as 'x_y').
	side : int
		Side length in edges (1 = unit square).

	Returns
	-------
	List[List[str]]
		Each match is a list of node indices [n00, n10, n11, n01] in cycle order.
	"""
	# Extract coordinates
	coords = {}
	for n, data in graph.nodes(data=True):
		if 'x' in data and 'y' in data:
			coords[n] = (int(data['x']), int(data['y']))
		else:
			lbl = data.get('label', str(n))
			if "_" in lbl:
				x, y = lbl.split("_")
				coords[n] = (int(x), int(y))

	if not coords:
		raise ValueError("Graph nodes must have 'x','y' attributes or labels like 'x_y'.")

	pos_to_node = {xy: n for n, xy in coords.items()}
	matches = []

	for (x, y), n00 in pos_to_node.items():
		# Candidate corners
		corners = {
			"n00": (x, y),
			"n10": (x + side, y),
			"n11": (x + side, y + side),
			"n01": (x, y + side),
		}
		if all(c in pos_to_node for c in corners.values()):
			n10 = pos_to_node[corners["n10"]]
			n11 = pos_to_node[corners["n11"]]
			n01 = pos_to_node[corners["n01"]]

			# Directed cycle edges: n00->n10->n11->n01->n00
			if (graph.has_edge(n00, n10)
				and graph.has_edge(n01, n11)
				and graph.has_edge(n00, n01)
				and graph.has_edge(n10, n11)):
				matches.append([n00, n10, n11, n01])

	return matches



def find_grid_pattern_isomorphisms(target: nx.DiGraph, pattern: nx.DiGraph):
	
	# --- 1. Extract coordinates
	def extract_coords(G):
		coords = {}
		for n, data in G.nodes(data=True):
			if 'x' in data and 'y' in data:
				coords[n] = (int(data['x']), int(data['y']))
			else:
				lbl = data.get('label', str(n))
				if "_" in lbl:
					try:
						x, y = map(int, lbl.split("_"))
						coords[n] = (x, y)
					except ValueError:
						continue
		return coords
	
	coords_target = extract_coords(target)
	coords_pattern = extract_coords(pattern)

	if not coords_target or not coords_pattern:
		raise ValueError("Both graphs must have 'x','y' attributes or labels like 'x_y'.")

	# --- 2. Normalize pattern coordinates (make bottom-left = (0,0))
	min_px = min(x for x, y in coords_pattern.values())
	min_py = min(y for x, y in coords_pattern.values())
	norm_pattern = {p: (x - min_px, y - min_py) for p, (x, y) in coords_pattern.items()}

	# get the corner index pat0 in the pattern if its coords after normalization are 0,0
	anchor_pat = [p for p, (px, py) in norm_pattern.items() if (px, py) == (0, 0)]
	if not anchor_pat:
		return []
	pat0 = anchor_pat[0]

	matches = []
	for t, (tx, ty) in coords_target.items():
		

		# try to put the corner node on each node in the graph

		mapping = {pat0: t}
		ok = True
		#check for other pattern nodes if they have an equivalent node in the target graph
		#if we search for a square and put 0,0 on t(6,4) then we will search for (6+1,4),(6,4+1) and (6+1,4+1) 
		for p, (px, py) in norm_pattern.items():
			if p == pat0:
				continue
			candidate_coord = (tx + px, ty + py)
			# Does this coordinate exist in target?
			if candidate_coord not in {v: k for k, v in coords_target.items()}:
				ok = False
				break
			target_node = [k for k, v in coords_target.items() if v == candidate_coord][0]
			mapping[p] = target_node

		if not ok:
			continue

		# --- 4. Check edge consistency
		consistent = True
		for u, v in pattern.edges():
			if not target.has_edge(mapping[u], mapping[v]):
				consistent = False
				break

		if consistent:
			matches.append(mapping)

	return matches


def find_squares_any_step(graph: nx.DiGraph):
	"""
	Find all directed square cycles in a directed grid-like graph.
	Works even if the step is not exactly 1 (arbitrary width/height).
	
	Parameters
	----------
	graph : nx.DiGraph
		Directed graph with 'x','y' attributes or labels like "x_y".
	
	Returns
	-------
	List[List[str]]
		Each match is a list of node ids [n00, n10, n11, n01] in cycle order.
	"""
	# --- Extract coordinates
	coords = {}
	for n, data in graph.nodes(data=True):
		if 'x' in data and 'y' in data:
			coords[n] = (int(data['x']), int(data['y']))
		else:
			lbl = data.get('label', str(n))
			if "_" in lbl:
				try:
					x, y = map(int, lbl.split("_"))
					coords[n] = (x, y)
				except ValueError:
					continue

	if not coords:
		raise ValueError("Graph nodes must have 'x','y' attributes or labels like 'x_y'.")

	# Make reverse lookup
	pos_to_node = {xy: n for n, xy in coords.items()}
	matches = []

	# --- Try all possible pairs horizontally aligned
	for (x1, y1), n00 in pos_to_node.items():
		for (x2, y2), n10 in pos_to_node.items():
			if y1 != y2 or x2 <= x1:
				continue  # must share same y and x2 > x1

			width = x2 - x1

			# look for corresponding top nodes
			top_y = y1 + width  # can be any step, not just 1

			if (x1, top_y) in pos_to_node and (x2, top_y) in pos_to_node:
				n01 = pos_to_node[(x1, top_y)]
				n11 = pos_to_node[(x2, top_y)]

				# Check directed cycle edges
				if (graph.has_edge(n00, n10)
					and graph.has_edge(n00, n01)
					and graph.has_edge(n01, n11)
					and graph.has_edge(n10, n11)):
					matches.append([n00, n10, n11, n01])

	return matches


def find_rectangles_any_step(graph: nx.DiGraph):
	"""
	Find all directed rectangle cycles in a directed grid-like graph.
	Works for arbitrary width/height (not just squares).
	
	Parameters
	----------
	graph : nx.DiGraph
		Directed graph with 'x','y' attributes or labels like "x_y".
	
	Returns
	-------
	List[List[str]]
		Each match is a list of node ids [n00, n10, n11, n01] in cycle order.
	"""
	# --- Extract coordinates
	coords = {}
	for n, data in graph.nodes(data=True):
		if 'x' in data and 'y' in data:
			coords[n] = (int(data['x']), int(data['y']))
		else:
			lbl = data.get('label', str(n))
			if "_" in lbl:
				try:
					x, y = map(int, lbl.split("_"))
					coords[n] = (x, y)
				except ValueError:
					continue

	if not coords:
		raise ValueError("Graph nodes must have 'x','y' attributes or labels like 'x_y'.")

	# Make reverse lookup
	pos_to_node = {xy: n for n, xy in coords.items()}
	matches = []

	# --- Try all possible bottom edges (same y, different x)
	for (x1, y1), n00 in pos_to_node.items():
		for (x2, y2), n10 in pos_to_node.items():
			if y1 != y2 or x2 <= x1:
				continue  # must share same y and x2 > x1

			# --- Try all possible heights
			for (xx, yy), _ in pos_to_node.items():
				if xx != x1 or yy <= y1:
					continue
				height = yy - y1
				top_y = y1 + height

				# check existence of top corners
				if (x1, top_y) in pos_to_node and (x2, top_y) in pos_to_node:
					n01 = pos_to_node[(x1, top_y)]
					n11 = pos_to_node[(x2, top_y)]

					# Check directed cycle edges
					if (graph.has_edge(n00, n10)  # bottom
						and graph.has_edge(n00, n01)  # left
						and graph.has_edge(n10, n11)  # right
						and graph.has_edge(n01, n11)):  # top
						matches.append([n00, n10, n11, n01])

	return matches





def find_grid_pattern_isomorphisms_any_step(target: nx.DiGraph, pattern: nx.DiGraph):
	"""
	Find subgraph isomorphisms of 'pattern' inside 'target',
	allowing arbitrary step size (scaling of the pattern grid).
	"""

	# --- 1. Extract coordinates
	def extract_coords(G):
		coords = {}
		for n, data in G.nodes(data=True):
			if 'x' in data and 'y' in data:
				coords[n] = (int(data['x']), int(data['y']))
			else:
				lbl = data.get('label', str(n))
				if "_" in lbl:
					try:
						x, y = map(int, lbl.split("_"))
						coords[n] = (x, y)
					except ValueError:
						continue
		return coords

	coords_target = extract_coords(target)
	coords_pattern = extract_coords(pattern)

	if not coords_target or not coords_pattern:
		raise ValueError("Both graphs must have 'x','y' attributes or labels like 'x_y'.")

	# --- 2. Normalize pattern coordinates (make bottom-left = (0,0))
	min_px = min(x for x, y in coords_pattern.values())
	min_py = min(y for x, y in coords_pattern.values())
	norm_pattern = {p: (x - min_px, y - min_py) for p, (x, y) in coords_pattern.items()}

	# get anchor pattern node (at (0,0))
	anchor_pat = [p for p, (px, py) in norm_pattern.items() if (px, py) == (0, 0)]
	if not anchor_pat:
		return []
	pat0 = anchor_pat[0]

	pos_to_node = {xy: n for n, xy in coords_target.items()}
	matches = []

	# --- 3. Try every possible placement and scaling factor
	for t, (tx, ty) in coords_target.items():
		mapping = {pat0: t}
		ok = True

			

		for p, (px, py) in norm_pattern.items():
			if p == pat0:
				continue
			for scale in range(1, 20):
				candidate_coord = (tx + px * scale, ty + py * scale)
				if candidate_coord not in pos_to_node:
					ok = False
					break
				mapping[p] = pos_to_node[candidate_coord]

		if not ok:
			continue

		# --- 4. Check edge consistency
		consistent = True
		for u, v in pattern.edges():
			if not target.has_edge(mapping[u], mapping[v]):
				consistent = False
				break

		if consistent:
			matches.append(mapping)

	return matches




def find_grid_pattern_isomorphisms_any_step_1(target: nx.DiGraph, pattern: nx.DiGraph):
	"""
	Find subgraph isomorphisms of 'pattern' inside 'target',
	allowing arbitrary rectangular scaling (independent step size in x and y).
	"""

	# --- 1. Extract coordinates
	def extract_coords(G):
		coords = {}
		for n, data in G.nodes(data=True):
			if 'x' in data and 'y' in data:
				coords[n] = (int(data['x']), int(data['y']))
			else:
				lbl = data.get('label', str(n))
				if "_" in lbl:
					try:
						x, y = map(int, lbl.split("_"))
						coords[n] = (x, y)
					except ValueError:
						continue
		return coords

	coords_target = extract_coords(target)
	coords_pattern = extract_coords(pattern)

	if not coords_target or not coords_pattern:
		raise ValueError("Both graphs must have 'x','y' attributes or labels like 'x_y'.")

	# --- 2. Normalize pattern coordinates (make bottom-left = (0,0))
	min_px = min(x for x, y in coords_pattern.values())
	min_py = min(y for x, y in coords_pattern.values())
	norm_pattern = {p: (x - min_px, y - min_py) for p, (x, y) in coords_pattern.items()}

	# get anchor pattern node (at (0,0))
	anchor_pat = [p for p, (px, py) in norm_pattern.items() if (px, py) == (0, 0)]
	if not anchor_pat:
		return []
	pat0 = anchor_pat[0]

	pos_to_node = {xy: n for n, xy in coords_target.items()}
	matches = []

	# --- 3. Try every possible placement of the anchor node
	for t, (tx, ty) in coords_target.items():
		# try to infer scaling factors from each other pattern node
		for p_ref, (px_ref, py_ref) in norm_pattern.items():
			if p_ref == pat0:
				continue

			# loop over all possible target nodes to deduce scaling
			for node_ref, (xx, yy) in coords_target.items():
				dx_pat, dy_pat = px_ref, py_ref
				dx_tar, dy_tar = xx - tx, yy - ty

				# skip if both deltas are zero (same as anchor)
				if dx_pat == 0 and dy_pat == 0:
					continue

				# compute scale_x and scale_y
				scale_x = dx_tar / dx_pat if dx_pat != 0 else None
				scale_y = dy_tar / dy_pat if dy_pat != 0 else None

				# reject non-integers or non-positive scales
				if scale_x is not None and (scale_x <= 0 or scale_x != int(scale_x)):
					continue
				if scale_y is not None and (scale_y <= 0 or scale_y != int(scale_y)):
					continue

				scale_x = int(scale_x) if scale_x is not None else 1
				scale_y = int(scale_y) if scale_y is not None else 1

				# --- 4. Try to map the whole pattern with these scales
				mapping = {pat0: t}
				ok = True
				for p, (px, py) in norm_pattern.items():
					if p == pat0:
						continue
					candidate_coord = (tx + px * scale_x, ty + py * scale_y)
					if candidate_coord not in pos_to_node:
						ok = False
						break
					mapping[p] = pos_to_node[candidate_coord]

				if not ok:
					continue

				# --- 5. Check edge consistency
				consistent = True
				for u, v in pattern.edges():
					if not target.has_edge(mapping[u], mapping[v]):
						consistent = False
						break

				if consistent:
					matches.append(mapping)

	# --- 6. Remove duplicates
	unique_matches = []
	seen = set()
	for m in matches:
		key = tuple(sorted(m.items()))
		if key not in seen:
			seen.add(key)
			unique_matches.append(m)

	return unique_matches



# -------- Example usage -------- #

if __name__ == "__main__":
	os.chdir(os.path.dirname(os.path.realpath(__file__)) + '/..')

	#pattern ="square_apositions-09212025140420"
	# pattern= "pan_apositions-09212025143931"
	
	# target= "apositions-09232025154832"
	#target= "net_apositions-09232025154022"
	#target = "apositions-09222025154927"
	parser = argparse.ArgumentParser(description='Process graph matching parameters.')
	parser.add_argument('--pattern', type=str,required=True, help='pattern graph dot file name')

	parser.add_argument('--target', type=str,required=True,  help='target graph dot file name')
	args = parser.parse_args()

	pattern = args.pattern
	target= args.target



	Gp = nx.drawing.nx_agraph.read_dot(f'dat/{pattern}.dot')
	Gt = nx.drawing.nx_agraph.read_dot(f'dat/{target}.dot')
	
	inst = {}
	load(inst, Gt, id=1)

	# squares = find_square_isomorphisms_digraph(Gt, side=1)
	# print("Found directed squares:", squares)

	matches = find_grid_pattern_isomorphisms_any_step_1(Gt,Gp)
	print(f"MATCH_COUNT={len(matches)}")

	# print(f"grid_pattern_isomorphisms Found {len(matches)} {pattern}  ")
	# #for m in matches[:5]:  # just show first 5
	# for m in matches:
	# 	print(m)
	
	# matches = find_grid_pattern_isomorphisms(Gt,Gp)
	# print(f"grid_pattern_isomorphisms Found {len(matches)}  {pattern}  ")
	# for m in matches[:5]:  # just show first 5
	# 	print(m)


	#matches= find_rectangles_any_step(Gt)
	
 
 
 
	# print(f"find_rectangles Found {len(matches)} rect of P ")
	# for m in matches[:5]:  # just show first 5
	# 	print(m)