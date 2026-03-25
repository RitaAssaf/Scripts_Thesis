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
import psutil
import threading
import time
from datetime import datetime
from collections import Counter
from class_label_order import LabelOrder

from datetime import datetime 
from ilf import run_with_timeout,get_label,hopcroft, build_partial_order_3, build_partial_order_4,hopcroft_multiset,dir_ILF, ILF
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
	realnames= nx.get_node_attributes(graph, 'realname')
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

	instance[f'card{id}'] = [int(c) for c in cards.values()]
	for n1, n2 in edges:
		instance[f'E{id}'].append((int(n1), int(n2)))
	instance[f'A{id}'] = list()
	instance[f'realnames{id}'] = [name for name in realnames.values()]



def import_to_excel(solver_output):
	# Step 1: Clean ANSI escape sequences
	ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')
	clean_output = ansi_escape.sub('', solver_output)

	# Step 2: Extract metrics with individual fallback regexes
	effs_matches = re.findall(r'effs\s*:\s*(\d+)', clean_output)
	effs = effs_matches[-1] if effs_matches else "-"

	stop_match = re.search(r'stop\s*:\s*([A-Z_]+)', clean_output)
	stop = stop_match.group(1) if stop_match else "-"

	wck_matches = re.findall(r'wck\s*:\s*(\d+\.\d+)', clean_output)
	wck = wck_matches[-1] if wck_matches else "-"

	cpu_match = re.search(r'cpu\s*:\s*(\d+\.\d+)', clean_output)
	cpu = cpu_match.group(1) if cpu_match else "-"

	mem_match = re.search(r'mem\s*:\s*(\S+)', clean_output)
	mem = mem_match.group(1) if mem_match else "-"

	unsat_match = re.search(r'\bs\s+UNSATISFIABLE\b', clean_output)
	unsat = "Yes" if unsat_match else "No"

	wrong_dec_match = re.search(r'd\s+WRONG\s+DECISIONS\s+(\d+)', clean_output)
	wrong_dec = wrong_dec_match.group(1) if wrong_dec_match else "-"

	found_sols_match = re.search(r'd\s+FOUND\s+SOLUTIONS\s+(\d+)', clean_output)
	found_sols = found_sols_match.group(1) if found_sols_match else "-"

	complete_match = re.search(r'd\s+COMPLETE\s+EXPLORATION', clean_output)
	complete = "Yes" if complete_match else "No"

	# Step 3: Create Excel workbook
	wb = openpyxl.Workbook()
	ws = wb.active
	ws.title = "Indicators"

	headers = [
		"Pattern", "Target", "ILF", "Order", "Typing", "Card", "Run",
		"Dpts", "Effs", "Fails", "Wrgs", "Wck", "Ngds", "Sols",
		"Stop", "CPU", "Mem", "UNSAT", "WrongDec", "FoundSols", "Complete",
		"ilftime", "ilfmemo"
	]
	ws.append(headers)

	# Step 4: Prepare and append row
	run_count = 1
	row = [
		pattern, target, ilf, ordre, typage, card,
		f"run{run_count}",  # Run ID
		"-",                # Dpts (not extracted by fallback)
		effs,
		"-",                # Fails (not extracted by fallback)
		wrong_dec,          # Wrgs (using wrong decisions)
		wck,
		"-",                # Ngds (not extracted by fallback)
		found_sols,
		stop,
		cpu,
		mem,
		unsat,
		wrong_dec,
		found_sols,
		complete,
		time_used,
		mem_used
	]
	ws.append(row)

	# Step 5: Save Excel file
	try:
		timestamp = datetime.now().strftime("%d%m%Y%H%M%S")
		file_name = os.path.join(output_folder, f"indicators_{pattern}_{target}_{timestamp}.xlsx")
		wb.save(file_name)
		print(f"Data has been written to {file_name}")
	except Exception as e:
		print(f"Error saving file: {e}")


def get_node_label(G, label):
	#return [n for n, d in G.nodes(data=True) if d.get("label") == "Person"][0]
	return {n.get_name(): n for n in G.get_nodes()}[label] #graphiz file


def process_mapping( instance, mapping_n, mapping, target,pattern):

	print(f'{mapping_n}.\t[{", ".join(instance["V1"])}] -> [{", ".join(list(map(lambda i: instance["realnames2"][i], mapping)))}]')

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


