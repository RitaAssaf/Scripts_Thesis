import networkx as nx
import matplotlib.pyplot as plt
import inflect
import os
from collections import Counter
from class_label_order import LabelOrder
from class_node import Node
import multiprocessing
import traceback

import time
import psutil
import resource
import sys

# Optional: Only works on Unix (Linux/macOS)
try:
	
	def limit_memory(max_mb=500):
		"""Set a memory limit on the current process (in MB)."""
		soft, hard = resource.getrlimit(resource.RLIMIT_AS)
		resource.setrlimit(resource.RLIMIT_AS, (max_mb * 1024 * 1024, hard))
except ImportError:
	def limit_memory(max_mb):
		pass 


def _target(queue, func, args, kwargs, memory_limit_mb=None):
	try:
		# Optional memory limit (Linux/macOS)
		if memory_limit_mb:
			
			resource.setrlimit(resource.RLIMIT_AS, (memory_limit_mb * 1024 * 1024, resource.RLIM_INFINITY))

		result, iterations = func(*args, **kwargs)
		if result is None:  
			# dir_ILF returned None → domain failure
			queue.put(("fail", None, iterations))
		else:
			queue.put(("success", result, iterations))
	except Exception:
		queue.put(("error", traceback.format_exc(),0))


def run_with_timeout(timeout, func, *args, memory_limit_mb=None, **kwargs):
	queue = multiprocessing.Queue()
	process = multiprocessing.Process(target=_target, args=(queue, func, args, kwargs, memory_limit_mb))
	process.start()

	proc_ps = psutil.Process(process.pid)
	start_time = time.perf_counter()
	peak_memory = 0

	try:
		while process.is_alive():
			try:
				mem = proc_ps.memory_info().rss / (1024 * 1024)  # in MB
				peak_memory = max(peak_memory, mem)
			except psutil.NoSuchProcess:
				break  # Process ended quickly

			time.sleep(0.1)
			if time.perf_counter() - start_time > timeout:
				print(f"Function '{func.__name__}' timed out after {timeout} seconds. Terminating...")
				process.terminate()
				process.join()
				return "TIMEOUT", None, timeout, peak_memory

		process.join()

		if not queue.empty():
			status, result, iterations = queue.get()
			exec_time = time.perf_counter() - start_time
			
			if status == "success":
				print(f"Function completed in {exec_time:.2f} seconds using {peak_memory:.2f} MB memory.")
				return result, iterations, exec_time, peak_memory

			elif status == "fail":   # domain empty returned from dir_ILF
				print("ILF exited early due to empty domain.")
				return None, iterations, exec_time, peak_memory
			else:
				print("Function raised an exception:")
				print(result)
				return "Error",None, exec_time, peak_memory

		if process.exitcode != 0:
			print(f"Function '{func.__name__}' crashed or was killed (possibly out-of-memory).")
		else:
			print("Function exited without returning a result.")

		return "Error",None, time.perf_counter() - start_time, peak_memory

	except Exception as e:
		print("Unexpected error during monitoring:", str(e))
		process.terminate()
		return None,None, None, None



def eccentricity(G, start_node):
	return  nx.eccentricity(G, start_node)

def distancek(G, start_node, k):
	# A dictionary where the keys are the nodes and the values 
	# are the lengths of the shortest path from the source
	#  node to each node. For e in Gt instance 1, a:3, j:4
	lengths = nx.single_source_shortest_path_length(G, start_node)
	# Count nodes that have a path length less than k
	count = sum(1 for length in lengths.values() if 0 < length < k)
	return count

def get_num_cliques(G, node):
	cliques_per_node = nx.number_of_cliques(G)
	return cliques_per_node[node]

def count_node_cycles(G, node):
	cycles = nx.cycle_basis(G)
	a=0
	return sum(1 for cycle in cycles if node in cycle)

def get_label(graph, node, alpha, dir=False):
	if dir:
		return str(graph.in_degree(node)) +'_'+ str(graph.out_degree(node))
	else:

		if alpha == "degree":
			return graph.degree(node)
		elif alpha== "distance":
			return distancek(graph, node,2) #k=2
		elif alpha== "eccentricity":
			return eccentricity(graph,node)
		elif alpha== "num_cliques":
			return get_num_cliques(graph,node)
		elif alpha== "cycle":
			return count_node_cycles(graph,node)

