import networkx as nx

def read_graph_from_file(filename):
	G = nx.Graph()

	with open(filename, "r") as f:
		lines = f.readlines()

	# Number of nodes (not strictly needed, but kept for clarity)
	n = int(lines[0].strip())

	# First pass: create nodes with attributes
	for idx, line in enumerate(lines[1:]):
		parts = line.strip().split(";")

		neighbors_str = parts[0].strip()
		card = parts[1].strip()
		node_type = parts[2].strip()
		preceds_str = parts[3].strip()
		realname = parts[4].strip()

		preceds = preceds_str.split() if preceds_str else []

		G.add_node(
			idx,
			card=card,
			type=node_type,
			realname=realname,
			preceds=preceds
		)

	# Second pass: add edges
	for idx, line in enumerate(lines[1:]):
		parts = line.strip().split(";")
		neighbors_str = parts[0].strip()

		if neighbors_str:
			neighbors = neighbors_str.split()
			for n_idx in neighbors:
				G.add_edge(idx, int(n_idx))

	return G


if __name__ == '__main__':
	#G = read_graph_from_file("../lcres/glc_card_01072026152040.txt") #big instance
	G = read_graph_from_file("../lcres/glc_card_01082026092042.txt") #1000 nodes success
	#G = read_graph_from_file("../lcres/glc_card_01072026140535.txt") #small instance
	G = read_graph_from_file("../lcres/glc_card_01082026154806.txt")
	print(G.nodes[0])
	print(list(G.neighbors(0)))