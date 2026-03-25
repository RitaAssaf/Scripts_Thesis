import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
from itertools import combinations
import random
from networkx.drawing.nx_pydot import write_dot
from datetime import datetime
import argparse
from scipy.ndimage import gaussian_filter


class lcnode:
	def __init__(self, name=None, preceds=None, sublists=None):
		self.name = name
		self.preceds = preceds
		self.sublists =sublists


#not used
def sous_listes_transitives_completes(liste):
	sous_listes = []
	singletons = [[x] for x in liste]
	sous_listes.extend(singletons)

	pairs = set()
	index_map = {val: idx for idx, val in enumerate(liste)}

	# Step 1: Add all contiguous sublists
	for i in range(len(liste)):
		for j in range(i + 1, len(liste)):
			sub = liste[i:j + 1]
			sous_listes.append(sub)
			if len(sub) == 2:
				pairs.add((sub[0], sub[1]))

	# Step 2: Compute transitive closure (e.g., if (1,2) and (2,3) then add (1,3))
	transitive_pairs = set(pairs)
	changed = True
	while changed:
		changed = False
		new_pairs = set()
		for (a, b) in transitive_pairs:
			for (c, d) in transitive_pairs:
				if b == c and (a, d) not in transitive_pairs:
					new_pairs.add((a, d))
					changed = True
		transitive_pairs.update(new_pairs)

	# Step 3: Add [a, c] lists for all new transitive pairs
	for (a, c) in transitive_pairs:
		i = index_map[a]
		j = index_map[c]
		if i < j:
			sub = liste[i:j + 1]
			if sub[0] == a and sub[-1] == c and sub not in sous_listes:
				sous_listes.append([a, c])

	return sous_listes


def unique_combinations(nums, card=None):
	result = []
	n = len(nums)

	# If card is not specified, use the full length of the list
	max_len = min(card, n) if card is not None else n

	for r in range(1, max_len + 1):
		for combo in combinations(nums, r):
			result.append(list(combo))
	
	return result

def generer_sous_listes_ordonnées(liste):
	sous_listes = []
	for i in range(len(liste)):
		for j in range(i, len(liste)):
			sous_listes.append(liste[i:j + 1])  
	return sous_listes


def get_max_degree(graph):
	"""
	Returns the maximum degree of any node in the given graph.

	Parameters:
	- graph: A NetworkX graph object.

	Returns:
	- int: Maximum degree of any node.
	"""
	return max(dict(graph.degree()).values())




def extraction_arcs(mat:list[list],lab:str):
	# lit une liste de liste pour extraire des arcs sur chaque ligne dont le label est lab
	arc_ext=[]
	for li in mat:
		i = 0
		while i < len(li) - 1:
			if li[i] > -1: #token exist
				j = i + 1
				while j < len(li) and li[j] == -1:
					j = j + 1
				if j < len(li):
					arc_ext.append((li[i], li[j], {'label': lab, 'angle': 0 if lab == 'h' else 90}))
				i = j
			else:
				i = i + 1
	return arc_ext

def cloture_reflexive(G,lab:str):
	for noeud in G.nodes():
		G.add_edge(noeud, noeud)
		G[noeud][noeud]['label']=lab
	return G

def cloture_transitive(G,lab:str, angle=0):
	G_cloture = nx.transitive_closure(G)
	# Copier les attributs des arêtes du graphe d'origine vers le graphe de la clôture
	for u,v in G_cloture.edges():
		if 'label' not in G_cloture[u][v]:
			G_cloture[u][v]['label'] = lab
	for u,v in G_cloture.edges():
		if 'angle' not in G_cloture[u][v]:
			G_cloture[u][v]['angle'] = angle
	return G_cloture

def aplatir_liste(liste_imbriquee):
	resultat = []
	for i in liste_imbriquee:
		for e in i:
			resultat.append(e)
	return resultat





def get_coordinates(v, n):
	j = (v - 1) // n
	i = (v - 1) % n
	return (i, j)


def nommer(l, label):
	l=sorted(l)
	s = ".".join(map(str, l)) #concatener la liste des tokens dans la ligne/colonne
	return label + s #ajoute label l ou c

def numerote(mat:list[list]):
	compteur = 0  # Initialisation du compteur
	for i in range(len(mat)):
		for j in range(len(mat[i])):
			if mat[i][j] > -1:
				mat[i][j] = compteur
				compteur += 1
	return mat

def numerotep1(mat:list[list]):
	compteur = 1  # Initialisation du compteur
	for i in range(len(mat)):
		for j in range(len(mat[i])):
			if mat[i][j] > -1:
				mat[i][j] = compteur
				compteur += 1
	return mat

def generer_positions_alea(n, p):

	mat = [[-1] * n for _ in range(n)]
	places = random.sample(range(n * n), p)
	# Placer les 1
	for pl in places:
		i, j = divmod(pl, n)  # pl = 7 → divmod(7, 3) → (2, 1)  # Row 2, Column 1 in matrix 3 x 3
		mat[i][j] = 1
	return mat



def generer_positions_alea_rm_isolated(n, p):
	"""
	Génère une matrice n x n remplie de -1, avec p positions mises à 1.
	Puis supprime toute case '1' isolée (sans autre '1' sur sa ligne ni sa colonne).
	"""
	if not 0 <= p <= n * n:
		raise ValueError("p must be between 0 and n*n")

	# 1) Placement aléatoire initial
	mat = [[-1] * n for _ in range(n)]
	for pl in random.sample(range(n * n), p):
		i, j = divmod(pl, n)
		mat[i][j] = 1

	# 2) Comptes par lignes et colonnes
	row_counts = [0] * n
	col_counts = [0] * n
	for i in range(n):
		for j in range(n):
			if mat[i][j] == 1:
				row_counts[i] += 1
				col_counts[j] += 1

	# 3) Supprimer les '1' isolés
	for i in range(n):
		for j in range(n):
			if mat[i][j] == 1 and row_counts[i] == 1 and col_counts[j] == 1:
				mat[i][j] = -1

	return mat