def hopcroft(m, m_prime, dir=False):
	# Create a bipartite graph
	B = nx.Graph()
	
	# Add nodes for each element in m and m'
	left_nodes = ['m_' + str(i) for i in range(len(m))]
	right_nodes = ['m_prime_' + str(j) for j in range(len(m_prime))]
	
	B.add_nodes_from(left_nodes, bipartite=0)  # Left set (m)
	B.add_nodes_from(right_nodes, bipartite=1)  # Right set (m_prime)
	
	if dir:
		# Add edges based on the partial order (a_i <= b_j)
		for i, a_i in enumerate(m):
			for j, b_j in enumerate(m_prime):
				if label_less_than(a_i , b_j):
					B.add_edge('m_' + str(i), 'm_prime_' + str(j))
	else:
		# Add edges based on the partial order (a_i <= b_j)
		for i, a_i in enumerate(m):
			for j, b_j in enumerate(m_prime):
				if int(a_i) <= (b_j):
					B.add_edge('m_' + str(i), 'm_prime_' + str(j))
	
	# Run Hopcroft-Karp algorithm to find maximum matching, specifying top_nodes
	matching = nx.bipartite.maximum_matching(B, top_nodes=left_nodes)
	
	# Check if matching covers all elements of m (left set)
	matched_left = [node for node in matching if node in left_nodes]
	
	# If all elements of m are matched, return True (m <= m')
	return len(matched_left) == len(m)



#	print(f"does m_1 preceds m_4?: {oneprecedstwo('m_1', 'm_4', ordered_labels)}")

def oneprecedstwo(m, m_prime, ordered_labels):
	# Find label and label_prime in a single loop
	label, label_prime = None, None
	for x in ordered_labels:
		if x._name == m:
			label = x
		if x._name == m_prime:
			label_prime = x
		# Stop early if both are found
		if label and label_prime:
			break
	
	# Check if either label or label_prime is None
	if label is None or label_prime is None:
		print(f"label '{m}' or '{m_prime}' not found in ordered_labels")
		return False

	# Ensure `_preceds` is iterable and check for label_prime in it
	if not isinstance(label._preceds, list):
		print(f"Warning: _preceds attribute for '{label._name}' is not a list.")
		return False

	# Check if label_prime's name is in label's preceds list
	result = label_prime._name in label._preceds
   # print(f"Checking if '{label_prime._name}' is in '{label._name}'._preceds: {result}")
   # print(f"prime: {label_prime} and label: {label}")
	return result


def hopcroft_multiset(m, m_prime, ordered_labels):
	#print(f"does 'm_5', 'm_5' preceds m_3', 'm_4?: {hopcroft_multiset(['m_5', 'm_5'],['m_4'], ordered_labels)}")

	# Create a bipartite graph
	B = nx.Graph()
	
	# Add nodes for each element in m and m'
	left_nodes = ['m_' + str(i) for i in range(len(m))]
	right_nodes = ['m_prime_' + str(j) for j in range(len(m_prime))]
	
	B.add_nodes_from(left_nodes, bipartite=0)  # Left set (m)
	B.add_nodes_from(right_nodes, bipartite=1)  # Right set (m_prime)
	
	# Add edges based on the partial order (a_i <= b_j)
	for i, a_i in enumerate(m):
		for j, b_j in enumerate(m_prime):
			if oneprecedstwo( a_i, b_j, ordered_labels):
				B.add_edge('m_' + str(i), 'm_prime_' + str(j))
	
	# Run Hopcroft-Karp algorithm to find maximum matching, specifying top_nodes
	matching = nx.bipartite.maximum_matching(B, top_nodes=left_nodes)
	
	# Check if matching covers all elements of m (left set)
	matched_left = [node for node in matching if node in left_nodes]
	
	# If all elements of m are matched, return True (m <= m')
	return len(matched_left) == len(m)



