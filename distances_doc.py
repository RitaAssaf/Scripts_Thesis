from pycsp3 import *
distances = [
[0, 5, 6, 6, 6],
[5, 0, 9, 8, 4],
[6, 9, 0, 1, 7],
[6, 8, 1, 0,6],
[6, 4, 7, 6,0]
]
nCities = len ( distances )
# c [ i ] is the ith city of the tour
c = VarArray ( size = nCities , dom = range ( nCities ))
# d [ i ] is the distance between the cities i and i +1 chosen in the tour
d = VarArray ( size = nCities , dom = distances )
satisfy (
# Visiting each city only once
AllDifferent ( c )
)
if not variant ():
	satisfy (
	# computing the distance between any two successive cities in the tour
	distances [ c [ i ]][ c [ i + 1]] == d [ i ] for i in range ( nCities )
	)
elif variant ( " table " ):
	T = {( i , j , distances [ i ][ j ]) for i in range ( nCities ) for j in range ( nCities )}
	satisfy (
	# computing the distance between any two successive cities in the tour
	( c [ i ] , c [ i + 1] , d [ i ]) in T for i in range ( nCities )
	)

minimize (
# minimizing the traveled distance
Sum ( d )
)