def generer_positions_alea_2(n, p):
	mat = [[-1] * n for _ in range(n)]
	places = random.sample(range(n * n), p)

	# Place initial 1s
	for pl in places:
		i, j = divmod(pl, n)
		mat[i][j] = 1


	def is_isolated(i, j):
		"""Check if mat[i][j] == 1 is isolated (alone in row and column)."""
		if mat[i][j] != 1:
			return False
		row_count = sum(1 for x in mat[i] if x == 1)
		col_count = sum(1 for row in mat if row[j] == 1)
		return row_count == 1 and col_count == 1

	# Fix isolated ones
	for i in range(n):
		for j in range(n):
			if is_isolated(i, j):
				# Remove isolated 1
				mat[i][j] = -1

				# Find a new place to put it (not isolated if possible)
				candidates = [(r, c) for r in range(n) for c in range(n) if mat[r][c] == -1]
				random.shuffle(candidates)

				placed = False
				for r, c in candidates:
					mat[r][c] = 1
					if not is_isolated(r, c):
						placed = True
						break
					mat[r][c] = -1  # rollback if still isolated

				if not placed and candidates:
					# If no safe spot, just put it anywhere free
					r, c = candidates[0]
					mat[r][c] = 1

	return mat



# Function to extract ordered nodes based on preceds
def sorted_nodes(graph):
	ordered = []
	for node in graph.nodes:
		if node not in ordered:
			ordered.append(node)
		for succ in graph.nodes[node]['preceds']:
			if succ not in ordered:
				ordered.append(succ)
	return ordered


def build_preced(lignes, colonnes, GLC_max, GT):
	for li in lignes:
		for lj in lignes:
			if lj == li:# la relation d'ordre n'est pas réfléxives
				continue
			found = False
			for node_i in li:
				for node_j in lj:
					if (node_i, node_j) in GT.edges:
						GLC_max.nodes[nommer(sorted(li), 'l')]['preceds'].append(nommer(sorted(lj), 'l'))
						found = True
						break  
				if found:
					break  # break loop over node_i
	breakpoint=0
	for ci in colonnes:
		for cj in colonnes:
			if ci == cj:# la relation d'ordre n'est pas réfléxives
				continue
			found = False
			for node_i in ci:
				for node_j in cj:
					if (node_i, node_j) in GT.edges:
						GLC_max.nodes[nommer(sorted(ci), 'c')]['preceds'].append(nommer(sorted(cj), 'c'))
						found = True
						break  
				if found:
					break  # break loop over node_i
	breakpoint=0


def replace_negatives_with_zero(A):

	A = np.array(A)          # ensure NumPy array
	A[A == -1] = 0           # replace -1s with 0s
	return A


def analyze_matrix_distribution_0(A, output_file="matrix_metrics.txt"):
	"""
	Compute spatial and statistical distribution measures for a binary (0/1) matrix
	and write the results to a text file.
	"""

	# Convert to numpy array
	A = np.array(A)
	m, n = A.shape
	ones = np.argwhere(A == 1)
	N = len(ones)

	# If no 1s in matrix
	if N == 0:
		with open(output_file, "w") as f:
			f.write("Matrix has no 1s.\n")
		return

	# 1. Density
	density = N / (m * n)

	# 2. Row & column variances
	row_sums = A.sum(axis=1)
	col_sums = A.sum(axis=0)
	row_var = np.var(row_sums)
	col_var = np.var(col_sums)

	# 3. Spatial concentration (center of mass + spread)
	i_mean, j_mean = ones.mean(axis=0)
	spread = np.mean((ones[:,0] - i_mean)**2 + (ones[:,1] - j_mean)**2)

	#4. Entropy of distribution
	p = np.zeros((m, n))
	p[A == 1] = 1 / N
	entropy = -np.sum(p[A == 1] * np.log(p[A == 1]))


	# Write results to file
	with open(output_file, "w") as f:
		f.write("=== Matrix Distribution Metrics ===\n\n")
		f.write(f"Matrix size: {m} x {n}\n")
		f.write(f"Number of 1s: {N}\n\n")
		f.write(f"Density: {density:.4f}\n")
		f.write(f"Row variance: {row_var:.4f}\n")
		f.write(f"Column variance: {col_var:.4f}\n")
		f.write(f"Center of mass: ({i_mean:.2f}, {j_mean:.2f})\n")
		f.write(f"Spatial spread: {spread:.4f}\n")
		f.write(f"Entropy: {entropy:.4f}\n")

	print(f"✅ Metrics written to '{output_file}'")

	return m, n, N, density, row_var, col_var, i_mean, j_mean , spread, entropy



def analyze_matrix_distribution(A, output_file="matrix_metrics.txt"):
	"""
	Compute spatial and statistical distribution measures for a binary (0/1) matrix
	and write the results to a text file.
	"""

	# Convert to numpy array
	A = np.array(A)
	m, n = A.shape
	ones = np.argwhere(A == 1)
	N = len(ones)

	# If no 1s in matrix
	if N == 0:
		with open(output_file, "w") as f:
			f.write("Matrix has no 1s.\n")
		return

	# 1. Density
	density = N / (m * n)

	# 2. Row & column variances
	row_sums = A.sum(axis=1)
	col_sums = A.sum(axis=0)
	row_var = np.var(row_sums)
	col_var = np.var(col_sums)

	# 3. Spatial concentration (center of mass + spread)
	i_mean, j_mean = ones.mean(axis=0)
	spread = np.mean((ones[:, 0] - i_mean)**2 + (ones[:, 1] - j_mean)**2)

	# 4. Spatial entropy of 1s
	# p = A / N  # spatial probability distribution
	# p_nonzero = p[p > 0]  # only positions with 1s
	# entropy = -np.sum(p_nonzero * np.log(p_nonzero))


	# 4. Spatial entropy (depends on spread)
	smoothed = gaussian_filter(A.astype(float), sigma=2)
	p = smoothed / smoothed.sum()
	entropy = -np.sum(p[p > 0] * np.log(p[p > 0]))




	# Write results to file
	with open(output_file, "w") as f:
		f.write("=== Matrix Distribution Metrics ===\n\n")
		f.write(f"Matrix size: {m} x {n}\n")
		f.write(f"Number of 1s: {N}\n\n")
		f.write(f"Density: {density:.4f}\n")
		f.write(f"Row variance: {row_var:.4f}\n")
		f.write(f"Column variance: {col_var:.4f}\n")
		f.write(f"Center of mass: ({i_mean:.2f}, {j_mean:.2f})\n")
		f.write(f"Spatial spread: {spread:.4f}\n")
		f.write(f"Entropy: {entropy:.4f}\n")

	print(f"✅ Metrics written to '{output_file}'")

	return m, n, N, density, row_var, col_var, i_mean, j_mean, spread, entropy