def build_partial_order_3(nodes, dir=False):
	partial_order = {}
	order_labels = []
	label_letter='a'
	if dir:
		j=1
		for node_a in nodes:
		
			exist= False
			if len( order_labels)==0:
				order_labels.append(LabelOrder(label_letter+'_' + str(j), node_a._label, [], [node_a._name],[], node_a._predecessors, node_a._successors ))
				j=j+1
				# for label_i in order_labels:
				# 		if label_less_than(label_i._label ,order_labels[-1]._label ) and hopcroft(label_i._predecessors , order_labels[-1]._predecessors,dir)  and hopcroft(label_i._successors , order_labels[-1]._successors,dir):
				# 			label_i._preceds.append(order_labels[-1]._name )
			else:
				for label_k in order_labels:
					if label_k._label== node_a._label and Counter(node_a._predecessors) == Counter(label_k._predecessors) and Counter(node_a._successors) == Counter(label_k._successors): #Counter(list1) This checks whether both lists have the same elements with the same frequency, regardless of the order.            
						exist= True  
						# un noeud a un label qui existe déjà 
						label_k.add_node(node_a._name)         
						break
				
				if exist == False:
					order_labels.append(LabelOrder(label_letter+'_' + str(j), node_a._label, [], [node_a._name],[], node_a._predecessors, node_a._successors ))
					j=j+1
					# for label_i in order_labels:
					# 	if label_less_than(label_i._label ,order_labels[-1]._label ) and hopcroft(label_i._predecessors , order_labels[-1]._predecessors, dir)  and hopcroft(label_i._successors , order_labels[-1]._successors,dir):
					# 		label_i._preceds.append(order_labels[-1]._name )
		for label_i in order_labels:
			for label_j in order_labels:
				if label_less_than(label_i._label ,label_j._label ) and hopcroft(label_i._predecessors , label_j._predecessors, dir)  and hopcroft(label_i._successors , label_j._successors,dir):
					if label_j._name not in label_i._preceds:
						label_i._preceds.append(label_j._name )
	
	else:

		j=1
		for node_a in nodes:
		
			exist= False
			if len( order_labels)==0:
				order_labels.append(LabelOrder(label_letter+'_' + str(j), node_a._label, [], [node_a._name],[], node_a._predecessors, node_a._successors ))
				j=j+1
				#comparer l'élt qu'on vient d'ajouter avec les labels de la liste 
				# dans ce cas len=0 l'elt label m1 sera ajouté à preceds de lui même
				# for label_i in order_labels:
				# 	# comparaison qui dépend de degré comment comparer m1 m2
				# 		if int(label_i._label) <= int(order_labels[-1]._label) and hopcroft(label_i._neighbors_labels , order_labels[-1]._neighbors_labels, dir):
				# 			label_i._preceds.append(order_labels[-1]._name )
			else:
				for label_k in order_labels:
					if label_k._label== node_a._label and Counter(node_a._neighbors_labels) == Counter(label_k._neighbors_labels): #Counter(list1) This checks whether both lists have the same elements with the same frequency, regardless of the order.            
						exist= True  
						# un noeud a un label qui existe déjà 
						label_k.add_node(node_a._name)         
						break
				
				if exist == False:
					order_labels.append(LabelOrder(label_letter+'_' + str(j), node_a._label, node_a._neighbors_labels, [node_a._name],[] ))
					j=j+1
					# for label_i in order_labels:
					# 	if int(label_i._label) <= int(order_labels[-1]._label) and hopcroft(label_i._neighbors_labels , order_labels[-1]._neighbors_labels, dir):
					# 		label_i._preceds.append(order_labels[-1]._name )
		for label_i in order_labels:
			for label_j in order_labels:
				if int(label_i._label) <= int(label_j._label) and hopcroft(label_i._neighbors_labels , label_j._neighbors_labels, dir):
					if label_j._name not in label_i._preceds:
						label_i._preceds.append(label_j._name )
			
	return  order_labels

#LabelOrder(self, name, label, neighbors_labels, nodes, preceds):
#Node(self,name, label, neighbors_labels, domain, ispattern)


def next_label(label):
	if not label:
		return 'a'
	
	label = list(label)
	i = len(label) - 1
	
	while i >= 0 and label[i] == 'z':
		label[i] = 'a'
		i -= 1
	
	if i < 0:
		label = ['a'] + label
	else:
		label[i] = chr(ord(label[i]) + 1)
	
	return ''.join(label)




