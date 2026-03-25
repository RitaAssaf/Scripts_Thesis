import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
from itertools import combinations
import random

def extraction_arcs(mat:list[list],lab:str):
	# lit une liste de liste pour extraire des arcs sur chaque ligne dont le label est lab
	arc_ext=[]
	for li in mat:
		i = 0
		while i < len(li) - 1:
			if li[i] != 0:
				j = i + 1
				while j < len(li) and li[j] == 0:
					j = j + 1
				if j < len(li):
					arc_ext.append((li[i], li[j], {'label': lab}))
				i = j
			else:
				i = i + 1
	return arc_ext

def cloture_reflexive(G,lab:str):
	for noeud in G.nodes():
		G.add_edge(noeud, noeud)
		G[noeud][noeud]['label']=lab
	return G

def cloture_transitive(G,lab:str):
	G_cloture = nx.transitive_closure(G)
	# Copier les attributs des arêtes du graphe d'origine vers le graphe de la clôture
	for u,v in G_cloture.edges():
		if 'label' not in G_cloture[u][v]:
			G_cloture[u][v]['label'] = lab
	return G_cloture

def aplatir_liste(liste_imbriquee):
	resultat = []
	for i in liste_imbriquee:
		for e in i:
			resultat.append(e)
	return resultat


def all_sublists(lst):
	sublists = []
	for i in range(len(lst) + 1):
		sublists.extend([list(sub) for sub in combinations(lst, i)])
	sublists.remove([])
	return sublists


def get_coordinates(v, n):
	j = (v - 1) // n
	i = (v - 1) % n
	return (i, j)


def nommer(l, label):
	s = "".join(map(str, l))
	return label + s

def numerote(mat:list[list]):
	compteur = 1  # Initialisation du compteur
	for i in range(len(mat)):
		for j in range(len(mat[i])):
			if mat[i][j] == 1:
				mat[i][j] = compteur
				compteur += 1
	return mat


def generer_positions_alea(n, p):

	mat = [[0] * n for _ in range(n)]
	places = random.sample(range(n * n), p)
	# Placer les 1
	for pl in places:
		i, j = divmod(pl, n)  # Convertir index 1D en 2D
		mat[i][j] = 1
	return mat