def main():
	# positions = [[1,-1, -1,-1,-1],
	# 			[1,1,1,1,1],
	# 			[1,1,1,-1,-1],
	# 			[-1,-1,-1,-1,-1],
	# 			s[-1,-1,-1,-1,-1]
	# 		]
	#positions = [[1,1],[1,1],[1,-1]]
	positions = generer_positions_alea_2(grid, number_of_nodes)


	positions_to_study = replace_negatives_with_zero(positions)
	m, n, N, density, row_var, col_var, i_mean, j_mean , spread, entropy=analyze_matrix_distribution(positions_to_study)
	print(f"m:{round(m,3)}, n:{round(n,3)}, N:{round(N,3)}, density:{round(density,3)}, row_var:{round(row_var,3)}, col_var:{round(col_var,3)}, i_mean:{round(i_mean,3)}, j_mean:{round(j_mean,3)}, spread:{round(spread,3)}, entropy:{round(entropy,3)}")

	positions = numerote(positions)

	#print(positions)

	#traitement de l'instance et mise en forme des paramètres (taille, arcs...)
	nb_nodes = sum(1 for li in positions for val in li if val != -1)
	taille_graphique = len(positions)
	positionsT = list(map(list, zip(*positions))) #transpose zip ([[1 2 3], [4 5 6]]) = [1 4] [2 5] [3 6]
	arcs = extraction_arcs(positions,'h')+extraction_arcs(positionsT,'v')

	arcs_h = [arc for arc in arcs if arc[2]['label'] == 'h']
	arcs_v = [arc for arc in arcs if arc[2]['label'] == 'v']

	sup_ligcol=False#pour ne pas afficher les lignes colonnes de taille 1 dans le GLC
	
	# création du graphe de position réduit
	G = nx.DiGraph()
	# for n in ran-ge(nb_nodes):
	# 	G.add_node(n , type='t'),
	for i in range(len(positions)):
		for j in range(len(positions[i])):
			if positions[i][j] > -1:
				G.add_node(positions[i][j],x=j, y=i,  position=(j, i))
	G.add_edges_from(arcs)

	# graphe avec arcs horizontaux
	GH = nx.DiGraph()
	GH.add_nodes_from(range(0, nb_nodes))
	GH.add_edges_from(arcs_h)
	# graphe avec arcs verticaux
	GV = nx.DiGraph()
	GV.add_nodes_from(range(0, nb_nodes))
	GV.add_edges_from(arcs_v)

	#Graphe de position (avec transitivité)
	GHT = cloture_transitive(GH,'h',0)
	GVT = cloture_transitive(GV,'v',90)
	GT = nx.compose(GHT, GVT)


	GT2 = nx.DiGraph()

	# Add nodes from G to GT2 with all attributes
	for n, attr in G.nodes(data=True):
		GT2.add_node(n, **attr)

	# Add edges from GT to GT2
	for u, v, attr in GT.edges(data=True):
		GT2.add_edge(u, v, **attr) 

	# Extraction des lignes et colonnes
	lignes = list(nx.find_cliques(GHT.to_undirected()))
	colonnes = list(nx.find_cliques(GVT.to_undirected()))
	
	transitive_lignes = list(nx.enumerate_all_cliques(GHT.to_undirected()))
	transitive_colonnes = list(nx.enumerate_all_cliques(GVT.to_undirected()))
	edges = []

#preceds origin############################################################""
#### création du graphe lignes/colonnes maximales######################################################################"######"
	
	GLC_max = nx.Graph()


	for li in lignes:
		li=sorted(li)
		node_name = nommer(li, 'l')
		GLC_max.add_node(node_name, type='l', preceds=[])	#j'ai ajouté l56
		
	for co in colonnes:
		node_name = nommer(co, 'c')
		GLC_max.add_node(node_name, type='c', preceds=[])	#j'ai ajouté c24
		
	build_preced(lignes, colonnes,GLC_max, GT)

	for li in lignes:
		for co in colonnes:
			if set(li) & set(co): # computes the intersection between these two sets
				GLC_max.add_edge(nommer(sorted(li), 'l'), nommer(sorted(co), 'c'))
				edges.append((nommer(sorted(li), 'l'), nommer(sorted(co), 'c')))


## création des sous-listes lignes/colonnes###########################################################################
	sublists = {}
	all_lignes = []
	lines_names = []
	for li in lignes:
		li=sorted(li)
		line_name= nommer(li, 'l')
		sublists[line_name]=generer_sous_listes_ordonnées(li)
		all_lignes.append(sublists[line_name])
	all_colonnes = []
	for co in colonnes:
		co=sorted(co)
		col_name= nommer(sorted(co), 'c')
		sublists[col_name]=generer_sous_listes_ordonnées(co)
		all_colonnes.append(sublists[col_name])
	all_colonnes = aplatir_liste(all_colonnes)
	all_lignes = aplatir_liste(all_lignes)
	# Supression des lignes et colonnes de taille 1 pour la visibilité
	if sup_ligcol:
		all_lignes=[li for li in all_lignes if len(li) > 1]
		all_colonnes = [col for col in all_colonnes if len(col) > 1]


