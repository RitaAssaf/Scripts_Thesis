from enum import Enum, auto
from pycsp3 import *
import os
import sys
import argparse
import pygraphviz as pgv
from pathlib import Path
import inflect
import networkx as nx
import pydot
from collections import Counter
from class_label_order import LabelOrder
from class_node import Node
from ilf import get_label,hopcroft, build_partial_order_3, build_partial_order_4,hopcroft_multiset,dir_ILF
#from digraph import graph_generator

# Load data in model
def load(instance, graph_file, id, node_dict={}):
	
	# Load graph
	graph = nx.drawing.nx_agraph.read_dot(graph_file).to_directed()

	# Plot input graph
	pydot.graph_from_dot_file(graph_file)[0].write_png(f'res/{Path(os.path.basename(graph_file)).stem}.png')

	#print("Parsed nodes:", graph.nodes(data=True))

	#edges = graph.edges
	edges = [(u, v, d['angle']) for u, v, d in graph.edges(data=True) if 'angle' in d]
	labels = nx.get_node_attributes(graph, 'label')
	angles = nx.get_edge_attributes(graph, 'angle')
	graphs = pydot.graph_from_dot_file(graph_file)
	pydot_graph = graphs[0]
	nodes = pydot_graph.get_nodes()
	#print("Total nodes in PyDot:", len(nodes))
	#print("Node labels:", labels)

	# Set instance data
	instance[f'NV_{id}'] = graph.number_of_nodes()
	instance[f'NE_{id}'] = graph.number_of_edges()
	instance[f'V{id}'] = [label for label in labels.values()]
	instance[f'E{id}'] = list()
	instance[f'A{id}'] = list()
	instance['dom']=node_dict
	for n1, n2, a in edges:
		instance[f'E{id}'].append((int(n1), int(n2)))
		key = (n1, n2, 0) if (n1, n2, 0) in angles else (n1, n2)
		instance[f'A{id}'].append('Horizontal' if angles[key] == '0' else 'Vertical')



def process_mapping( instance, mapping_n, mapping, target,pattern):

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

def domain_n(i):
	return [5,6] if i==1 or i==2 else range(10)
	#return node_dict[f'{i+1}p']
def model(

	# =============== DATA
	
	dom: list[str],
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
	#I = VarArray(size=NV_1, dom=domain_n)
	T = {( i , j ) for i , j in E2 } | {( j , i ) for i , j in E2 }

	# =============== CONSTRAINT

	satisfy(

		AllDifferent(I),

		# preserving edges
		[( I [ i ] , I [ j ]) in T for (i , j ) in E1 ] ,

		[
		#((disjunction(I[n1] == node_dict[f'{n1+1}p'][i % len(node_dict[f'{n1+1}p'])])for i in range(len(node_dict[f'{n1+1}p'])) )for n1 in range(NV_1))
		#((I[n1] in node_dict[f'{n1+1}p'])for n1 in range(NV_1))

		]
	)
	for i in range(NV_1):
		print(I[i].dom)
	print(posted())
	return I





if __name__ == '__main__':

	#pattern='dipan'
	#pattern='corner'
	# target='graph'
	pattern='wellFormed'
	target='net'
	#target='diNet'
	#target='target010220251109'
	#pattern='diWellFormed'
	solver = ACE
	# Go to parent directory
	os.chdir(os.path.dirname(os.path.realpath(__file__)) + '/..')

	# Create a solving instance of the model
	instance = dict()


	Gp = nx.drawing.nx_agraph.read_dot(f'dat/{pattern}.dot')
	Gt = nx.drawing.nx_agraph.read_dot(f'dat/{target}.dot')
	Gp = nx.relabel_nodes(Gp, {node: f"{node}p" for node in Gp.nodes()})
	
	#node_list = dir_ILF(Gp,Gt)
	#node_list = dir_ILF(Gp,Gt)
	#node_dict = {node._name: node._domain for node in node_list if node._ispattern}
	#node_dict = {node._name: [int(value) for value in node._domain] for node in node_list if node._ispattern}

	# Load data to the instance
	load(instance, f'dat/{pattern}.dot', 1)
	load(instance, f'dat/{target}.dot', 2)

	I = model(**instance)

	result = solve(sols=ALL)

	num_solutions = n_solutions() or 0  # Default to 0 if None

	if num_solutions > 0:
		print(f'Patterns {pattern} in  {target}:')
		for solution_i in range(n_solutions()):
			process_mapping( instance, solution_i + 1, values(I, sol=solution_i),target,pattern)
	else:
		print('No solutions found :(') 