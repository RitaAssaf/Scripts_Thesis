import networkx as nx
import psutil
import os
import sys
import time

MEMORY_LIMIT_MB = 500  # Set a memory limit in MB

def read_graph_from_file(filename):
	G = nx.Graph()

	with open(filename, "r") as f:
		lines = f.readlines()

	# Number of nodes (not strictly needed)
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

		# Check memory after adding each node
		if is_memory_exceeded():
			full_memo()
			sys.exit("Memory limit exceeded. Execution stopped.")

	# Second pass: add edges
	for idx, line in enumerate(lines[1:]):
		parts = line.strip().split(";")
		neighbors_str = parts[0].strip()

		if neighbors_str:
			neighbors = neighbors_str.split()
			for n_idx in neighbors:
				G.add_edge(idx, int(n_idx))

		# Check memory after adding each edge
		if is_memory_exceeded():
			full_memo()
			sys.exit("Memory limit exceeded. Execution stopped.")

	return G


def is_memory_exceeded():
	process = psutil.Process(os.getpid())
	mem_mb = process.memory_info().rss / (1024 * 1024)
	return mem_mb > MEMORY_LIMIT_MB

def full_memo():
	process = psutil.Process(os.getpid())
	mem_info = process.memory_info()
	print("\n=== FULL MEMORY REPORT ===")
	print(f"RSS (Resident Set Size): {mem_info.rss / (1024 * 1024):.2f} MB")
	print(f"VMS (Virtual Memory Size): {mem_info.vms / (1024 * 1024):.2f} MB")
	print(f"Shared: {mem_info.shared / (1024 * 1024):.2f} MB")
	print(f"Text: {mem_info.text / (1024 * 1024):.2f} MB")
	print(f"Lib: {mem_info.lib / (1024 * 1024):.2f} MB")
	print(f"Data: {mem_info.data / (1024 * 1024):.2f} MB")
	print(f"Dirty: {mem_info.dirty / (1024 * 1024):.2f} MB")
	print("==========================\n")


if __name__ == '__main__':
	# filename = "../lcres/glc_card_01072026152040.txt"  # Big instance
	filename="../lcres/glc_card_01072026140535.txt" #small instance

	print(f"Loading graph from {filename}...")
	G = read_graph_from_file(filename)
	print("Graph loaded successfully!")
	print(G.nodes[0])
	print(list(G.neighbors(0)))