#dictionnaire full preceds pour inclure les sous-lignes/colonnes pour chaque noeud globale###################"""""""#

	full_preceds={}
	for node in GLC_max.nodes:
		new_preceds=[]
		for preced in GLC_max.nodes[node]['preceds']:
			if preced.startswith('l'):
				new_preceds.append([nommer( sorted(li), 'l' ) for li in sublists[preced]])
			else:
				new_preceds.append([nommer( sorted(ci) , 'c') for ci in sublists[preced]])
		full_preceds[node]=[item for sublist in new_preceds for item in sublist]
			
		

#création du graphes avec sous-lignes/colonnes#####################################################""	
	GLC = nx.Graph()
	
	GLC.add_nodes_from([
	(
		nommer(li, 'l'), 
		{
			'type': 'l',
			'sublists': sublists[nommer(li, 'l')] if nommer(li, 'l') in sublists else "",
			'preceds': full_preceds[nommer(li, 'l')] if nommer(li, 'l') in full_preceds else "",
			'card': len(li)
		}
	) 
	for li in all_lignes
	])

	GLC.add_nodes_from([
	(
		nommer(sorted(co), 'c'), 
		{
			'type': 'c',
			'sublists': sublists[nommer(sorted(co), 'c')] if nommer(sorted(co), 'c') in sublists else "", 
			'preceds': full_preceds[nommer(sorted(co), 'c')] if nommer(sorted(co), 'c') in full_preceds else "",
			'card': len(co)
		}
	) 
	for co in all_colonnes
	])

	for lc_complete in GLC_max.nodes:#cette étape n'est plus nécessaire car toutes les sous-listes existent dans full_preceds
		for sublist in sublists[lc_complete]:#les enfants héritent le preceds des parents
			if lc_complete.startswith('l'):
				GLC.nodes[nommer(sublist, 'l')]['preceds'] = full_preceds[lc_complete]
			else:
				GLC.nodes[nommer(sublist, 'c')]['preceds'] = full_preceds[lc_complete]


	for li in all_lignes:
		for co in all_colonnes:
			if set(li) & set(co):
				GLC.add_edge(nommer(li, 'l'), nommer(sorted(co), 'c'))


###LC TRANSITIV################################################################################""

	# sublists_t = {}
	# all_lignes_t = []
	# lines_names = []
	# for li in lignes:
	# 	li=sorted(li)
	# 	line_name= nommer(li, 'l')
	# 	sublists_t[line_name]=unique_combinations(li)
	# 	all_lignes_t.append(sublists_t[line_name])
	# all_colonnes_t = []
	# for co in colonnes:
	# 	co=sorted(co)
	# 	col_name= nommer(sorted(co), 'c')
	# 	sublists_t[col_name]=unique_combinations(co)
	# 	all_colonnes_t.append(sublists_t[col_name])
	# all_colonnes_t = aplatir_liste(all_colonnes_t)
	# all_lignes_t = aplatir_liste(all_lignes_t)

	# #for each &full line if it preceds l123 then preceds l1,l2,l3,l12,l13,l23
	# full_preceds_transitive={}
	# for node in GLC_max.nodes:
	# 	new_preceds=[]
	# 	for preced in GLC_max.nodes[node]['preceds']:#exemple de bowtie c25 preceds c036 
	# 		if preced.startswith('l'):s
	# 			new_preceds.append([nommer( li, 'l' ) for li in sublists_t[preced]])
	# 		else:
	# 			new_preceds.append([nommer( ci , 'c') for ci in sublists_t[preced]])#c0,c03,c06
	# 	full_preceds_transitive[node]=[item for sublist in new_preceds for item in sublist]
			
	
	# # création du graphe avec toutes lignes/colonnes
	# GLCT = nx.Graph()
	
	# GLCT.add_nodes_from([
	# (
	# 	nommer(li, 'l'), 
	# 	{
	# 		'type': 'l',
	# 		'sublists_t': sublists_t[nommer(li, 'l')] if nommer(li, 'l') in sublists_t else "", 
	# 		'preceds': full_preceds_transitive[nommer(li, 'l')] if nommer(li, 'l') in full_preceds_transitive else "",
	# 		'card': len(li)
	# 	}
	# ) 
	# for li in all_lignes_t
	# ])

	# GLCT.add_nodes_from([
	# (
	# 	nommer(sorted(co), 'c'), 
	# 	{
	# 		'type': 'c',
	# 		'sublists_t': sublists_t[nommer(sorted(co), 'c')] if nommer(sorted(co), 'c') in sublists_t else "", 
	# 		'preceds':full_preceds_transitive[nommer(sorted(co), 'c')] if nommer(sorted(co), 'c') in full_preceds_transitive else "",
	# 		'card': len(co)
	# 	}
	# ) 
	# for co in all_colonnes_t
	# ])

	# for lc_complete in GLC_max.nodes:
	# 	for sublist in sublists_t[lc_complete]:
	# 		if lc_complete.startswith('l'):
	# 			GLCT.nodes[nommer(sublist, 'l')]['preceds'] = full_preceds_transitive[lc_complete]
	# 		else:
	# 			GLCT.nodes[nommer(sublist, 'c')]['preceds'] = full_preceds_transitive[lc_complete]


	# for li in all_lignes_t:
	# 	for co in all_colonnes_t:
	# 		if set(li) & set(co):
	# 			GLCT.add_edge(nommer(li, 'l'), nommer(sorted(co), 'c'))