#Function model takes as parameter nodes,edges and retrun var array
#builds the model but returns only I

def model(

	# =============== DATA
	
	# Pattern graph G1 = (V1, E1), with |V1| = NV_1, |E1| = NV_1, and A1 the angle of each edges in E1
	NV_1: int, 
	NE_1: int, 
	V1: list[str],
	E1: list[list[int]],
	A1: list[Angle],
	type1:list[str],
	preced_t_1:list[list[int]],
	
	# Target graph G2 = (V2, E2), with |V2| = NV_2, |E2| = NV_2, and A2 the angle of each edges in E2
	NV_2: int, 
	NE_2: int, 
	V2: list[str],
	E2: list[list[int]],
	A2: list[Angle],
	type2:list[str],
	preced_t_2:list[list[int]],
	card1=[],
	card2=[],
	realnames1=[],
	realnames2=[]
):


	# =============== VARIABLE


	I = VarArray(size=NV_1, dom=lambda i: domain_n(i, NV_2))

	if card:
		cardinality_p= VarArray(size= NV_1, dom=range(15))
		cardinality_t=VarArray(size= NV_2, dom=range(15))
	
	T = {( i , j ) for i , j in E2 } | {( j , i ) for i , j in E2 }

	# =============== CONSTRAINT
	satisfy(

		AllDifferent(I),

		[( I [ i ] , I [ j ]) in T for (i , j ) in E1 ] ,

	)
	
	if ordre : 
		satisfy (
			[( I [ i ] , I [ j ]) in pairs_t for (i , j ) in pairs_p ] 
		)

	if card :
		satisfy (
			[cardinality_p[n] == card_p[n] for n in range(NV_1)], 
			[cardinality_t[n] == card_t[n] for n in range(NV_2)],
			[cardinality_t[I[i]] == cardinality_p[i] for i in range(NV_1)]
		)
	# for i in range(NV_1):
	# 	print(I[i].dom)
	#print(posted())
	return I


MEMORY_KILLED = False

def monitor_and_kill(pid, threshold_gb=21, interval=5):
	"""Monitor process (and children) memory and kill if exceeds threshold."""
	global MEMORY_KILLED
	try:
		parent = psutil.Process(pid)
		while parent.is_running():
			# Sum memory for parent + children
			mem_used_gb = parent.memory_info().rss / (1024 ** 3)
			for child in parent.children(recursive=True):
				mem_used_gb += child.memory_info().rss / (1024 ** 3)

			if mem_used_gb > threshold_gb:
				MEMORY_KILLED = True
				print(f"[WARNING] Memory exceeded {threshold_gb} GB ({mem_used_gb:.4f} GB). Killing process...")
				with open("memory_log.txt", "a") as log_file:
					log_file.write(f"[{datetime.now()}] Killed process due to memory limit ({mem_used_gb:.4f} GB)\n")

				# Kill children first
				for child in parent.children(recursive=True):
					try:
						child.terminate()
					except psutil.NoSuchProcess:
						pass
				parent.terminate()
				try:
					parent.wait(timeout=5)
				except psutil.TimeoutExpired:
					parent.kill()
				break

			time.sleep(interval)
	except psutil.NoSuchProcess:
		pass