def build_partial_order_4(nodes, ordered_labels, dir=False):
	partial_order = {}
	new_order_labels = []
	
	j=1
	label_letter= ordered_labels[0]._name.split('_')[0]
	#label_letter=chr(ord(label_letter) + 1)
	label_letter = next_label(label_letter)

	
	if dir:
		for node_a in nodes:
	
			label_label_ajouté= node_a._label
			
			exist= False
			if len( new_order_labels)==0:
				new_order_labels.append(LabelOrder(label_letter +'_'+ str(j), node_a._label, [], [node_a._name],[], node_a._predecessors, node_a._successors ))
				
				j=j+1
				
				#Suppose we have n1= m1.{m1,m1} and want to add n2=m2.{m3}, n1<n2
				# check m1< m2 i.e. m2 in m1.preceds and hopcroft multiset ({m1, m1}, {m3})
				for label_i in new_order_labels: 
		
					objet_label_label_boucle=[x for x in ordered_labels if x._name == label_i._label][0] # get m1 from the old ordered labels
			else:
				for label_k in new_order_labels:
					if label_k._label== node_a._label and Counter(node_a._predecessors) == Counter(label_k._predecessors) and Counter(node_a._successors) == Counter(label_k._successors):#Counter(list1) This checks whether both lists have the same elements with the same frequency, regardless of the order.            

					#if label_k._label== node_a._label and Counter(node_a._neighbors_labels) == Counter(label_k._neighbors_labels): #Counter(list1) This checks whether both lists have the same elements with the same frequency, regardless of the order.            
						exist= True  
						# un noeud a un label qui existe déjà 
						label_k.add_node(node_a._name)         
						break
				
				if exist == False:
					new_order_labels.append(LabelOrder(label_letter +'_'+ str(j), node_a._label, [], [node_a._name],[], node_a._predecessors, node_a._successors ))
					j=j+1
					# for label_i in new_order_labels:
					# 	objet_label_label_boucle=[x for x in ordered_labels if x._name == label_i._label][0] 
				
					# 	if  label_label_ajouté in objet_label_label_boucle._preceds and hopcroft_multiset(label_i._predecessors, node_a._predecessors, ordered_labels) and hopcroft_multiset(label_i._successors, node_a._successors, ordered_labels):
					# 		label_i._preceds.append(new_order_labels[-1]._name )
	
		#comparer chaque label l_i avec les labels de la liste pour voir si  l_i preceds l_j
		# for label_i in new_order_labels:#exemple label_i=b2=a1.a4.(a5,a6)
		# 		for label_j in new_order_labels:
		# for label_i in [label for label in new_order_labels if label._name == 'b_5']:
		# 	for label_j in [label for label in new_order_labels if label._name == 'b_36']:
		for label_i in  new_order_labels :
			for label_j in  new_order_labels :
						
			#prendre les attributs du l_i c a d prendre l'objet a1 de b2
					objet_label_boucle=[x for x in ordered_labels if x._name == label_i._label][0] 
					#si  le label a14 de l_j est dans la liste des preceds de label a1 du l_i et les multisets l_i sont< à l_j selon l'ancien ordre (a5,a6)< (a7,a8) 
					if  label_j._label in objet_label_boucle._preceds and hopcroft_multiset(label_i._predecessors, label_j._predecessors, ordered_labels) and hopcroft_multiset(label_i._successors, label_j._successors, ordered_labels):
					#si l_j n'est pas déjà ajoutée
						if label_j._name not in label_i._preceds:
							label_i._preceds.append(label_j._name )

	else:
		for node_a in nodes:
		
			label_label_ajouté= node_a._label
			neighbors_label_ajouté=node_a._neighbors_labels
			exist= False
			if len( new_order_labels)==0:
				new_order_labels.append(LabelOrder(label_letter +'_'+ str(j), node_a._label, node_a._neighbors_labels, [node_a._name],[] ))
				j=j+1
				
				#Suppose we have n1= m1.{m1,m1} and want to add n2=m2.{m3}, n1<n2
				# check m1< m2 i.e. m2 in m1.preceds and hopcroft multiset ({m1, m1}, {m3})
				# for label_i in new_order_labels: 
		
				# 	objet_label_label_boucle=[x for x in ordered_labels if x._name == label_i._label][0] # get m1 from the old ordered labels
				
				# 	if  label_label_ajouté in objet_label_label_boucle._preceds and hopcroft_multiset(label_i._neighbors_labels, neighbors_label_ajouté, ordered_labels):
				# 		label_i._preceds.append(new_order_labels[-1]._name )
			else:
				for label_k in new_order_labels:
					if label_k._label== node_a._label and Counter(node_a._neighbors_labels) == Counter(label_k._neighbors_labels): #Counter(list1) This checks whether both lists have the same elements with the same frequency, regardless of the order.            
						exist= True  
						# un noeud a un label qui existe déjà 
						label_k.add_node(node_a._name)         
						break
				
				if exist == False:
					new_order_labels.append(LabelOrder(label_letter +'_'+ str(j), node_a._label, node_a._neighbors_labels, [node_a._name],[] ))
					j=j+1
					# for label_i in new_order_labels:
					# #on retrouve le label de la liste m déjà construite
					# 	objet_label_label_boucle=[x for x in ordered_labels if x._name == label_i._label][0] 
				
					# 	if  label_label_ajouté in objet_label_label_boucle._preceds and hopcroft_multiset(label_i._neighbors_labels, neighbors_label_ajouté, ordered_labels):
					# 		label_i._preceds.append(new_order_labels[-1]._name )
		for label_i in new_order_labels:  #pour chaque label l_i
			for label_j in new_order_labels: #vérifier si l_i preceds l_j 

				objet_label_boucle=[x for x in ordered_labels if x._name == label_i._label][0] # get m1 from the old ordered labels
				#si le label l_j dans preceds de l_i et hopcroft l_i et l_j
				if  label_j._label in objet_label_boucle._preceds and hopcroft_multiset(label_i._neighbors_labels, label_j._neighbors_labels, ordered_labels):
					if label_j._name not in label_i._preceds:
						label_i._preceds.append(label_j._name )
			
	return  new_order_labels