# ###LC CARD################################################################################""
	max_card=4
	sublists_t = {}
	all_lignes_t = []
	lines_names = []
	for li in lignes:
		li=sorted(li)
		line_name= nommer(li, 'l')
		sublists_t[line_name]=unique_combinations(li,max_card)
		all_lignes_t.append(sublists_t[line_name])
	all_colonnes_t = []
	for co in colonnes:
		co=sorted(co)
		col_name= nommer(sorted(co), 'c')
		sublists_t[col_name]=unique_combinations(co,max_card)
		all_colonnes_t.append(sublists_t[col_name])
	all_colonnes_t = aplatir_liste(all_colonnes_t)
	all_lignes_t = aplatir_liste(all_lignes_t)
	


	#for each &full line if it preceds l123 then preceds l1,l2,l3,l12,l13,l23
	full_preceds_transitive={}
	for node in GLC_max.nodes:
		new_preceds=[]
		for preced in GLC_max.nodes[node]['preceds']:#exemple de bowtie c25 preceds c036 
			if preced.startswith('l'):
				new_preceds.append([nommer( li, 'l' ) for li in sublists_t[preced]])
			else:
				new_preceds.append([nommer( ci , 'c') for ci in sublists_t[preced]])#c0,c03,c06
		full_preceds_transitive[node]=[item for sublist in new_preceds for item in sublist]
			



	# création du graphe avec cardinalité
	glc_card = nx.Graph()
	
	glc_card.add_nodes_from([
	(
		nommer(li, 'l'), 
		{
			'type': 'l',
			'sublists_t': sublists_t[nommer(li, 'l')] if nommer(li, 'l') in sublists_t else "", 
			'preceds': full_preceds_transitive[nommer(li, 'l')] if nommer(li, 'l') in full_preceds_transitive else "",
			'card': len(li)
		}
	) 
	for li in all_lignes_t
	])

	glc_card.add_nodes_from([
	(
		nommer(sorted(co), 'c'), 
		{
			'type': 'c',
			'sublists_t': sublists_t[nommer(sorted(co), 'c')] if nommer(sorted(co), 'c') in sublists_t else "", 
			'preceds':full_preceds_transitive[nommer(sorted(co), 'c')] if nommer(sorted(co), 'c') in full_preceds_transitive else "",

			'card': len(co)
		}
	) 
	for co in all_colonnes_t
	])

	#sublists inherits order from parents
	for lc_complete in GLC_max.nodes:
		for sublist in sublists_t[lc_complete]: #sublists inherits the preceds from their parents
			if lc_complete.startswith('l'):#example if l012 preceds l34 then l01 preceds l34 and l1 preceds l34
				glc_card.nodes[nommer(sublist, 'l')]['preceds'] = full_preceds_transitive[lc_complete]
			else:
				glc_card.nodes[nommer(sublist, 'c')]['preceds'] = full_preceds_transitive[lc_complete]


	for li in all_lignes_t:
		for co in all_colonnes_t:
			if set(li) & set(co):
				glc_card.add_edge(nommer(li, 'l'), nommer(sorted(co), 'c'))


