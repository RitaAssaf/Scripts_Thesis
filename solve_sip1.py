import os
import sys
import argparse
from pathlib import Path

import networkx as nx
import pydot

# Load data in model
def load(instance, graph_file, id):
	
	# Load graph
	graph = nx.drawing.nx_agraph.read_dot(graph_file)

	# Plot input graph
	pydot.graph_from_dot_file(graph_file)[0].write_png(f'res/{Path(os.path.basename(graph_file)).stem}.png')

	# Get graph edges and labels
	edges = graph.edges
	labels = nx.get_node_attributes(graph, 'label')
	angles = nx.get_edge_attributes(graph, 'angle')

	# Set instance data
	instance[f'NV_{id}'] = graph.number_of_nodes()
	instance[f'NE_{id}'] = graph.number_of_edges()
	instance[f'V{id}'] = [label for label in labels.values()]
	instance[f'E{id}'] = list()
	instance[f'A{id}'] = list()
	for n1, n2 in edges:
		instance[f'E{id}'].append((int(n1), int(n2)))
		instance[f'A{id}'].append('Horizontal' if angles[n1, n2] == '0' else 'Vertical')

# Print solution and generate related graph
def process_mapping(modler, instance, mapping_n, mapping):

	# Print mapping variables in this model (and so, no generated file)
	print(f'{mapping_n}.\t[{", ".join(instance["V1"])}] -> [{", ".join(list(map(lambda i: instance["V2"][i-1], mapping)))}]')

	# Plot mapping
	graph = pydot.graph_from_dot_file(f'dat/{args.target}.dot')[0]
	for v1 in range(instance['NV_1']):
		graph.get_node(str(mapping[v1]))[0].set_label(instance['V1'][v1])
		graph.get_node(str(mapping[v1]))[0].set_style('filled')
	graph.write_png(f'res/{modler}_{args.pattern}_in_{args.target}_{mapping_n}.png')

if __name__ == '__main__':

	# Parse command line arguments
	parser = argparse.ArgumentParser()
	parser.add_argument('-p', '--pattern', type=str, default='pan', help='Pattern graph')
	parser.add_argument('-t', '--target', type=str, default='net', help='Target graph')
	parser.add_argument('-a', '--all', action=argparse.BooleanOptionalAction, default=False, help='Get all solutions')
	parser.add_argument('-m', '--modler', type=str, default='mzn', help='Choose the modler')
	args = parser.parse_args()

	# Go to parent directory
	os.chdir(os.path.dirname(os.path.realpath(__file__)) + '/..')

	# Use the given modler
	match args.modler:

		case 'pycsp3':

			from pycsp3 import *
			import sip
			# Use ACE solver
			solver = ACE

			# Create a solving instance of the model
			instance = dict()

			# Load data to the instance
			load(instance, f'dat/{args.pattern}.dot', 1)
			load(instance, f'dat/{args.target}.dot', 2)

			
			I = sip.model(**instance)

			# Solve the instance
			result = solve(sols=ALL if args.all else 1)


			if n_solutions() > 0:
				print(f'Patterns {args.pattern} in target {args.target}:')
				for solution_i in range(n_solutions()):
					process_mapping(args.modler, instance, solution_i + 1, values(I, sol=solution_i))

		case _:
			raise SystemExit('Error: Unknown modler')
	
	print()