if __name__ == '__main__':

	parser = argparse.ArgumentParser(description='Process graph matching parameters.')
	parser.add_argument('--pattern', type=str, required=True, help='Name of the pattern file (without .dot extension)')
	parser.add_argument('--target', type=str, required=True, help='Name of the target file (without .dot extension)')
	parser.add_argument('--ilf', action='store_true', help='Enable ILF option')
	parser.add_argument('--ordre', action='store_true', help='Enable order option')
	parser.add_argument('--typage', action='store_true', help='Enable typing option')
	parser.add_argument('--card', action='store_true', help='Enable typing option')
	parser.add_argument("--output", type=str, required=True) 
	parser.add_argument('--timeout', action='store_true', help='Enable timeout 120 option')
	args = parser.parse_args()

	pattern = args.pattern
	target = args.target
	ilf = args.ilf
	ordre = args.ordre
	typage = args.typage
	card= args.card
	enable_timeout= args.timeout
	output_folder= args.output
	time_used=0
	mem_used=0
	
	
	# ilf_reached_timeout= False
	# pattern='pan'
	# target='panp1_lctr-06082025165701'
	# ilf = False
	# ordre = True
	# typage = True
	# card= True
	# enable_timeout= True
	#output_folder= "/home/etud/Bureau/projet/indicators_lines_cols/"
	

	timestamp = datetime.now().strftime("%d%m%Y%H%M%S")

	solver = ACE
	# Go to parent directory
	os.chdir(os.path.dirname(os.path.realpath(__file__)) + '/..')

	# Create a solving instance of the model
	instance = dict()


	Gp = nx.drawing.nx_agraph.read_dot(f'lcres/{pattern}.dot')
	Gt = nx.drawing.nx_agraph.read_dot(f'lcres/{target}.dot')
	Gp = nx.relabel_nodes(Gp, {node: f"{node}p" for node in Gp.nodes()})
	ilf_reached_timeout= False
	if ilf:
		node_dict,  time_used, mem_used = run_with_timeout(10800 , ILF, Gp, Gt) #timeout 3 hrs
		if node_dict is None:
				ilf_reached_timeout= True
	else:
		node_dict = {}


	if ilf_reached_timeout:
		print("ilf_reached_timeout")
		import_to_excel('stop: ILF_TIMEOUT') #fills Stop header with ILF_TIMEOUT
	else:
		# Load data to the instance
		load(instance, f'lcres/{pattern}.dot', 1)
		load(instance, f'lcres/{target}.dot', 2)

		# p={0:{1},2:{3},1:{},3:{}}
		# t={3:{0,1,2},0:{1,2},1:{2},5:{7,6,4},7:{6,4},6:{4},4:{},2:{}}
		
		if card: 
			card_p= cp_array(instance['card1'])
			card_t= cp_array(instance['card2'])

		preced_p_graph=instance['preced_t_1']
		preced_t_graph=instance['preced_t_2']

		

		pairs_p = [(i, elem) for i, sublist in enumerate(preced_p_graph) for elem in sublist]
		pairs_t = [(i, elem) for i, sublist in enumerate(preced_t_graph) for elem in sublist]


		# Check if required keys exist in instance before calling model()
		required_keys = [
			"NV_1", "NE_1", "V1", "E1", "A1", "type1", "preced_t_1",
			"NV_2", "NE_2", "V2", "E2", "A2", "type2", "preced_t_2"
		]

		for key in required_keys:
			if key not in instance:
				print(f"Missing key in instance: {key}")


		I = model(**instance)


		timeout = 3600

		options = f"-t={timeout}s -s=all -trace -ev"

		#result = solve(sols=ALL, verbose=2)
		
		# if(enable_timeout):
		# 	result = solve(solver="ACE", options=options)
		# else:
		# 	result = solve(sols=ALL)
		ace_jar_path = "/home/etud/Bureau/projet/lib/python3.11/site-packages/pycsp3/solvers/ace/ACE-2.3.jar"


		if os.path.exists("lc5.xml"):
			command = ["java", "-jar", ace_jar_path, "lc5.xml", "-s=all",   f"-t={timeout}s","-trace", "-ev"]
			try:
				process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
				TEST_MODE = False  # Set to False for real run
				MEMORY_LIMIT_GB = 0.001 if TEST_MODE else 0.022

				monitor_thread = threading.Thread(target=monitor_and_kill, args=(process.pid, MEMORY_LIMIT_GB), daemon=True)
				monitor_thread.start()

				stdout, stderr = process.communicate(timeout=timeout)


				# make sure the monitor thread exits cleanly before moving on
				# monitor_thread.join(timeout=1)

				solver_output = stdout
				print("Solver Output:")
				print(solver_output)

				if process.returncode != 0:
					print("Solver exited with error:", process.returncode)

					if MEMORY_KILLED:
						import_to_excel('stop: ACE_MEM_LIMIT')
					elif stderr and "OutOfMemoryError" in stderr:
						print("JVM Out Of Memory.")
					else:
						import_to_excel(f'stop: ACE_ERROR_{process.returncode}')
				else:
					import_to_excel(solver_output)

					print("ACE completed successfully.")

			except subprocess.TimeoutExpired:
				print(f"ACE process timed out after {timeout} seconds.")
				import_to_excel('stop: ACE_TIMEOUT')

			except Exception as e:
				print(f"Error occurred: {e}")
				import_to_excel('stop: ACE_MEM_LIMIT')

		else:
			print("Error: lc5.xml file not generated. Check your model definition.")
		
