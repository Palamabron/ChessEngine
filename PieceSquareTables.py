#od 0 do 50
import numpy

whitePawnTable = numpy.array([
    [50, 50, 50, 50, 50, 50, 50, 50],
    [40, 40, 40, 40, 40, 40, 40, 40],
    [35, 35, 35, 35, 35, 35, 35, 35],
    [30, 30, 30, 30, 30, 30, 30, 30],
    [10, 10, 15, 40, 40, 15, 10, 10],
    [30, 10, 20, 30, 30, 20, 10, 30],
    [10, 10, 10,  5,  5, 10, 10, 10],
    [ 0,  0,  0,  0,  0,  0,  0,  0]
])

blackPawnTable = numpy.array([
    [ 0,  0,  0,  0,  0,  0,  0,  0],
    [10, 10, 10,  5,  5, 10, 10, 10],
    [30, 10, 20, 30, 30, 20, 10, 30],
    [10, 10, 15, 40, 40, 15, 10, 10],
    [30, 30, 30, 30, 30, 30, 30, 30],
    [35, 35, 35, 35, 35, 35, 35, 35],
    [40, 40, 40, 40, 40, 40, 40, 40],
    [50, 50, 50, 50, 50, 50, 50, 50]
])


KnightTable = numpy.array([
    [10,  0, 10, 10, 10, 10,  0, 10],
    [10, 20, 20, 20, 20, 20, 20, 10],
    [10, 20, 40, 35, 35, 40, 20, 10],
    [10, 20, 35, 20, 20, 35, 20, 10],
    [10, 20, 35, 20, 20, 35, 20, 10],
    [10, 20, 35, 35, 35, 35, 20, 10],
    [10, 20, 20, 20, 20, 20, 20, 10],
    [10,  0, 10, 10, 10, 10,  0, 10]
])



BishopTable = numpy.array([
    [30, 30,  20, 10, 10, 20, 30, 30],
    [30, 40,  30, 20, 20, 30, 40, 30],
    [20, 10,  40, 10, 10, 40, 10, 20],
    [10,  0,  10, 20, 20, 10,  0, 10],
    [10,  0,  10, 20, 20, 10,  0, 10],
    [20, 10,  40, 10, 10, 40, 10, 20],
    [30, 40,  30, 20, 20, 30, 40, 30],
    [30, 20,  10, 10, 10, 10, 20, 30]
])



RookTable = numpy.array([
    [40, 30, 40, 40, 40, 40, 30, 40],
    [40, 40, 40, 40, 40, 40, 40, 40],
    [10, 10, 20, 20, 20, 20, 10, 10],
    [10, 10, 10, 10, 10, 10, 10, 10],
    [10, 10, 10, 10, 10, 10, 10, 10],
    [10, 10, 20, 20, 20, 20, 10, 10],
    [40, 40, 40, 40, 40, 40, 40, 40],
    [40, 30, 40, 40, 40, 40, 30, 40]
])


QueenTable = numpy.array([
    [10, 10, 10, 30, 10, 10, 10, 10],
    [10, 10, 30, 30, 30, 30, 10, 10],
    [10, 40, 30, 30, 30, 40, 20, 10],
    [10, 20, 30, 30, 30, 30, 20, 10],
    [10, 20, 30, 30, 30, 30, 20, 10],
    [10, 20, 30, 30, 30, 30, 20, 10],
    [10, 40, 20, 30, 30, 10, 40, 10],
    [10, 10, 10, 30, 10, 10, 10, 10]
])


whiteKingTable = numpy.array([
    [ 0,   0,   0,   0,   0,   0,  0,  0],
    [ 0,   0,   0,   0,   0,   0,  0,  0],
    [ 0,   0,   0,   0,   0,   0,  0,  0],
    [ 0,   0,   0,   0,   0,   0,  0,  0],
    [ 0,   0,   0,   0,   0,   0,  0,  0],
    [ 0,   0,   0,   0,   0,   0,  0,  0],
    [5,   10,   0, -10, -10, -10, 10,  5],
    [20,  20,  30, -10,  10, -10, 30, 20]
])

blackKingTable = numpy.array([
    [20, 20,  30, -10,  10, -10, 30, 20],
    [ 5, 10,   0, -10, -10, -10, 10,  5],
    [ 0,  0,   0,   0,   0,   0,  0,  0],
    [ 0,  0,   0,   0,   0,   0,  0,  0],
    [ 0,  0,   0,   0,   0,   0,  0,  0],
    [ 0,  0,   0,   0,   0,   0,  0,  0],
    [ 0,  0,   0,   0,   0,   0,  0,  0],
    [ 0,  0,   0,   0,   0,   0,  0,  0]
])