############### création de l'hypergraphe de Stell avec uniquement les lignes et colonnes complètes
	HST = nx.DiGraph()
	HST.add_nodes_from(GLC_max.nodes(data=True))
	HST.add_nodes_from(G.nodes(data=True))
	for n in G.nodes():
		HST.add_edge(n, n)
	for li in lignes:
		for n in G.nodes():
			if n in li:
				HST.add_edge(nommer(li, 'l'), n)
	for co in colonnes:
		for n in G.nodes():
			if n in co:
				HST.add_edge(nommer(sorted(co), 'c'), n)

	# Graphe de positions avec la disposition en grille
	# positions pour le dessin
	if positions == []:
		# si on utilise une représentation sans avoir une grille au départ
		# mais juste la liste des arcs et le graphe G
		pos = {}
		for node in G.nodes():
			x, y = get_coordinates(node, taille_graphique)
			pos.update({node: (x, -y)})
	else:
		pos = {}
		
	# Choix des affichages 
	affichage={'GP':True,'Equivalent':False,'glc_card': True,'GT':False,'GLCRed':False,'GLCall':False,'HS':False,'GLCT': False,'imageGRed': False, 'imageGLCall': False }

	# Affichage des deux graphes de positions (réduit et avec transitivité
	if affichage['GP']:
		
		timestamp = datetime.now().strftime("%m%d%Y%H%M%S")

		# Generate Graphviz DOT format
		dot_filename = f"../dat/apositions-{timestamp}.dot"
		#write_dot(G, dot_filename)
		with open(dot_filename, "w") as f:
			f.write("digraph G {\n")
			f.write("    graph [splines=false, nodesep=0.5, rankdir=TB];\n")
			f.write("    node [shape=circle, fixedsize=true, width=0.4, fontsize=10];\n")

			# Add nodes with labels
			for node, (x, y) in nx.get_node_attributes(G, "position").items():
				f.write(f'    {node} [label="{node}", x={x}, y={y}];\n')

			# Add rank=same constraints
			row_dict = {}
			for node, pos in nx.get_node_attributes(G, "position").items():
				y_coord = pos[1]
				if y_coord not in row_dict:
					row_dict[y_coord] = []
				row_dict[y_coord].append(str(node))

			for nodes in row_dict.values():
				if len(nodes) > 1:
					f.write(f'    {{ rank=same; {" ".join(nodes)} }};\n')

			#Add edges with angle attributes (only once)
			for node_a, node_b, attributes in arcs:
				#f.write(f'    {node_a} -> {node_b} [{angle}];\n')
				attr_str = ", ".join(f'{key}="{value}"' if isinstance(value, str) else f"{key}={value}" for key, value in attributes.items())
				f.write(f'    {node_a} -> {node_b} [{attr_str}];\n')

			# f.write(f"//{positions} \n")

			f.write("}\n")

		print(f"Graph saved to {dot_filename}")


	if affichage['Equivalent']:
		timestamp = datetime.now().strftime("%m%d%Y%H%M%S")

		# using l012, l34 token format
		dot_filename = f"../lcres/equivalent_{timestamp}.dot"

		# Append rank constraints for ordered nodes
		ordered_nodes = sorted_nodes(GLC_max)
	
		# Create a mapping of node names to indices
		node_index_map = {node: str(i) for i, node in enumerate(ordered_nodes)}
		# Separate nodes into 'l' and 'c' groups
		l_nodes = [node for node in ordered_nodes if node.startswith('l')]
		c_nodes = [node for node in ordered_nodes if node.startswith('c')]
		# Get indices of line nodes ('l' nodes)
		l_nodes_indices = [node_index_map[node] for node in ordered_nodes if node.startswith('l')]
		# Get indices of line nodes ('c' nodes)
		c_nodes_indices = [node_index_map[node] for node in ordered_nodes if node.startswith('c')]
		with open(dot_filename, "a") as f:
			f.write("strict graph G {\n")
			f.write("    graph [splines=true, nodesep=0.5, rankdir=TB];\n")
			f.write("    node [shape=circle, fixedsize=true, width=0.4, fontsize=10];\n")
			
			for node, index in node_index_map.items():
				node_type = GLC_max.nodes[node]['type']
				node_card = GLC.nodes[node].get('card', "")
				preceds = ','.join(node_index_map[succ] for succ in GLC_max.nodes[node]['preceds'])
				f.write(f'    {index} [label="{index}", type="{node_type}", preceds="{preceds}", realname="{node}", card="{node_card}"];\n')
			
			# Add edges with indices
			for edge in GLC_max.edges:
				f.write(f'    {node_index_map[edge[0]]} -- {node_index_map[edge[1]]};\n')



			f.write("\n    // Ensure horizontal order\n")
			f.write(f"    {{ rank=same; {' '.join(l_nodes_indices )} }}\n")
			f.write(f"    {{ rank=same; {' '.join(c_nodes_indices)} }}\n")
			
			f.write("}\n")
		print(f"DOT saved in :'{dot_filename}'")

	# Graphe avec toutes les lignes colonnes et transitivité
	if affichage['GLCT']: 
		timestamp = datetime.now().strftime("%m%d%Y%H%M%S")

	
		dot_filename = f"../lcres/lctr-{timestamp}.dot"
		num_nodes = GLCT.number_of_nodes()
		num_edges = GLCT.number_of_edges()
		max_degree = get_max_degree(GLCT)
		num_components = nx.number_connected_components(GLCT)


		# Create a mapping of nodes to their indices
		node_index_map = {node: str(i) for i, node in enumerate(GLCT.nodes)}

		l_nodes_indices = [node_index_map[node] for node in GLCT.nodes if node.startswith('l')]
		c_nodes_indices = [node_index_map[node] for node in GLCT.nodes if node.startswith('c')]

		with open(dot_filename, "a") as f:
			f.write("strict graph G {\n")
			f.write("    graph [splines=true, nodesep=0.5, rankdir=TB];\n")
			f.write("    node [shape=circle, fixedsize=true, width=0.4, fontsize=10];\n")

				# Add number of nodes and edges as comment or metadata
			f.write(f"    // Number of nodes: {num_nodes}\n")
			f.write(f"    // Number of edges: {num_edges}\n")
			# Add nodes with indexed labels
			for node in GLCT.nodes:
				node_type = GLCT.nodes[node].get('type', "")
				node_card = GLCT.nodes[node].get('card', "")
				preceds = ",".join(node_index_map[p] for p in GLCT.nodes[node].get('preceds', []) if p in node_index_map)
				index = node_index_map[node]  # Get index for the node
				#label = f"{node}#{index}"     # Create indexed label
				f.write(f'    {index} [label="{index}", type="{node_type}", preceds="{preceds}", realname="{node}", card="{node_card}"];\n')

			# Add edges
			for node_a, node_b in GLCT.edges:
				index_a = node_index_map[node_a]  # Get index for node_a
				index_b = node_index_map[node_b]  # Get index for node_b
				f.write(f'    {index_a} -- {index_b} ;\n')


			f.write("}\n")
			print(f"DOT saved in :'{dot_filename}', num_nodes:{num_nodes}, num_edges:{num_edges}, max_degree: {max_degree}, num_components: {num_components}, ")


#Graphe avec toutes les lignes colonnes + transitivité + cardinalité
	if affichage['glc_card']: 
		timestamp = datetime.now().strftime("%m%d%Y%H%M%S")

		#indexes format 
		dot_filename = f"../lcres/glc_card_{timestamp}.dot"
		num_nodes = glc_card.number_of_nodes()
		num_edges = glc_card.number_of_edges()
		max_degree = get_max_degree(glc_card)
		num_components = nx.number_connected_components(glc_card)


		# Create a mapping of nodes to their indices
		node_index_map = {node: str(i) for i, node in enumerate(glc_card.nodes)}

		l_nodes_indices = [node_index_map[node] for node in glc_card.nodes if node.startswith('l')]
		c_nodes_indices = [node_index_map[node] for node in glc_card.nodes if node.startswith('c')]

		with open(dot_filename, "a") as f:
			f.write("strict graph G {\n")
			f.write("    graph [splines=true, nodesep=0.5, rankdir=TB];\n")
			f.write("    node [shape=circle, fixedsize=true, width=0.4, fontsize=10];\n")

				# Add number of nodes and edges as comment or metadata
			f.write(f"    // Number of nodes: {num_nodes}\n")
			f.write(f"    // Number of edges: {num_edges}\n")
			# Add nodes with indexed labels
			for node in glc_card.nodes:
				node_type = glc_card.nodes[node].get('type', "")
				node_card = glc_card.nodes[node].get('card', "")
				preceds = ",".join(node_index_map[p] for p in glc_card.nodes[node].get('preceds', []) if p in node_index_map)
				index = node_index_map[node]  
				f.write(f'    {index} [label="{index}", type="{node_type}", preceds="{preceds}", realname="{node}", card="{node_card}"];\n')

			# Add edges
			for node_a, node_b in glc_card.edges:
				index_a = node_index_map[node_a]  # Get index for node_a
				index_b = node_index_map[node_b]  # Get index for node_b
				f.write(f'    {index_a} -- {index_b} ;\n')


			f.write("}\n")
			print(f"DOT saved in :'{dot_filename}', num_nodes:{num_nodes}, num_edges:{num_edges}, max_degree:{max_degree}, num_components: {num_components}")


	if affichage['GT']:
		
		timestamp = datetime.now().strftime("%m%d%Y%H%M%S")
		# Count nodes and edges
		num_nodes = GT2.number_of_nodes()
		num_edges = GT2.number_of_edges()
		max_degree = get_max_degree(GT2)
		num_components = nx.number_weakly_connected_components(GT2)
		num_strongly_components = nx.number_strongly_connected_components(GT2)


		# Generate Graphviz DOT format
		dot_filename = f"../dat/gt-{timestamp}.dot"
		with open(dot_filename, "w") as f:
			f.write("digraph G {\n")
			f.write("    graph [splines=false, nodesep=0.5, rankdir=TB];\n")
			f.write("    node [shape=circle, fixedsize=true, width=0.4, fontsize=10];\n")

			# Add nodes with labels
			for node, pos in nx.get_node_attributes(GT2, "position").items():
				f.write(f'    {node} [label="{node}"];\n')

			# Add rank=same constraints
			row_dict = {}
			for node, pos in nx.get_node_attributes(GT2, "position").items():
				y_coord = pos[1]
				if y_coord not in row_dict:
					row_dict[y_coord] = []
				row_dict[y_coord].append(str(node))

			for nodes in row_dict.values():
				if len(nodes) > 1:
					f.write(f'    {{ rank=same; {" ".join(nodes)} }};\n')

			#Add edges with angle attributes (only once)
			for node_a, node_b, attributes in GT2.edges(data=True):
				#f.write(f'    {node_a} -> {node_b} [{angle}];\n')
				attr_str = ", ".join(f'{key}="{value}"' if isinstance(value, str) else f"{key}={value}" for key, value in attributes.items())
				f.write(f'    {node_a} -> {node_b} [{attr_str}];\n')

			# f.write(f"//{positions} \n")

			f.write("}\n")

		print(f"Graph saved to {dot_filename} , num_nodes:{num_nodes}, num_edges:{num_edges}, max_degree:{max_degree}, num_strongly_components:{num_strongly_components}, num_components: {num_components}")


