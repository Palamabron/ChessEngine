import random


def generateNumberForBoard():
    figures = [
        'wP', 'wB', 'wR', 'wN', 'wK', 'wQ',
        'bP', 'bB', 'bR', 'bN', 'bK', 'bQ'
    ]
    numbers = [[[random.randint(900_000, 1_000_000) for _ in range(12)] for _ in range(8)] for _ in range(8)]
    enpassant = [random.randint(900_000, 1_000_000) for _ in range(8)]
    castlingRights = [random.randint(900_000, 1_000_000) for _ in range(4)]
    for row in numbers:
        for bow in row:
            print(bow)
    return numbers


def generateHash(gameState, numbers):
    hashNumber = 0
    for i in range(len(gameState.board)):
        for j in range(len(gameState.board)):
            if gameState.board[i][j] == 'wP':
                hashNumber ^= numbers[i][j][0]
            elif gameState.board[i][j] == 'wB':
                hashNumber ^= numbers[i][j][1]
            elif gameState.board[i][j] == 'wR':
                hashNumber ^= numbers[i][j][2]
            elif gameState.board[i][j] == 'wN':
                hashNumber ^= numbers[i][j][3]
            elif gameState.board[i][j] == 'wK':
                hashNumber ^= numbers[i][j][4]
            elif gameState.board[i][j] == 'wQ':
                hashNumber ^= numbers[i][j][5]
            elif gameState.board[i][j] == 'bP':
                hashNumber ^= numbers[i][j][6]
            elif gameState.board[i][j] == 'bB':
                hashNumber ^= numbers[i][j][7]
            elif gameState.board[i][j] == 'bR':
                hashNumber ^= numbers[i][j][8]
            elif gameState.board[i][j] == 'bN':
                hashNumber ^= numbers[i][j][9]
            elif gameState.board[i][j] == 'bK':
                hashNumber ^= numbers[i][j][10]
            elif gameState.board[i][j] == 'bQ':
                hashNumber ^= numbers[i][j][11]
    return hashNumber


generateNumberForBoard()
