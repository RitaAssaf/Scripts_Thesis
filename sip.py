safrom enum import Enum, auto
from pycsp3 import *

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

	# =============== CONSTRAINT

	satisfy(

		# Map all nodes from graph 1
		AllDifferent(I),

		[
			Exist(
					(I[E1[e1][0]] == E2[e2][p]) & (I[E1[e1][1]] == E2[e2][(p + 1) % 2]) #1 ou 0
					and I[E1[e1][0]]==1
				for e2 in range(NE_2) for p in range(2) if A1[e1] == A2[e2]
			) for e1 in range(NE_1)
		]

		#bidirection
		#[
        #    Or(
        #        (I[E1[e][0] - 1], I[E1[e][1] - 1]) in E2,  # Direction 1
        #        (I[E1[e][1] - 1], I[E1[e][0] - 1]) in E2   # Direction 2
        #    )
        #    for e in range(NE_1)
        #]
	)

	#print(posted())
	return I
