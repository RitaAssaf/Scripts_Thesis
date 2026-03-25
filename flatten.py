from pycsp3 import *


x = VarArray ( size =[3 ,3] , dom = lambda i , j : {0 ,1} if i >= j else None )
print ( " x : " , x )
print ( " x[0] : " , x[0] )
print ( " x flattened : " , flatten ( x ))