def main():
	# instance
	positions = [[1, 1, 1, 1],
				[1, 1, 1, 0],
				[1, 1, 1, 0],
			   [0, 1, 0, 0]]

	#positions = generer_positions_alea(10,50)
	positions = numerote(positions)

	#traitement de l'instance et mise en forme des paramètres (taille, arcs...)
	nb_nodes = sum(1 for li in positions for val in li if val != 0)
	taille_graphique = len(positions)
	positionsT = list(map(list, zip(*positions)))
	arcs = extraction_arcs(positions,'h')+extraction_arcs(positionsT,'v')

	arcs_h = [arc for arc in arcs if arc[2]['label'] == 'h']
	arcs_v = [arc for arc in arcs if arc[2]['label'] == 'v']

	sup_ligcol=True #pour ne pas afficher les lignes colonnes de taille 1 dans le GLC

	# création du graphe de position réduit
	G = nx.DiGraph()
	for n in range(nb_nodes):
		G.add_node(n + 1, type='t'),
	G.add_edges_from(arcs)

	for n in G.nodes():
		G.nodes[n]["color"] = "orange" if n in (1, 2) else "lightgray"


	# graphe avec arcs horizontaux
	GH = nx.DiGraph()
	GH.add_nodes_from(range(1, nb_nodes+1))
	GH.add_edges_from(arcs_h)
	# graphe avec arcs verticaux
	GV = nx.DiGraph()
	GV.add_nodes_from(range(1, nb_nodes+1))
	GV.add_edges_from(arcs_v)

	#Graphe de position (avec transitivité)
	GHT = cloture_transitive(GH,'h')
	GVT = cloture_transitive(GV,'v')
	GT = nx.compose(GHT, GVT)

	
	for n in GT.nodes():
		GT.nodes[n]["color"] = "lightgray"
		#GT.nodes[n]["color"] = "orange" if n in (1, 2,5,6) else "lightgray"



	# Extraction des lignes et colonnes
	lignes = list(nx.find_cliques(GHT.to_undirected()))
	colonnes = list(nx.find_cliques(GVT.to_undirected()))

	all_lignes = []
	for li in lignes:
		all_lignes.append(all_sublists(li))
	all_colonnes = []
	for co in colonnes:
		all_colonnes.append(all_sublists(co))
	all_colonnes = aplatir_liste(all_colonnes)
	all_lignes = aplatir_liste(all_lignes)
	# Supression des lignes et colonnes de taille 1 pour la visibilité
	if sup_ligcol:
		all_lignes=[li for li in all_lignes if len(li) > 1]
		all_colonnes = [col for col in all_colonnes if len(col) > 1]

	# création du graphe lignes/colonnes maximales
	GLC_max = nx.Graph()
	GLC_max.add_nodes_from([(nommer(li, 'l'), {'type': 'l'}) for li in lignes])
	GLC_max.add_nodes_from([(nommer(co, 'c'), {'type': 'c'}) for co in colonnes])
	for li in lignes:
		for co in colonnes:
			if set(li) & set(co):
				GLC_max.add_edge(nommer(li, 'l'), nommer(co, 'c'))

	# création du graphe avec toutes lignes/colonnes
	GLC = nx.Graph()
	GLC.add_nodes_from([(nommer(li, 'l'), {'type': 'l'}) for li in all_lignes])
	GLC.add_nodes_from([(nommer(co, 'c'), {'type': 'c'}) for co in all_colonnes])
	for li in all_lignes:
		for co in all_colonnes:
			if set(li) & set(co):
				GLC.add_edge(nommer(li, 'l'), nommer(co, 'c'))

	# création de l'hypergraphe de Stell avec uniquement les lignes et colonnes complètes
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
				HST.add_edge(nommer(co, 'c'), n)

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
		for x in range(taille_graphique):
			for y in range(taille_graphique):
				if positions[x][y] != 0:
					pos.update({positions[x][y]: (y,-x)})
	
	# Choix des affichages 

	affichage={'GP':True,'GLCRed':False,'GLCall':False,'HS':False}

	# Affichage des deux graphes de positions (réduit et avec transitivité
	if affichage['GP']:
		node_colors = [G.nodes[n]["color"] for n in G.nodes()]

		plt.figure("Graphe de position (avec transitivité)", figsize=(nb_nodes, nb_nodes))
		node_colors = [GT.nodes[n]["color"] for n in GT.nodes()]
		nx.draw_networkx_nodes(GT, pos, node_color=node_colors, node_size=2000)
		nx.draw_networkx_edges(
			GT,
			pos,
			edgelist=GT.edges(),
			edge_color="gray",
			connectionstyle="arc3,rad=-0.2",
			arrows=True,
			arrowstyle='-|>',
			arrowsize=14,
			node_size=2000  # important when nodes are large
		)
		nx.draw_networkx_labels(GT, pos, font_size=18)
		# nx.draw(GT, pos, with_labels=True, node_color=node_colors,
		# 		edge_color="gray", node_size=1000,connectionstyle="arc3,rad=-0.2")
		plt.savefig("GP.png")
		plt.show()

	# Graphe avec lignes et colonnes
	if affichage['GLCRed']:
		bilignes=[l for l,d in GLC_max.nodes(data=True) if d["type"]=='l']
		pos = nx.bipartite_layout(GLC_max,bilignes)
		plt.figure("Graphe lignes/colonnes max")
		nx.draw(GLC_max, pos, with_labels=True, node_color="lightgray", edge_color="gray",
				node_size=1000)
		plt.savefig("GLCRed.png")
		plt.show()

	# Graphe avec toutes les lignes colonnes
	if affichage['GLCall']: 
		plt.figure("Graphe toutes lignes/colonnes")
		labels_lignes = [n for n, d in GLC.nodes(data=True) if d["type"] == "l"]
		node_sizes = [len(n) * 300 for n in labels_lignes]
		pos = nx.bipartite_layout(GLC, labels_lignes)
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
		nx.draw_networkx_nodes(HST, pos, nodelist=labels_tokens, node_size=500,
						   node_color="lightgray", node_shape="o")

		nx.draw_networkx_edges(HST, pos, edge_color="black", arrowsize=20)
		nx.draw_networkx_labels(HST, pos, font_size=12, font_color="black")
		plt.savefig("HS.png")
		plt.show()


if __name__ == '__main__':
	main()