#####################################################################################
#affichage

	# Graphe avec lignes et colonnes
	if affichage['GLCRed']:
		timestamp = datetime.now().strftime("%m%d%Y%H%M%S")

		# using l012, l34 token format
		dot_filename = f"../lcres/aGLC_tokens_{timestamp}.dot"
		
		ordered_nodes = sorted_nodes(GLC_max)
	
		# Create a mapping of node names to indices
		node_index_map = {node: str(i) for i, node in enumerate(ordered_nodes)}
		# Separate nodes into 'l' and 'c' groups
		l_nodes = [node for node in ordered_nodes if node.startswith('l')]
		c_nodes = [node for node in ordered_nodes if node.startswith('c')]
		# Get indices of line nodes ('l' nodes)
		l_nodes_indices = [node_index_map[node] for node in ordered_nodes if node.startswith('l')]
		# Get indices of line nodes ('c' nodes)
		c_nodes_indices = [node_index_map[node] for node in ordered_nodes if node.startswith('c')]

		timestamp = datetime.now().strftime("%m%d%Y%H%M%S")

		# Generate Graphviz DOT format
		dot_filename_label = f"../lcres/aGLC_{timestamp}.dot"

		with open(dot_filename_label, "w") as f:
			f.write("strict graph G {\n")
			f.write("    graph [splines=true, nodesep=0.5, rankdir=TB];\n")
			f.write("    node [shape=circle, fixedsize=true, width=0.4, fontsize=10];\n")

			for node, index in node_index_map.items():
				node_type = GLC_max.nodes[node]['type']
				node_card = GLCT.nodes[node].get('card', "")

				preceds = ','.join(node_index_map[succ] for succ in GLC_max.nodes[node]['preceds'])
				f.write(f'    {index} [label="{index}", type="{node_type}", preceds="{preceds}" , realname="{node}" , card="{node_card}"];\n')
			
			# Add edges with indices
			for edge in GLC_max.edges:
				f.write(f'    {node_index_map[edge[0]]} -- {node_index_map[edge[1]]};\n')

			f.write("\n    // Ensure horizontal order\n")
			f.write(f"    {{ rank=same; {' '.join(l_nodes_indices)} }}\n")
			f.write(f"    {{ rank=same; {' '.join(c_nodes_indices)} }}\n")
			# f.write("\n    // Invisible edges to enforce left-to-right order\n")
			# for i in range(len(ordered_nodes) - 1):
			# 	if ordered_nodes[i].startswith('l') and ordered_nodes[i+1].startswith('l'):
			# 		f.write(f"    {node_index_map[ordered_nodes[i]]} -- {node_index_map[ordered_nodes[i+1]]} [style=invis];\n")
			# 	elif ordered_nodes[i].startswith('c') and ordered_nodes[i+1].startswith('c'):
			# 		f.write(f"    {node_index_map[ordered_nodes[i]]} -- {node_index_map[ordered_nodes[i+1]]} [style=invis];\n")
			
			f.write("}\n")

		print(f"DOT saved in :'{dot_filename_label}'")



	# Graphe avec toutes les lignes colonnes
	if affichage['GLCall']: 
		timestamp = datetime.now().strftime("%m%d%Y%H%M%S")

		# l012 tokens format
		dot_filename = f"../lcres/agraph-lc-{timestamp}.dot"

		# Separate nodes into 'l' and 'c' groups
		l_nodes = [node for node in GLC.nodes if node.startswith('l')]
		c_nodes = [node for node in GLC.nodes if node.startswith('c')]

		with open(dot_filename, "a") as f:
			f.write("strict graph G {\n")
			f.write("    graph [splines=true, nodesep=0.5, rankdir=TB];\n")
			f.write("    node [shape=circle, fixedsize=true, width=0.4, fontsize=10];\n")

			# Add nodes with label, type, and preceds attributes
			for node in GLC.nodes:
				node_type = GLC.nodes[node].get('type', "")
				preceds = ",".join(map(str, GLC.nodes[node].get('preceds', [])))  # Join list if exists, else ""
				f.write(f'    {node} [label="{node}", type="{node_type}", preceds="{preceds}"];\n')

			# Add edges
			for node_a, node_b in GLC.edges:
				f.write(f'    {node_a} -- {node_b} ;\n')

			f.write("}\n")
			print(f"DOT saved in :'{dot_filename}'")

