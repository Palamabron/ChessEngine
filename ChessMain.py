"""
User input and display
"""
import math

import pygame as p
import ChessEngine
from playsound2 import playsound
from threading import Thread
from multiprocessing import Process, Queue
import chessAI
import time

BOARD_WIDTH = BOARD_HEIGHT = 512  # lub 400
MOVE_LOG_PANEL_WIDTH = 490
MOVE_LOG_PANEL_HEIGHT = BOARD_HEIGHT
DIMENSION = 8
SQ_SIZE = BOARD_HEIGHT // DIMENSION
MAX_FPS = 20
IMAGES = {}
p.display.set_caption("chess engine")


def loadImages():
    pieces = ['bR', 'bB', 'bN', 'bQ', 'bK', 'bP', 'wP', 'wR', 'wB', 'wN', 'wQ', 'wK']
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("img/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))


def main():
    p.init()
    screen = p.display.set_mode((BOARD_WIDTH + MOVE_LOG_PANEL_WIDTH, BOARD_HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    gameState = ChessEngine.GameState()
    validMoves = gameState.getValidMoves()
    moveLogFont = p.font.SysFont('Arial', 24, False, False)
    moveMade = False  # valid move
    animate = False
    loadImages()  # only once
    running = True
    sqSelected = ()  # no square is selected (row, col)
    playerClicks = []  # two tuples np. [(6, 4) (4, 4)] (od do)
    moveIterator = 1
    gameOver = False
    playerOne = 1  # if human playing white is True, if ai white false
    playerTwo = 0  # if human playing black is True, if ai black false
    AIThinking = False
    moveFinderProcess = None
    isMoveUndone = False
    # if playerOne=playerTwo=False then is ai vs ai
    while running:
        isHumanTurn = (gameState.whiteToMove and playerOne) or (not gameState.whiteToMove and playerTwo)
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            elif e.type == p.MOUSEBUTTONDOWN:
                if not gameOver:
                    location = p.mouse.get_pos()  # (x, y) of mouse
                    col = location[0] // SQ_SIZE
                    row = location[1] // SQ_SIZE
                    if sqSelected == (row, col) or col >= 8:  # if user clicked twice or mouse log click
                        sqSelected = ()  # deselect
                        playerClicks = []  # clear clicks
                    else:
                        sqSelected = (row, col)
                        playerClicks.append(sqSelected)
                    # if user first click was empty square
                    if len(playerClicks) == 1 and gameState.board[sqSelected[0]][sqSelected[1]] == "--":
                        playerClicks = []
                        sqSelected = ()
                    if len(playerClicks) == 2 and isHumanTurn:  # if second click:
                        move = ChessEngine.Move(playerClicks[0], playerClicks[1], gameState.board)
                        if move in gameState.getValidMoves():
                            # tu dac funkcje z dzwiekiem =============================================
                            playSound(move, gameState, gameOver)
                            if move.pieceMoved[1] != "P":
                                print(f"{moveIterator}. {move.pieceMoved[1]}{move.getChessNotation()}")
                            else:
                                print(f"{moveIterator}. {move.getChessNotation()}")
                            # print(f"MoveLog: {repr(gameState.moveLog)}")
                            moveIterator += 1
                        for i in range(len(validMoves)):
                            if move == validMoves[i]:
                                gameState.makeMove(validMoves[i])
                                moveMade = True
                                animate = True
                                sqSelected = ()
                                playerClicks = []
                                break
                        if moveMade:
                            makeCheckSound(gameState)
                            gameState.moveCounter += 1
                        else:
                            playerClicks = [sqSelected]

            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:  # undo when "z" is pressed
                    gameState.undoMove()
                    moveMade = True
                    animate = False
                    gameOver = False
                    if AIThinking:
                        moveFinderProcess.terminate()
                        AIThinking = False
                    isMoveUndone = True
                if e.key == p.K_r:  # reset
                    gameState = ChessEngine.GameState()
                    validMoves = gameState.getValidMoves()
                    sqSelected = ()
                    playerClicks = []
                    moveMade = False
                    animate = False
                    gameOver = False
                    if AIThinking:
                        moveFinderProcess.terminate()
                        AIThinking = False
                    isMoveUndone = True

        # AI move finder
        if not gameOver and not isHumanTurn and not isMoveUndone:
            if not AIThinking:
                AIThinking = True
                print("thinking...")
                returnQueue = Queue()  # pass data between threads
                moveFinderProcess = Process(target=chessAI.findBestMove, args=(gameState, validMoves, returnQueue, playerOne, playerTwo))
                moveFinderProcess.start()  # call func parallely

            if not moveFinderProcess.is_alive():
                print("done thinking")
                AIMove = returnQueue.get()
                if AIMove is None:
                    AIMove = chessAI.findRandomMove(gameState.getValidMoves())
                gameState.makeMove(AIMove)
                # playSound(AIMove, gameState, gameOver)
                moveMade = True
                animate = True
                AIThinking = False

        if moveMade:
            if animate:
                animateMove(gameState.moveLog[-1], screen, gameState.board, clock)
            validMoves = gameState.getValidMoves()
            moveMade = False
            animate = False
            isMoveUndone = False

        drawGameState(screen, gameState, validMoves, sqSelected, moveLogFont)

        if gameState.checkmate or gameState.stalemate:
            gameOver = True
            text = 'Stalemate' if gameState.stalemate else 'Black wins by checkmate' if gameState.whiteToMove else 'Black wins by checkmate '
            drawEndGameText(screen, text)

        clock.tick(MAX_FPS)
        p.display.flip()


# draw graphics
def drawGameState(screen, gameState, validMoves, sqSelected, moveLogFont):
    drawBoard(screen)  # draw sq on board
    highlightSquares(screen, gameState, validMoves, sqSelected)  # draw pieces highlighting
    drawPieces(screen, gameState.board)  # draw pieces
    drawMoveLog(screen, gameState, moveLogFont)


def drawBoard(screen):
    global colors
    colors = [p.Color("white"), p.Color("gray")]
    for row in range(DIMENSION):
        for column in range(DIMENSION):
            color = colors[((row + column) % 2)]
            p.draw.rect(screen, color, p.Rect(column * SQ_SIZE, row * SQ_SIZE, SQ_SIZE, SQ_SIZE))


def highlightSquares(screen, gameState, validMoves, sqSelected):
    if sqSelected != ():
        row, column = sqSelected
        if gameState.board[row][column][0] == ('w' if gameState.whiteToMove else 'b'):
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            a = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(100)
            a.set_alpha(100)
            s.fill(p.Color('blue'))
            a.fill(p.Color('red'))
            screen.blit(s, (column * SQ_SIZE, row * SQ_SIZE))
            s.fill(p.Color('yellow'))
            for move in validMoves:
                if move.startRow == row and move.startCol == column:
                    if gameState.board[move.endRow][move.endCol] == '--' and not move.isEnpassantMove:
                        screen.blit(s, (move.endCol * SQ_SIZE, move.endRow * SQ_SIZE))
                    else:
                        screen.blit(a, (move.endCol * SQ_SIZE, move.endRow * SQ_SIZE))


def drawPieces(screen, board):
    for row in range(DIMENSION):
        for column in range(DIMENSION):
            piece = board[row][column]
            if piece != "--":
                screen.blit(IMAGES[piece], p.Rect(column * SQ_SIZE, row * SQ_SIZE, SQ_SIZE, SQ_SIZE))


def drawMoveLog(screen, gameState, font):
    moveLogRect = p.Rect(BOARD_WIDTH, 0, MOVE_LOG_PANEL_WIDTH, MOVE_LOG_PANEL_HEIGHT)
    p.draw.rect(screen, p.Color('black'), moveLogRect)
    moveLog = gameState.moveLog
    moveTexts = []
    for i in range(0, len(moveLog), 2):
        moveString = str(i // 2 + 1) + ". " + str(moveLog[i]) + " "
        if i + 1 < len(moveLog):
            moveString += str(moveLog[i + 1]) + "    "
        moveTexts.append(moveString)
    movesPerRow = 4
    padding = 5
    lineSpacing = 2
    textY = padding
    for i in range(0, len(moveTexts), movesPerRow):
        text = ""
        for j in range(movesPerRow):
            if i + j < len(moveTexts):
                text += moveTexts[i + j]
        textObject = font.render(text, True, p.Color('white'))
        textLocation = moveLogRect.move(padding, textY)
        screen.blit(textObject, textLocation)
        textY += textObject.get_height() + lineSpacing


def animateMove(move, screen, board, clock):
    global colors
    dR = move.endRow - move.startRow
    dC = move.endCol - move.startCol
    # framesPerSquare = const/dystans do pokonania
    # dzwiek powinnen sie pojawic w ~25 klatce
    distance = math.sqrt(dR ** 2 + dC ** 2)
    frameCount = math.ceil((abs(dR) + abs(dC)) * 17 / distance)
    for frame in range(frameCount + 1):
        row, column = (move.startRow + dR * frame / frameCount, move.startCol + dC * frame / frameCount)
        drawBoard(screen)
        drawPieces(screen, board)
        # erase the piece
        color = colors[(move.endRow + move.endCol) % 2]
        endSquare = p.Rect(move.endCol * SQ_SIZE, move.endRow * SQ_SIZE, SQ_SIZE, SQ_SIZE)
        p.draw.rect(screen, color, endSquare)
        # draw captured piece first then rect
        if move.pieceCaptured != "--":
            if move.isEnpassantMove:
                enpassantRow = move.endRow + 1 if move.pieceCaptured[0] == 'b' else move.endRow - 1
                endSquare = p.Rect(move.endCol * SQ_SIZE, enpassantRow * SQ_SIZE, SQ_SIZE, SQ_SIZE)
            screen.blit(IMAGES[move.pieceCaptured], endSquare)
        screen.blit(IMAGES[move.pieceMoved], p.Rect(column * SQ_SIZE, row * SQ_SIZE, SQ_SIZE, SQ_SIZE))
        p.display.flip()
        clock.tick(60)


def makeCheckSound(gameState):
    inCheck, pins, checks = gameState.checkForPinsAndChecks()
    if inCheck or len(checks) != 0:
        Thread(target=playsound, args=('sound/check.mp3',), daemon=True).start()


def playSound(move, gameState, gameOver):
    allyColor = gameState.board[move.startRow][move.startCol][0]
    if move.isCastleMove:
        Thread(target=playsound, args=('sound/castling.mp3',), daemon=True).start()
        return
    elif gameState.board[move.endRow][move.endCol] == '--' and not move.isEnpassantMove:
        Thread(target=playsound, args=('sound/move1.mp3',), daemon=True).start()
        return
    elif gameState.board[move.endRow][move.endCol][0] != allyColor or move.isEnpassantMove:
        Thread(target=playsound, args=('sound/capturing.mp3',), daemon=True).start()
        return
    elif gameOver:
        Thread(target=playsound, args=('sound/lose_win.mp3',), daemon=True).start()
        return


def drawEndGameText(screen, text):
    font = p.font.SysFont("Arial", 32, True, False)
    textObject = font.render(text, False, p.Color('Gray'))
    textLocation = p.Rect(0, 0, BOARD_WIDTH, BOARD_HEIGHT).move(BOARD_WIDTH / 2 - textObject.get_width() / 2,
                                                                BOARD_HEIGHT / 2 - textObject.get_height() / 2)
    screen.blit(textObject, textLocation)
    textObject = font.render(text, False, p.Color('Black'))
    screen.blit(textObject, textLocation.move(2, 2))


if __name__ == '__main__':
    main()