def ILF(Gp, Gt, posp={}, post={}, instance=[]):
	labeling="degree"
	iterations_ilf=0
	p = inflect.engine()
	#INITIAL DOMAINS##############################################
	print('	#INITIAL DOMAINS##############################################')
	iterations_ilf+=1
	#  def __init__(self,name, label, neighbors_labels, domain, pattern):
	nodes_array = [
	Node(node,"" , [], list(Gt.nodes()), 1) 
	for node in Gp.nodes()
	]
	
	nodes_array.extend([
	Node(node,"", [],[], 0) 
	for node in Gt.nodes()
	])

	
	#etiquetage
	for node in nodes_array:
		if node._ispattern:
			node._label= get_label(Gp, node._name, labeling)

		else:
			node._label= get_label(Gt, node._name, labeling)


	node_dict_name = {node._name: node for node in nodes_array}


	#DOMAIN FILTERING########################################################
	for node in nodes_array:
		for node_j in node._domain:
			if not node._label <= node_dict_name[node_j]._label:
				node._domain.remove(node_j)
	# EARLY EXIT CHECK
		for node in nodes_array:
			if node._ispattern and not node._domain:
				print(f"Node {node._name} has empty domain after {p.ordinal(iterations_ilf)} iteration. Exiting.")
				return None, iterations_ilf
	


	# print('## NODES ARRAY ##############################')
	# for node in nodes_array:
	# 	print(node)

	#FIRST ITERATION##############################################
	
	print('	#1st ITERATION##############################################')
	iterations_ilf+=1

	for node in nodes_array:
		if node._ispattern:
			node._label=get_label(Gp, node._name, labeling)
			node._neighbors_labels=list(get_label(Gp, neighbor, labeling) for neighbor in Gp.neighbors(node._name))
		else:
			node._label=get_label(Gt, node._name,labeling)
			node._neighbors_labels=list(get_label(Gt, neighbor, labeling) for neighbor in Gt.neighbors(node._name))


	ordered_labels= build_partial_order_3(nodes_array, False )
	
	#DOMAIN FILTERING###################################
	for label in ordered_labels:
		nodes_preced=[]
		#prendre les noeuds preceds dans le domaine du label _ispattern
		for label_preced in label._preceds: #m1 < m2,m3,m4
			# prendre m2
			labelpreced= [x for x in ordered_labels if x._name == label_preced ][0] 
			
			#prendre les noeuds qui ont label m2
			for nodepreced in labelpreced._nodes:
				#vérifier que le noeud n'est pas pattern avant de l'ajouter
				if not node_dict_name [nodepreced]._ispattern:
					nodes_preced.append(nodepreced)
			#pour les noeus qui ont ce label ajouter les noeuds preceds au domaine
		for node in label._nodes:
			noeud= node_dict_name [ node]
			noeud._domain=nodes_preced
	
	
		# EARLY EXIT CHECK
		for node in nodes_array:
			if node._ispattern and not node._domain:
				print(f"Node {node._name} has empty domain after {p.ordinal(iterations_ilf)} iteration. Exiting.")
				return None, iterations_ilf
	

	# print('## NODES ARRAY ##############################')
	# for node in nodes_array:
	# 	print(node)

	# print('## LABELS ARRAY ##############################')
	# for label in ordered_labels:
	# 	print(label)

	

	# ITERATIONS LOOP ##############################################
	for i in range(3, 100): #k=100 max iterations
		iterations_ilf+=1
		domains_unchanged= True
		num_labels_unchanged= True

		print(f"	#{p.ordinal(i)} ITERATION  ############################################")
		
		for node in nodes_array:
			node._label=[x for x in ordered_labels if node._name in x._nodes ][0]._name
			
		# Create a lookup dictionary for name-to-node mappings
		node_dict = {node._name: node for node in nodes_array}

		# Update each node's neighbor labels using the dictionary
		for node in nodes_array :
			if node._ispattern:
				node._neighbors_labels=list([node_dict[neighbor]._label for neighbor in Gp.neighbors(node._name) if neighbor in node_dict])
			else:
				node._neighbors_labels=list([node_dict[neighbor]._label for neighbor in Gt.neighbors(node._name) if neighbor in node_dict])
		
		
		
		new_ordered_labels= build_partial_order_4(nodes_array , ordered_labels)
		
		#DOMAIN FILTERING###################################
		#pour chaque label de l'ordre, prendre les labels qui suivent 
		#m1< m2, m3, m4 : prendre  m2, m3, m4  
		#et pour tous les noeuds qui ont lable m1, ajouter les noeuds qui ont label m2 ou m3 ou m4 au domaine de m1
		for label in new_ordered_labels:
			nodes_preced=[]
			#ajouter les noeuds aux domaines
			for label_preced in label._preceds: #m1 < m2,m3,m4

				# prendre m2 en tant qu'objet			
				labelpreced = [x for x in new_ordered_labels if x._name == label_preced] [0]
				
				#prendre les noeuds qui ont label m2
				for nodepreced in labelpreced._nodes:
					#vérifier que le noeud est pattern avant de l'ajouter
					if not node_dict_name [ nodepreced]._ispattern:
						nodes_preced.append(nodepreced)
			
			#pour les noeus patterne qui ont ce label affecter les noeuds preceds au domaine
			for node in label._nodes:
				noeud= node_dict_name [ node]
				if noeud._ispattern:
					# si le domaine d'un noeud est différent des noeuds affectés
					if domains_unchanged and Counter(noeud._domain) != Counter(nodes_preced):
						domains_unchanged=False
					noeud._domain= nodes_preced
		
		
		if len(ordered_labels)!= len(new_ordered_labels):
			num_labels_unchanged=False

		# la prochaine itération on utilise les nouveaux labels n1,n2,.. pour comparer o1=n1.{n} et o2=n2.{n3}
		ordered_labels= new_ordered_labels


		# EARLY EXIT CHECK
		for node in nodes_array:
			if node._ispattern and not node._domain:
				print(f"Node {node._name} has empty domain after {p.ordinal(iterations_ilf)} iteration. Exiting.")
				return None, iterations_ilf


		# print('## NODES ARRAY ##############################')
		# for node in nodes_array:
		# 	print(node)

		# print('## LABELS ARRAY ##############################')
		# for label in new_ordered_labels:
		# 	print(label) 

		if num_labels_unchanged and domains_unchanged:
			print(f"Fixpoint reached at {p.ordinal(i)} iteration for labeling {labeling} on############################################# ")
			break
	

	return  {node._name: [int(value) for value in node._domain] for node in nodes_array if node._ispattern}, iterations_ilf