#################################################################################
		#indexes format 
		dot_filename = f"../lcres/aalc-{timestamp}.dot"

		# Create a mapping of nodes to their indices
		node_index_map = {node: str(i) for i, node in enumerate(GLC.nodes)}

		l_nodes_indices = [node_index_map[node] for node in GLC.nodes if node.startswith('l')]
		c_nodes_indices = [node_index_map[node] for node in GLC.nodes if node.startswith('c')]

		with open(dot_filename, "a") as f:
			f.write("strict graph G {\n")
			f.write("    graph [splines=true, nodesep=0.5, rankdir=TB];\n")
			f.write("    node [shape=circle, fixedsize=true, width=0.4, fontsize=10];\n")

			# Add nodes with indexed labels
			for node in GLC.nodes:
				node_type = GLC.nodes[node].get('type', "")
				node_card = GLC.nodes[node].get('card', "")
				#preceds = ",".join(map(str, GLC.nodes[node].get('preceds', [])))  # Join list if exists, else ""
				preceds = ",".join(node_index_map[p] for p in GLC.nodes[node].get('preceds', []) if p in node_index_map)
				index = node_index_map[node]  # Get index for the node
				f.write(f'    {index} [label="{index}", type="{node_type}", preceds="{preceds}", realname="{node}", card="{node_card}"];\n')

			# Add edges
			for node_a, node_b in GLC.edges:
				index_a = node_index_map[node_a]  # Get index for node_a
				index_b = node_index_map[node_b]  # Get index for node_b
				f.write(f'    {index_a} -- {index_b} ;\n')


			f.write("}\n")
			print(f"DOT saved in :'{dot_filename}'")


	# Hypergraphe version Stell
	if affichage['HS']:
		plt.figure("HyperGraphe lignes/colonnes max")
		pos = nx.spring_layout(HST)
		labels_lignes = [n for n, d in HST.nodes(data=True) if d["type"] == "l"]
		node_sizes = [len(n) * 300 for n in labels_lignes]
		nx.draw_networkx_nodes(HST, pos, nodelist=labels_lignes, node_size=node_sizes,
						   node_color="lightgray", node_shape="s")
		labels_colonnes = [n for n, d in HST.nodes(data=True) if d["type"] == "c"]
		node_sizes = [len(n) * 300 for n in labels_colonnes]
		nx.draw_networkx_nodes(HST, pos, nodelist=labels_colonnes, node_size=node_sizes,
						   node_color="lightgray", node_shape="d")
		labels_tokens = [n for n, d in HST.nodes(data=True) if d["type"] == "t"]
		nx.draw_networkx_nodes(HST, pos, nodelist=labels_tokens, node_size=1500,
						   node_color="lightgray", node_shape="o")

		nx.draw_networkx_edges(HST, pos, edge_color="black", arrowsize=20)
		nx.draw_networkx_labels(HST, pos, font_size=12, font_color="black")
		plt.savefig("HS.png")


	if affichage['imageGRed']:
		if positions == []:
		
			pos = {}
			for node in G.nodes():
				x, y = get_coordinates(node, taille_graphique)
				pos.update({node: (x, -y)})
		else:
			pos = {}
			for x in range(taille_graphique):
				for y in range(taille_graphique):
					if positions[x][y] != -1:
						pos.update({positions[x][y]: (y,-x)})
		plt.figure("Graphe de position réduit", figsize=(nb_nodes, nb_nodes))
		nx.draw(G, pos, with_labels=True, node_color="lightgray", linewidths=2.0, edge_color="black", node_size=1500,
			node_shape="o",connectionstyle="arc3,rad=0", font_size=18)
		plt.savefig("GRed.png")
		plt.show()
		plt.figure("Graphe de position (avec transitivité)", figsize=(nb_nodes, nb_nodes))
		nx.draw(GT, pos, with_labels=True, node_color="lightgray", edge_color="black", node_size=1500,
			connectionstyle="arc3,rad=0", font_size=18)
		#plt.savefig("GP.png")
		#plt.show()

	if affichage['imageGLCall']: 
		plt.figure("Graphe toutes lignes/colonnes")
		labels_lignes = [n for n, d in GLC.nodes(data=True) if d["type"] == "l"]
		node_sizes = [len(n) * 300 for n in labels_lignes]
		# Get initial layout
		pos = nx.bipartite_layout(GLC, labels_lignes)

		# Scale positions to increase spacing
		scale_factor = 3  # You can increase this value for more spacing
		pos = {k: (v[0] * scale_factor, v[1] * scale_factor) for k, v in pos.items()}
		nx.draw_networkx_nodes(GLC, pos, nodelist=labels_lignes, node_size=node_sizes,
						   node_color="lightgray", node_shape="o")
		labels_colonnes = [n for n, d in GLC.nodes(data=True) if d["type"] == "c"]
		node_sizes = [len(n) * 300 for n in labels_colonnes]
		nx.draw_networkx_nodes(GLC, pos, nodelist=labels_colonnes, node_size=node_sizes,
						   node_color="lightgray", node_shape="s")
		nx.draw_networkx_edges(GLC, pos, edge_color="black")
		nx.draw_networkx_labels(GLC, pos, font_size=12, font_color="black")
		plt.savefig("GLCall.png")
		plt.show()



if __name__ == '__main__':
	# parser = argparse.ArgumentParser(description='Process graph matching parameters.')
	# parser.add_argument('--nodes', type=int, default=20, help='Nodes of generated graph')

	# parser.add_argument('--grid', type=int, default=10, help='size of the square matrix')
	# args = parser.parse_args()

	# number_of_nodes = int(args.nodes)
	# grid= int(args.grid)
	number_of_nodes =600
	grid=70
	main()