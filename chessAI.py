import random
import numpy
import PieceSquareTables
import chessOpenings

pieceScore = {'K': 200, 'Q': 90, 'R': 50, 'B': 33, 'N': 32, 'P': 10}

CHECKMATE = 1000
STALEMATE = 0
DEPTH = 4
nextMove = None
counter = 0


def findRandomMove(validMoves):
    return validMoves[random.randint(0, len(validMoves) - 1)]


# iteration
def findBestMoveIteration(gameState, validMoves):
    turnMultiplier = 1 if gameState.whiteToMove else -1
    opponentMinMaxScore = CHECKMATE
    bestPlayerMove = None
    # playerMove - obecna tura, oppMove - przyszla tura
    random.shuffle(validMoves)
    for playerMove in validMoves:
        gameState.makeMove(playerMove)
        opponentsMoves = gameState.getValidMoves()
        if gameState.checkmate:
            opponentMaxScore = -CHECKMATE
        elif gameState.stalemate:
            opponentMaxScore = STALEMATE
        else:
            opponentMaxScore = -CHECKMATE
            for opponentsMove in opponentsMoves:
                gameState.makeMove(opponentsMove)
                gameState.getValidMoves()
                if gameState.checkmate:
                    score = CHECKMATE
                elif gameState.stalemate:
                    score = STALEMATE
                else:
                    score = -turnMultiplier * scoreMaterial(gameState.board)
                if score > opponentMaxScore:
                    opponentMaxScore = score
                    bestPlayerMove = playerMove
                gameState.undoMove()
        if opponentMaxScore < opponentMinMaxScore:
            opponentMinMaxScore = opponentMaxScore
            bestPlayerMove = playerMove
        gameState.undoMove()
    return bestPlayerMove


def findBestMove(gameState, validMoves, returnQueue, playerOne, playerTwo):
    global nextMove, counter
    # random.shuffle(validMoves)
    counter = 0
    # print('gameState.moveCounter ' + str(gameState.moveCounter))
    if gameState.moveCounter < 3 and nextMove is None:
        nextMove = chessOpenings.makeOpening(gameState, playerOne, playerTwo)
    # findMoveNegaMax(gameState, validMoves, DEPTH, 1 if gameState.whiteToMove else -1)
    if nextMove is None:
        if gameState.getNumberOfPiecesOnBoard() < 9:
            findMoveNegaMaxAlphaBeta(gameState, validMoves, ++++DEPTH, -CHECKMATE, CHECKMATE,
                                     1 if gameState.whiteToMove else -1)
        elif gameState.getNumberOfPiecesOnBoard() < 18:
            findMoveNegaMaxAlphaBeta(gameState, validMoves, ++DEPTH, -CHECKMATE, CHECKMATE,
                                     1 if gameState.whiteToMove else -1)
        else:
            findMoveNegaMaxAlphaBeta(gameState, validMoves, DEPTH, -CHECKMATE, CHECKMATE,
                                     1 if gameState.whiteToMove else -1)
    print(counter)
    returnQueue.put(nextMove)


# recursion MinMax algorythm
def findMoveMinMax(gameState, validMoves, depth, whiteToMove):
    global nextMove
    if depth == 0:
        return scoreMaterial(gameState.board)

    if whiteToMove:
        maxScore = -CHECKMATE
        for move in validMoves:
            gameState.makeMove(move)
            nextMoves = gameState.getValidMoves()
            score = findMoveMinMax(gameState, nextMoves, depth - 1, False)
            if score > maxScore:
                maxScore = score
                if depth == DEPTH:
                    nextMove = move
            gameState.undoMove()
        return maxScore

    else:
        minScore = CHECKMATE
        for move in validMoves:
            gameState.makeMove(move)
            nextMoves = gameState.getValidMoves()
            score = findMoveMinMax(gameState, nextMoves, depth - 1, True)
            if score < minScore:
                minScore = score
                if depth == DEPTH:
                    nextMove = move
            gameState.undoMove()
        return minScore


def findMoveNegaMax(gameState, validMoves, depth, turnMultiplier):
    global nextMove, counter
    counter += 1
    if depth == 0:
        return turnMultiplier * scoreBoard(gameState)

    maxScore = -CHECKMATE
    for move in validMoves:
        gameState.makeMove(move)
        nextMoves = gameState.getValidMoves()
        score = -findMoveNegaMax(gameState, nextMoves, depth - 1, -turnMultiplier)
        if score > maxScore:
            maxScore = score
            if depth == DEPTH:
                nextMove = move
        gameState.undoMove()
    return maxScore


# NegaMax with AlphaBeta Pruning
def findMoveNegaMaxAlphaBeta(gameState, validMoves, depth, alpha, beta, turnMultiplier):
    global nextMove, counter
    counter += 1
    if depth == 0:
        return turnMultiplier * scoreBoard(gameState)
    # move ordering - implement later
    maxScore = -CHECKMATE

    for move in validMoves:
        gameState.makeMove(move)
        nextMoves = gameState.getValidMoves()
        # if len(nextMoves) > 25:
        #     nextMoves = getSortedMoves(gameState, nextMoves)
        nextMoves = getSortedMoves(gameState, nextMoves)
        score = -findMoveNegaMaxAlphaBeta(gameState, nextMoves, depth - 1, -beta, -alpha, -turnMultiplier)
        if score > maxScore:
            maxScore = score
            if depth == DEPTH:
                nextMove = move
                # print(move, score)
        gameState.undoMove()
        if maxScore > alpha:  # prunning
            alpha = maxScore
        if alpha >= beta:
            break
    return maxScore


