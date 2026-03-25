from enum import Enum, auto
from pycsp3 import *
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
def process_mapping( instance, mapping_n, mapping, target,pattern):

	# Print mapping variables in this model (and so, no generated file)
	print(f'{mapping_n}.\t[{", ".join(instance["V1"])}] -> [{", ".join(list(map(lambda i: instance["V2"][i-1], mapping)))}]')

	# Plot mapping
	graph = pydot.graph_from_dot_file(f'dat/{target}.dot')[0]
	for v1 in range(instance['NV_1']):
		graph.get_node(str(mapping[v1]))[0].set_label(instance['V1'][v1])
		graph.get_node(str(mapping[v1]))[0].set_style('filled')
	graph.write_png(f'res/{pattern}_in_{target}_{mapping_n}.png')


# Angle of the edge of a graph
class Angle(str, Enum):
	Horizontal = 'Horizontal'
	Vertical = 'Vertical'

def model(

	# =============== DATA
	
	# Pattern graph G1 = (V1, E1), with |V1| = NV_1, |E1| = NV_1, and A1 the angle of each edges in E1
	NV_1: int, 
	NE_1: int, 
	V1: list[str],
	E1: list[list[int]],
	A1: list[Angle],

	# Target graph G2 = (V2, E2), with |V2| = NV_2, |E2| = NV_2, and A2 the angle of each edges in E2
	NV_2: int, 
	NE_2: int, 
	V2: list[str],
	E2: list[list[int]],
	A2: list[Angle]
):

	# =============== VARIABLE

	# Mapping nodes from graph 1 to graph 2
	I = VarArray(size=NV_1, dom=range(1, NV_2 + 1))
 
	T = {( i , j ) for i , j in E2 } | {( j , i ) for i , j in E2 }

	# =============== CONSTRAINT

	satisfy(

		# Map all nodes from graph 1
		AllDifferent(I),

		
		[
			Exist(
					(I[E1[e1][0]] == E2[e2][p]) & (I[E1[e1][1]] == E2[e2][(p+ 1) % 2]) #p=1 ou 0
				for e2 in range(NE_2) for p in range(2) if A1[e1]==A2[e2]
			) for e1 in range(NE_1)
		]
	)

	#print(posted())
	return I

if __name__ == '__main__':
	#pattern='wellFormed'
	pattern='pan'
	target='targetLargeNum'
	solver = ACE
	# Go to parent directory
	os.chdir(os.path.dirname(os.path.realpath(__file__)) + '/..')

	# Create a solving instance of the model
	instance = dict()

	# Load data to the instance
	load(instance, f'dat/{pattern}.dot', 1)
	load(instance, f'dat/{target}.dot', 2)


	I = model(**instance)

	# Solve the instance
	result = solve(sols=ALL)

	num_solutions = n_solutions() or 0  # Default to 0 if None

	if num_solutions > 0:
		print(f'Patterns {pattern} in  {target}:')
		for solution_i in range(n_solutions()):
			process_mapping( instance, solution_i + 1, values(I, sol=solution_i),target,pattern)
	else:
		print('No solutions found :(')