def label_less_than(label_1, label_2):
	return (int(label_1.split('_')[0]) <= int(label_2.split('_')[0]) and 
					int(label_1.split('_')[1]) <= int(label_2.split('_')[1]))


def dir_ILF(Gp, Gt, posp={}, post={}):
	labeling="degree"
	iterations_ilf=0
	p = inflect.engine()
	#INITIAL DOMAINS##############################################
	print('	#INITIAL DOMAINS##############################################')
	
	#  def __init__(self,name, label, neighbors_labels, domain, pattern):
	nodes_array = [
	Node(node, "", [], list(Gt.nodes()), 1, set(), set())  # Explicitly provide empty sets
	for node in Gp.nodes()
	]

	nodes_array.extend([
	Node(node, "", [], [], 0, set(), set())  # Explicitly provide empty sets
	for node in Gt.nodes()
	])

	node_dict_name = {node._name: node for node in nodes_array}


	#FIRST FILTERING ##############################################
	print('	#FIRST ITeration##############################################')
	iterations_ilf += 1

	
	for node in nodes_array:
		if node._ispattern:
			node._label= get_label(Gp, node._name, labeling,True)

		else:
			node._label= get_label(Gt, node._name, labeling,True)


	#DOMAIN FILTERING############
	for node in nodes_array:
		for node_j in list(node._domain):
			node_target=node_dict_name [node_j]
			# if not (node._label.split('_')[0] <= node_target._label.split('_')[0] and 
			# 		node._label.split('_')[1] <= node_target._label.split('_')[1]):
			if not (int(node._label.split('_')[0]) <= int(node_target._label.split('_')[0]) and 
			int(node._label.split('_')[1]) <= int(node_target._label.split('_')[1])):

				node._domain.remove(node_j)
	
	# EARLY EXIT CHECK
	for node in nodes_array:
		if node._ispattern and not node._domain:
			print(f"Node {node._name} has empty domain after initial filtering. Exiting.")
			return None, iterations_ilf

	
	# for node in nodes_array:
	# 	print(node)
	#FIRST ITERATION##############################################
	
	print('	#2nd ITERATION##############################################')
	predecessors = list()
	successors = list()
	
	for node in nodes_array:
		if node._ispattern:
			node._label = get_label(Gp, node._name, labeling, True)
			node._neighbors_labels = [get_label(Gp, neighbor, labeling, True) for neighbor in Gp.neighbors(node._name)]
			
			# Ensure lists are initialized to avoid "not defined" errors
			predecessors = list(Gp.predecessors(node._name)) if node._name in Gp else []
			successors = list(Gp.successors(node._name)) if node._name in Gp else []

			node._predecessors = [get_label(Gp, pred, labeling, True) for pred in predecessors]
			node._successors = [get_label(Gp, succ, labeling, True) for succ in successors]
		else:
			node._label = get_label(Gt, node._name, labeling, True)
			node._neighbors_labels = [get_label(Gt, neighbor, labeling) for neighbor in Gt.neighbors(node._name)]
			
			# Ensure lists are initialized to avoid "not defined" errors
			predecessors = list(Gt.predecessors(node._name)) if node._name in Gt else []
			successors = list(Gt.successors(node._name)) if node._name in Gt else []

			node._predecessors = [get_label(Gt, pred, labeling,True) for pred in predecessors]
			node._successors = [get_label(Gt, succ, labeling,True) for succ in successors]


	ordered_labels= build_partial_order_3(nodes_array , True)
	
	#DOMAIN FILTERING###################################
	for label in ordered_labels:
		nodes_preced=[]
		#prendre un label de l'ordre partiel
		for label_preced in label._preceds: #m1 < m2,m3,m4
			labelpreced= [x for x in ordered_labels if x._name == label_preced ][0] # prendre m2
			
			#prendre les noeuds qui ont label m2
			for nodepreced in labelpreced._nodes:
				#ajouter les noeuds qui ont label m2 à la liste des noeuds qui seront ajoutés aux noeuds qui ont label m1
				if not node_dict_name [ nodepreced]._ispattern:
					nodes_preced.append(nodepreced)
			#pour les noeuds qui ont label m1 ajouter les noeuds du label m2
		for node in label._nodes:
			noeud=node_dict_name [ node]
			noeud._domain= nodes_preced
	

	iterations_ilf += 1


	# EARLY EXIT CHECK
	for node in nodes_array:
		if node._ispattern and not node._domain:
			print(f"Node {node._name} has empty domain after 1st iteration. Exiting.")
			return None, iterations_ilf

	# print('## NODES ARRAY ##############################')
	# for node in nodes_array:
	# 	print(node)

	# print('## LABELS ARRAY ##############################')
	# for label in ordered_labels:
	# 	print(label)

	k=3

	# ITERATIONS LOOP ##############################################
	for i in range(3, k): #k=100 max iterations
		domains_unchanged= True
		num_labels_unchanged= True
		iterations_ilf += 1


		print(f"	#{p.ordinal(i)} ITERATION  ############################################")
		
		#label of node becomes m1,m2... if m1 has the node in its list
		for node in nodes_array:
			node._label=[x for x in ordered_labels if node._name in x._nodes ][0]._name
			
		# Create a lookup dictionary for name-to-node mappings
		node_dict = {node._name: node for node in nodes_array}

		# Update each node's neighbor labels using the dictionary
		for node in nodes_array :
			if node._ispattern:
				
				predecessors = list(Gp.predecessors(node._name)) if node._name in Gp else []
				successors = list(Gp.successors(node._name)) if node._name in Gp else []

				node._predecessors = [node_dict[pred]._label for pred in predecessors]
				node._successors = [node_dict[succ]._label for succ in successors]
				
			else:
				predecessors = list(Gt.predecessors(node._name)) if node._name in Gt else []
				successors = list(Gt.successors(node._name)) if node._name in Gt else []

				node._predecessors = [node_dict[pred]._label for pred in predecessors]
				node._successors = [node_dict[succ]._label for succ in successors]
				
		
		
		new_ordered_labels= build_partial_order_4(nodes_array , ordered_labels,True)
		
		#DOMAIN FILTERING###################################
		#pour chaque label de l'ordre, prendre les labels qui suivent 
		#m1< m2, m3, m4 : prendre  m2, m3, m4  
		#et pour tous les noeuds qui ont lable m1, ajouter les noeuds qui ont label m2 ou m3 ou m4 au domaine de m1
		for label in new_ordered_labels:
			nodes_preced=[]
			#ajouter les noeuds aux domaines
			for label_preced in label._preceds: #m1 < m2,m3,m4

				# prendre m2 en tant qu'objet			
				labelpreced = [x for x in new_ordered_labels if x._name == label_preced] [0]
				
				#prendre les noeuds qui ont label m2
				for nodepreced in labelpreced._nodes:
					#vérifier que le noeud est pattern avant de l'ajouter
					if not node_dict_name [ nodepreced]._ispattern:
						nodes_preced.append(nodepreced)
			
   			#pour les noeus patterne qui ont ce label affecter les noeuds preceds au domaine
			for node in label._nodes:
				noeud= node_dict_name [ node]
				if noeud._ispattern:
					# si le domaine d'un noeud est différent des noeuds affectés
					if domains_unchanged and Counter(noeud._domain) != Counter(nodes_preced):
						domains_unchanged=False
					noeud._domain= nodes_preced
		
		 # EARLY EXIT CHECK
		for node in nodes_array:
			if node._ispattern and not node._domain:
				print(f"Node {node._name} has empty domain after {p.ordinal(iterations_ilf)} iteration. Exiting.")
				return None, iterations_ilf
		
		if len(ordered_labels)!= len(new_ordered_labels):
			num_labels_unchanged=False

		# la prochaine itération on utilise les nouveaux labels n1,n2,.. pour comparer o1=n1.{n} et o2=n2.{n3}
		ordered_labels= new_ordered_labels


		print('## NODES ARRAY ##############################')
		for node in nodes_array:
			print(node)

		# print('## LABELS ARRAY ##############################')
		# for label in new_ordered_labels:
		# 	print(label) 

		if num_labels_unchanged and domains_unchanged:
			print(f"Fixpoint reached at {p.ordinal(iterations_ilf)} iteration for labeling {labeling} ############################################# ")
			break
	

	#return nodes_array
	return  {node._name: [int(value) for value in node._domain] for node in nodes_array if node._ispattern}, iterations_ilf