def getSortedMoves(gameState, moves):
    scores = []
    for move in moves:
        gameState.makeMove(move)
        scores.append(scoreBoard(gameState))
        gameState.undoMove()
    A = numpy.array(moves)
    B = numpy.array(scores)
    inds = B.argsort()
    sorted_moves = A[inds]
    sorted_moves = sorted_moves[::-1]
    # cut = len(sorted_moves) // 4
    sorted_moves = sorted_moves[:(len(sorted_moves))]
    # print(repr(B[inds]))
    # return sorted_moves[:(len(sorted_moves)-cut)]
    # print(repr(inds))
    return sorted_moves


'''
jeśli score > 0 to git dla białych, score < 0 to git czarnych
'''


def scoreBoard(gameState):
    if gameState.checkmate:
        if gameState.whiteToMove:
            return -CHECKMATE
        else:
            return CHECKMATE
    elif gameState.stalemate:
        return STALEMATE

    score = scoreMaterial(gameState.board)
    for row in range(len(gameState.board)):
        for column in range(len(gameState.board[row])):
            square = gameState.board[row][column]
            if square == '--':
                break
            # score it positionally
            piecePositionScore = 0
            pieceCastlingScore = 0
            if square[1] == 'P' and square[0] == 'w':
                piecePositionScore = PieceSquareTables.whitePawnTable[row][column]
            elif square[1] == 'P' and square[0] == 'b':
                piecePositionScore = PieceSquareTables.blackPawnTable[row][column]
            elif square[1] == 'N':
                piecePositionScore = PieceSquareTables.KnightTable[row][column]
            elif square[1] == 'B':
                piecePositionScore = PieceSquareTables.BishopTable[row][column]
            elif square[1] == 'R':
                piecePositionScore = PieceSquareTables.RookTable[row][column]
            elif square[1] == 'K':
                if square[0] == 'w':
                    piecePositionScore = PieceSquareTables.whiteKingTable[row][column]
                    pieceCastlingScore = scoreCastling(gameState, 'w')
                else:
                    piecePositionScore = PieceSquareTables.blackKingTable[row][column]
                    pieceCastlingScore = scoreCastling(gameState, 'b')
            elif square[1] == 'Q':
                piecePositionScore = PieceSquareTables.KnightTable[row][column]

            pawnStructureScore = 0
            # score Pawn structure
            if square[1] == 'P':
                pawnStructureScore = scorePawnStructure(gameState, row, column)

            if square[0] == 'w':
                score += pieceScore[square[1]] + piecePositionScore // 5 + pawnStructureScore + pieceCastlingScore
            elif square[0] == 'b':
                score -= pieceScore[square[1]] + piecePositionScore // 5 + pawnStructureScore + pieceCastlingScore

    return score


'''
Score the board based on material
'''


def scoreMaterial(board):
    score = 0
    for row in board:
        for square in row:
            if square[0] == 'w':
                score += pieceScore[square[1]]
            elif square[0] == 'b':
                score -= pieceScore[square[1]]

    return score


def scorePawnStructure(gameState, row, column):
    score = 0
    isChanged = False
    if 0 < row < 7 and 0 < column < 7:
        for i in range(-1, 1):
            for j in range(-1, 1):
                if gameState.board[row + i][row + j] == 'wP' and gameState.whiteToMove or gameState.board[row + i][
                    row + j] == 'bP' \
                        and not gameState.whiteToMove:
                    if i != row and j != column:
                        if i == j or abs(i - j) == 2:
                            score += 5
                            isChanged = True
                        elif i == row:
                            score += 2
                            isChanged = True
                        elif j == column:
                            score -= 10
                            isChanged = True

    elif 7 > row > 0 == column:
        if gameState.board[row][column + 1] == 'wP' and gameState.whiteToMove or gameState.board[row][
            column + 1] == 'bP' \
                and not gameState.whiteToMove:
            score += 2
            isChanged = True
        if gameState.board[row + 1][column + 1] == 'wP' and gameState.whiteToMove or gameState.board[row + 1][
            column + 1] == 'bP' \
                and not gameState.whiteToMove:
            score += 3
            isChanged = True
    elif 0 < row < 7 == column:
        if gameState.board[row][column - 1] == 'wP' and gameState.whiteToMove or gameState.board[row][
            column - 1] == 'bP' \
                and not gameState.whiteToMove:
            score += 2
            isChanged = True
        if gameState.board[row + 1][column - 1] == 'wP' and gameState.whiteToMove or gameState.board[row + 1][
            column - 1] == 'bP' \
                and not gameState.whiteToMove:
            score += 3
            isChanged = True

    if not isChanged:
        score -= 5

    return score


# punish and reward Castling
def scoreCastling(gameState, kingColor):
    score = 0
    if kingColor == 'w':
        if not gameState.currentCastlingRight.wks:
            score -= 5
        if not gameState.currentCastlingRight.wqs:
            score -= 5
        return score
    elif kingColor == 'b':
        if not gameState.currentCastlingRight.bks:
            score -= 5
        if not gameState.currentCastlingRight.bqs:
            score -= 5
        return score
    else:
        return 0
