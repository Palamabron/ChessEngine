import random

import ChessEngine


def makeOpening(gameState, playerOne, playerTwo):
    currentBoard = gameState.getFENnotation()
    move = None
    # białe ai
    if gameState.whiteToMove and not playerOne:
        # 1 ruch
        if currentBoard == 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR':  # if beginning
            tmp = random.randint(1, 3)
            if tmp == 1:
                move = ChessEngine.Move(cordToTuple('d2'), cordToTuple('d4'), gameState.board)  # 1. d4
            elif tmp == 2:
                move = ChessEngine.Move(cordToTuple('e2'), cordToTuple('e4'), gameState.board)  # 1. e4
            elif tmp == 3:
                move = ChessEngine.Move(cordToTuple('c2'), cordToTuple('c4'), gameState.board)  # 1. c4
        # 3 ruch gdzie 1. e4
        elif currentBoard == 'rnbqkbnr/pp1ppppp/8/2p5/4P3/8/PPPP1PPP/RNBQKBNR':  # if 2. c5
            move = ChessEngine.Move(cordToTuple('g1'), cordToTuple('f3'), gameState.board)  # 3. Nf3
        elif currentBoard == 'rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR':  # if 2. e5
            move = ChessEngine.Move(cordToTuple('g1'), cordToTuple('f3'), gameState.board)  # 3. Nf3
        elif currentBoard == 'rnbqkbnr/pp1ppppp/8/2p5/4P3/8/PPPP1PPP/RNBQKBNR':  # if 2. c5
            move = ChessEngine.Move(cordToTuple('g1'), cordToTuple('f3'), gameState.board)  # 3. Nf3
    # czarne ai
    elif not gameState.whiteToMove and not playerTwo:
        # 2 ruch
        if currentBoard == 'rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR':  # if 1. e4
            move = ChessEngine.Move(cordToTuple('c7'), cordToTuple('c5'), gameState.board)  # 2. c5
        elif currentBoard == 'rnbqkbnr/pppppppp/8/8/3P4/8/PPP1PPPP/RNBQKBNR':  # if 1. d4
            move = ChessEngine.Move(cordToTuple('g8'), cordToTuple('f6'), gameState.board)  # 2. Nf6
        elif currentBoard == 'rnbqkbnr/pppppppp/8/8/2P5/8/PP1PPPPP/RNBQKBNR':  # if 1. c4
            move = ChessEngine.Move(cordToTuple('g8'), cordToTuple('f6'), gameState.board)  # 2. Nf6
        # 3 ruch
        elif currentBoard == 'rnbqkbnr/pp1ppppp/8/2p5/4P3/5N2/PPPP1PPP/RNBQKB1R':  # if 3. Nf3
            move = ChessEngine.Move(cordToTuple('d7'), cordToTuple('d6'), gameState.board)  # 4. d6
    return move


def cordToTuple(location):
    tupleCoords = []
    filesToCols = {'h': 7, 'g': 6, 'f': 5, 'e': 4,
                   'd': 3, 'c': 2, 'b': 1, 'a': 0}
    ranksToRows = {'1': 7, '2': 6, '3': 5, '4': 4,
                   '5': 3, '6': 2, '7': 1, '8': 0}
    tupleCoords.append(ranksToRows.get(location[1]))
    tupleCoords.append(filesToCols.get(location[0]))
    tupleCoords = tuple(tupleCoords)
    return tupleCoords
