from enum import Enum, auto
from pycsp3 import *
import subprocess
import os
import sys
import argparse
import pygraphviz as pgv
from pathlib import Path
import inflect
import networkx as nx
import pydot
import re
import openpyxl
import subprocess
import random
from collections import Counter
from class_label_order import LabelOrder

from datetime import datetime 
from ilf import get_label,hopcroft, build_partial_order_3, build_partial_order_4,hopcroft_multiset,dir_ILF, ILF
from itertools import combinations

def load(instance, graph_file, id, node_dict={}):

	# Load graph
	graph = nx.drawing.nx_agraph.read_dot(graph_file)

	# Plot input graph
	pydot.graph_from_dot_file(graph_file)[0].write_png(f'res/{Path(os.path.basename(graph_file)).stem}.png')

	edges = graph.edges  # if multiedgeview add strict to graphiz
	lenedges = len(edges)
	labels = nx.get_node_attributes(graph, 'label')
	types = nx.get_node_attributes(graph, 'type')
	preceds = nx.get_node_attributes(graph, 'preceds')  # Extract preceds attribute
	cards = nx.get_node_attributes(graph, 'card')

	graphs = pydot.graph_from_dot_file(graph_file)
	pydot_graph = graphs[0]

	# Create a mapping of node labels to indices
	label_to_index = {label: int(node) for node, label in labels.items()}

	# Build preced_t list of lists based on preceds attribute
	preced_t = []
	for i in range(len(labels)):
		node_name = str(i)
		if node_name in preceds:
			# Convert preceds node labels to their corresponding indices
			preced_indices = [label_to_index[succ] for succ in preceds[node_name].split(',') if succ]
			preced_t.append(preced_indices)
		else:
			preced_t.append([])  # No preceds for this node


	instance[f'preced_t_{id}'] = preced_t  # Save to instance for later use

	# Set instance data
	instance[f'NV_{id}'] = graph.number_of_nodes()
	instance[f'NE_{id}'] = graph.number_of_edges()
	instance[f'V{id}'] = [name for name in labels.values()]
	instance[f'type{id}'] = [type for type in types.values()]
	instance[f'E{id}'] = list()
	#instance[f'card{id}'] = [c for c in cards.values()]
	instance[f'card{id}'] = [int(c) for c in cards.values()]
	for n1, n2 in edges:
		instance[f'E{id}'].append((int(n1), int(n2)))
	instance[f'A{id}'] = list()




def get_node_label(G, label):
	#return [n for n, d in G.nodes(data=True) if d.get("label") == "Person"][0]
	return {n.get_name(): n for n in G.get_nodes()}[label] #graphiz file


def process_mapping( instance, mapping_n, mapping, target,pattern):

	print(f'{mapping_n}.\t[{", ".join(instance["V1"])}] -> [{", ".join(list(map(lambda i: instance["V2"][i], mapping)))}]')

	# Plot mapping
	graph = pydot.graph_from_dot_file(f'lcres/{target}.dot')[0]
	for v1 in range(instance['NV_1']):#
		# prend le label du noeud target qui est dans l'array V2 a l'indice solution trouvé par le solveur
		#donc le solveur retourne array des indices des noeuds de la solution 
		node=instance['V2'][mapping[v1]] 
		get_node_label(graph, node).set_label(instance['V1'][v1])
		#graph.get_node(node)[0].set_label(instance['V1'][v1])
		get_node_label(graph, node).set_style('filled')
		graph.write_png(f'res/{pattern}_in_{target}_{mapping_n}.png')


# Angle of the edge of a graph
class Angle(str, Enum):
	Horizontal = 'Horizontal'
	Vertical = 'Vertical'

def domain_n(i, NV_2):
	
	indices_l= [i for i, type in enumerate(instance['type2'] ) if type == 'l']

	indices_c= [i for i, type in enumerate(instance['type2'] ) if type == 'c']
	#si le type du noeud patterne est l donc il aura les indices(qui sont les noms aussi) des noeuds l
	
	if not ilf and not typage:	
		return range(NV_2 )
	elif not ilf and typage:	
		if instance['type1'][i]== 'l':
			return indices_l
		else: return indices_c
	elif ilf and not typage:	
		return node_dict[f'{i}p']
	elif ilf and typage:
		ilf_domain= node_dict[f'{i}p']
		if instance['type1'][i]== 'l':
			return list(set(ilf_domain) & set(indices_l))
		else: return list(set(ilf_domain) & set(indices_c))
	

def dom_preced(i: int, j: int, target):
	if target:
		if 0 <= i < len(preced_t_graph) and 0 <= j < len(preced_t_graph[i]):
			return [preced_t_graph[i][j]] 
		return [-1] 
	else:
		if 0 <= i < len(preced_p_graph) and 0 <= j < len(preced_p_graph[i]):
			return [preced_p_graph[i][j]] 
		return [-1] 

def fill_matrix(lst_of_lsts,length):
	
	result = [sublist + [-1] * (length - len(sublist)) for sublist in lst_of_lsts]  # Fill shorter lists with -1
	
	return result


def random_graph_matching(pattern_graph, target_graph, node_pairs):

	pattern_nodes = list(pattern_graph.nodes()) if hasattr(pattern_graph, 'nodes') else list(pattern_graph.keys())
	target_nodes = list(target_graph.nodes()) if hasattr(target_graph, 'nodes') else list(target_graph.keys())

	if len(target_nodes) < len(pattern_nodes):
		raise ValueError("Target graph must have at least as many nodes as the pattern graph.")

	# Randomly sample unique target nodes
	selected_target_nodes = random.sample(target_nodes, len(pattern_nodes))

	# Pair pattern nodes with random target nodes
	matched_pairs = list(zip(pattern_nodes, selected_target_nodes))

	return matched_pairs

if __name__ == '__main__':

	pattern='pan'
	target = 'aalc-19032025124934'
	ilf = True
	ordre = True
	typage = True
	card= True

	# Go to parent directory
	os.chdir(os.path.dirname(os.path.realpath(__file__)) + '/..')

	# Initial pairs (could be empty or placeholders)
	initial_pairs = [(0, 1), (1, 2), (2, 3)]
	Gp = nx.drawing.nx_agraph.read_dot(f'lcres/{pattern}.dot')
	Gt = nx.drawing.nx_agraph.read_dot(f'lcres/{target}.dot')
	Gp = nx.relabel_nodes(Gp, {node: f"{node}p" for node in Gp.nodes()})
	
	

	# Perform random matching
	result = random_graph_matching(Gp, Gt, initial_pairs)

	print("Random matching result:", result)