# MAIN #############################################################################

# Instance 1: tokn graph relatively lightweight



def load(instance, graph_file, id):
	
	# Load graph
	graph = nx.drawing.nx_agraph.read_dot(graph_file).to_directed()

	# Plot input graph
	pydot.graph_from_dot_file(graph_file)[0].write_png(f'res/{Path(os.path.basename(graph_file)).stem}.png')

	# Get graph edges and labels
	#edges = graph.edges
	edges = [(u, v, d['angle']) for u, v, d in graph.edges(data=True) if 'angle' in d]
	labels = nx.get_node_attributes(graph, 'label')
	angles = nx.get_edge_attributes(graph, 'angle')

	# Set instance data
	instance[f'NV_{id}'] = graph.number_of_nodes()
	instance[f'NE_{id}'] = graph.number_of_edges()
	instance[f'V{id}'] = [label for label in labels.values()]
	instance[f'E{id}'] = list()
	instance[f'A{id}'] = list()
	for n1, n2, a in edges:
		instance[f'E{id}'].append((int(n1), int(n2)))
		key = (n1, n2, 0) if (n1, n2, 0) in angles else (n1, n2)
		instance[f'A{id}'].append('Horizontal' if angles[key] == '0' else 'Vertical')

################################################################

if __name__ == "__main__":
	
	

	pattern='ladder'
	target='gt-11252025133854'
	folder='dat'

	# target='pan'
	# pattern='panp1_lctr-06082025165701'
	# folder='lcres'

	# Go to parent directory
	os.chdir(os.path.dirname(os.path.realpath(__file__)) + '/..')

	# Gp = nx.drawing.nx_agraph.read_dot(f'lcres/{pattern}.dot')
	# Gt = nx.drawing.nx_agraph.read_dot(f'lcres/{target}.dot')
	

	Gp = nx.drawing.nx_agraph.read_dot(f'{folder}/{pattern}.dot')
	Gt = nx.drawing.nx_agraph.read_dot(f'{folder}/{target}.dot')
	
	# Transform nodes by appending 'p'
	Gp = nx.relabel_nodes(Gp, {node: f"{node}p" for node in Gp.nodes()})
	
	posp={}
	post={}

	# result,iterations, exec_time, peak_memory = run_with_timeout(2000, ILF, Gp, Gt, posp, post)
	result,iterations, exec_time, peak_memory = run_with_timeout(2000, dir_ILF, Gp, Gt, posp, post)
	#result,iterations, exec_time, peak_memory = run_with_timeout(3600 , ILF, Gp, Gt) #timeout 2 hrs

	if result == "TIMEOUT":
		ilf_reached_timeout = True
	elif result == "ERROR":
		print("ILF crashed or raised exception")
	elif result is None:
		ilf_domain_failed = True
	