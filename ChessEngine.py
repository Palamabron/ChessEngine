"""
Storing info about current state.
Calculating moves.
Move log.
"""
import numpy
import TranspositionTable


class GameState:
    def __init__(self):
        # self.board = [
        #     ['bR', '--', 'bQ', '--', 'bK', 'bB', '--', 'bR'],
        #     ['bP', '--', 'bP', '--', 'bP', 'bP', '--', 'bP'],
        #     ['--', '--', 'wN', '--', 'bB', '--', 'bP', '--'],
        #     ['--', '--', '--', '--', '--', '--', '--', '--'],
        #     ['--', '--', '--', 'wP', 'wN', '--', '--', '--'],
        #     ['--', '--', '--', '--', '--', '--', '--', '--'],
        #     ['wP', 'wP', 'wP', '--', '--', 'wP', 'wP', 'wP'],
        #     ['wR', '--', 'wB', 'wQ', 'wK', 'wB', '--', 'wR']
        # ]
        self.board = [
            ['bR', 'bN', 'bB', 'bQ', 'bK', 'bB', 'bN', 'bR'],
            ['bP', 'bP', 'bP', 'bP', 'bP', 'bP', 'bP', 'bP'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['wP', 'wP', 'wP', 'wP', 'wP', 'wP', 'wP', 'wP'],
            ['wR', 'wN', 'wB', 'wQ', 'wK', 'wB', 'wN', 'wR']
        ]
        self.moveFunctions = {'P': self.getPawnMoves, 'R': self.getRookMoves, 'N': self.getKnightMoves,
                              'B': self.getBishopMoves, 'Q': self.getQueenMoves, 'K': self.getKingMoves}
        self.whiteToMove = 1
        self.moveLog = []
        self.whiteKingLocation = (7, 4)
        self.blackKingLocation = (0, 4)
        self.inCheck = 0
        self.pins = []
        self.checks = []
        self.checkmate = 0
        self.stalemate = 0
        self.enpassantPossible = ()  # coords where enpassant is possible
        self.enpassantPossibleLog = [self.enpassantPossible]
        self.currentCastlingRight = CastleRights(True, True, True, True)
        self.castleRightsLog = [CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks,
                                             self.currentCastlingRight.wqs, self.currentCastlingRight.bqs)]
        self.moveCounter = 1
        self.numbers = TranspositionTable.generateNumberForBoard()
        self.hashValue = TranspositionTable.generateHash(self, self.numbers)

    def getNumberOfPiecesOnBoard(self):
        pieces = 0
        for row in self.board:
            for element in row:
                if element != '--':
                    pieces += 1
        return pieces

    def getFENnotation(self):
        fen = ''
        tmp = []
        for row in self.board:
            for element in row:
                if element == '--':
                    tmp.append(element)
                    if len(tmp) == 8:
                        fen += str(len(tmp))
                        tmp = []
                else:
                    if len(tmp) != 0:
                        fen += str(len(tmp))
                        tmp = []
                        if element[0] == 'w':
                            fen += element[1]
                        else:
                            fen += element[1].lower()
                    else:
                        if element[0] == 'w':
                            fen += element[1]
                        else:
                            fen += element[1].lower()
            if len(tmp) == 0:
                fen += '/'
            else:
                fen += str(len(tmp)) + '/'
                tmp = []
        fen = fen[:-1]
        return fen

    def setFENboard(self, fen):
        r = c = 0
        for element in fen:
            if element.isdigit():
                for i in range(int(element)):
                    self.board[r][c] = '--'
                    c += 1
                c -= 1
            elif element == '/':
                r += 1
                c = -1
            elif element == 'p':
                self.board[r][c] = 'bP'
            elif element == 'P':
                self.board[r][c] = 'wP'
            elif element == 'b':
                self.board[r][c] = 'bB'
            elif element == 'B':
                self.board[r][c] = 'wB'
            elif element == 'n':
                self.board[r][c] = 'bN'
            elif element == 'N':
                self.board[r][c] = 'wN'
            elif element == 'R':
                self.board[r][c] = 'wR'
            elif element == 'r':
                self.board[r][c] = 'bR'
            elif element == 'K':
                self.board[r][c] = 'wK'
            elif element == 'k':
                self.board[r][c] = 'bK'
            elif element == 'Q':
                self.board[r][c] = 'wQ'
            elif element == 'q':
                self.board[r][c] = 'bQ'
            c += 1

    # działa dla roszad, bicia w przelocie, promocji piona
    def makeMove(self, move):
        if self.board[move.startRow][move.startCol] != "--":
            self.board[move.startRow][move.startCol] = "--"
            self.board[move.endRow][move.endCol] = move.pieceMoved
            self.moveLog.append(move)
            self.whiteToMove = not self.whiteToMove  # swap players
            # król:
            if move.pieceMoved == 'wK':
                self.whiteKingLocation = (move.endRow, move.endCol)
            elif move.pieceMoved == 'bK':
                self.blackKingLocation = (move.endRow, move.endCol)

            # promocja
            if move.isPawnPromotion:
                # promotedPiece = None
                # while promotedPiece not in ["Q", "R", "B", "N"]:
                #     promotedPiece = input("Promote to Q, R, B or N")
                self.board[move.endRow][move.endCol] = move.pieceMoved[0] + 'Q'
                # self.board[move.endRow][move.endCol] = move.pieceMoved[0] + promotedPiece

            # enpassant move
            if move.isEnpassantMove:
                self.board[move.startRow][move.endCol] = '--'  # capture

            # update enpassant
            if move.pieceMoved[1] == 'P' and abs(move.startRow - move.endRow) == 2:  # only 2 square pawn advances
                self.enpassantPossible = ((move.startRow + move.endRow) // 2, move.startCol)
            else:
                self.enpassantPossible = ()

            self.enpassantPossibleLog.append(self.enpassantPossible)

            # castle move
            # print(move.isCastleMove)
            if move.isCastleMove:
                if move.endCol - move.startCol == 2:  # kingside castle
                    self.board[move.endRow][move.endCol - 1] = self.board[move.endRow][move.endCol + 1]  # moves the
                    # rook
                    self.board[move.endRow][move.endCol + 1] = "--"
                else:  # queenside castle
                    self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][move.endCol - 2]  # moves the
                    # rook
                    self.board[move.endRow][move.endCol - 2] = "--"
            # update castling rights - when it is a rook/king move
            self.updateCastleRights(move)
            self.castleRightsLog.append(CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks,
                                                     self.currentCastlingRight.wqs, self.currentCastlingRight.bqs))

    # undo last made move
    def undoMove(self):
        if len(self.moveLog) != 0:
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove
            # król:
            if move.pieceMoved == 'wK':
                self.whiteKingLocation = (move.startRow, move.startCol)
            elif move.pieceMoved == 'bK':
                self.blackKingLocation = (move.startRow, move.startCol)
            # undo enpassant
            if move.isEnpassantMove:
                self.board[move.endRow][move.endCol] = '--'  # leave landing square blank
                self.board[move.startRow][move.endCol] = move.pieceCaptured

            self.enpassantPossibleLog.pop()
            self.enpassantPossible = self.enpassantPossibleLog[-1]

            self.castleRightsLog.pop()  # get rid of the new castle right
            self.currentCastlingRight = self.castleRightsLog[-1]
            # undo castle
            if move.isCastleMove:
                if move.endCol - move.startCol == 2:
                    self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][move.endCol - 1]
                    self.board[move.endRow][move.endCol - 1] = '--'
                else:
                    self.board[move.endRow][move.endCol - 2] = self.board[move.endRow][move.endCol + 1]
                    self.board[move.endRow][move.endCol + 1] = '--'
            self.checkmate = False
            self.stalemate = False

    def inCheck(self):
        if self.whiteToMove:
            return self.squareUnderAttack(self.whiteKingLocation[0], self.whiteKingLocation[1])
        else:
            return self.squareUnderAttack(self.blackKingLocation[0], self.blackKingLocation[1])

    def squareUnderAttack(self, row, column):
        self.whiteToMove = not self.whiteToMove
        oppMoves = self.getAllPossibleMoves()
        self.whiteToMove = not self.whiteToMove
        for move in oppMoves:
            if move.endRow == row and move.endCol == column:
                return True
        return False

    # all moves without considering checks
    def getAllPossibleMoves(self):
        moves = []
        for row in range(len(self.board)):
            for column in range(len(self.board[row])):
                turn = self.board[row][column][0]
                if (turn == 'w' and self.whiteToMove) or (turn == 'b' and not self.whiteToMove):
                    piece = self.board[row][column][1]
                    self.moveFunctions[piece](row, column, moves)
        return moves

        # all moves considering checks

    def getValidMoves(self):
        """
        All moves considering checks.
        """
        tmpCastleRight = CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks,
                                      self.currentCastlingRight.wqs, self.currentCastlingRight.bqs)
        # advanced algorithm
        moves = []
        self.inCheck, self.pins, self.checks = self.checkForPinsAndChecks()

        if self.whiteToMove:
            kingRow = self.whiteKingLocation[0]
            kingCol = self.whiteKingLocation[1]
        else:
            kingRow = self.blackKingLocation[0]
            kingCol = self.blackKingLocation[1]
        if self.inCheck:
            if len(self.checks) == 1:  # only 1 check, block the check or move the king
                moves = self.getAllPossibleMoves()
                # to block the check you must put a piece into one of the squares between the enemy piece and your king
                check = self.checks[0]  # check information
                checkRow = check[0]
                checkCol = check[1]
                piece_checking = self.board[checkRow][checkCol]
                validSquares = []  # squares that pieces can move to
                # if knight, must capture the knight or move your king, other pieces can be blocked
                if piece_checking[1] == "N":
                    validSquares = [(checkRow, checkCol)]
                else:
                    for i in range(1, 8):
                        validSquare = (kingRow + check[2] * i,
                                       kingCol + check[3] * i)  # check[2] and check[3] are the check directions
                        validSquares.append(validSquare)
                        if validSquare[0] == checkRow and validSquare[1] == checkCol:  # once you get to pieceandcheck
                            break
                # get rid of any moves that don't block check or move king
                for i in range(len(moves) - 1, -1, -1):  # iterate through the list backwards when removing elements
                    if moves[i].pieceMoved[1] != "K":  # move doesn't move king so it must block or capture
                        if not (moves[i].endRow,
                                moves[i].endCol) in validSquares:  # move doesn't block or capture piece
                            moves.remove(moves[i])
            else:  # double check, king has to move
                self.getKingMoves(kingRow, kingCol, moves)
        else:  # not in check - all moves are fine
            moves = self.getAllPossibleMoves()
            if self.whiteToMove:
                self.getCastleMoves(self.whiteKingLocation[0], self.whiteKingLocation[1], moves)
            else:
                self.getCastleMoves(self.blackKingLocation[0], self.blackKingLocation[1], moves)

        if len(moves) == 0:
            if self.inCheck:
                self.checkmate = True
            else:
                # TODO stalemate on repeated moves
                self.stalemate = True
        else:
            self.checkmate = False
            self.stalemate = False

        self.currentCastlingRight = tmpCastleRight
        return moves

    def calculateStalemate(self):
        # stalemateByRepetition 3 te same ruchy z rzedu
        if len(self.moveLog) > 5:
            if self.moveLog[len(self.moveLog) - 1] == self.moveLog[len(self.moveLog) - 3]:
                if self.moveLog[len(self.moveLog) - 2] == self.moveLog[len(self.moveLog) - 4]:
                    if self.moveLog[len(self.moveLog) - 3] == self.moveLog[len(self.moveLog) - 5]:
                        self.stalemate = True
                        return
        # brak materialu do mata
        blackMaterial = whiteMaterial = []
        for i in range(0, 8):
            for j in range(0, 8):
                if self.board[i][j][0] == 'w':
                    whiteMaterial.append(self.board[i][j][1])
                elif self.board[i][j][0] == 'b':
                    blackMaterial.append(self.board[i][j][1])
        if len(whiteMaterial) == 1 and len(blackMaterial) == 1:
            self.stalemate = True
            return
        elif len(whiteMaterial) == 1 and len(blackMaterial) == 2:
            if blackMaterial[0] == 'K':
                if blackMaterial[1] == 'B' or blackMaterial[1] == 'N':
                    self.stalemate = True
                    return
            elif blackMaterial[1] == 'K':
                if blackMaterial[0] == 'B' or blackMaterial[0] == 'N':
                    self.stalemate = True
                    return
        elif len(blackMaterial) == 1 and len(whiteMaterial) == 2:
            if whiteMaterial[0] == 'K':
                if whiteMaterial[1] == 'B' or whiteMaterial[1] == 'N':
                    self.stalemate = True
                    return
            elif whiteMaterial[1] == 'K':
                if whiteMaterial[0] == 'B' or whiteMaterial[0] == 'N':
                    self.stalemate = True
                    return
        elif len(whiteMaterial) == 2 and len(blackMaterial) == 2:
            if (whiteMaterial[0] == 'K' and whiteMaterial[1] == 'B') or (
                    whiteMaterial[1] == 'K' and whiteMaterial[0] == 'B'):
                if (blackMaterial[0] == 'K' and blackMaterial[1] == 'B') or (
                        blackMaterial[1] == 'K' and blackMaterial[0] == 'B'):
                    whiteBishopCoords = blackBishopCoords = None
                    for i in range(0, 8):
                        for j in range(0, 8):
                            if self.board[i][j] == 'wB':
                                whiteBishopCoords = (i, j)
                            elif self.board[i][j] == 'bB':
                                blackBishopCoords = (i, j)
                    if (whiteBishopCoords[0] + whiteBishopCoords[1]) % 2 == (
                            blackBishopCoords[0] + blackBishopCoords[1]) % 2:
                        self.stalemate = True
                        return
        # fifty-move rule 50 ruchow bez bicia i bez ruchu pionem

    def checkForPinsAndChecks(self):
        pins = []
        checks = []
        inCheck = False
        if self.whiteToMove:
            enemyColor = "b"
            allyColor = "w"
            startRow = self.whiteKingLocation[0]
            startCol = self.whiteKingLocation[1]
        else:
            enemyColor = "w"
            allyColor = "b"
            startRow = self.blackKingLocation[0]
            startCol = self.blackKingLocation[1]
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1))
        for j in range(len(directions)):
            d = directions[j]
            possiblePin = ()  # RST pins
            for i in range(1, 8):
                endRow = startRow + d[0] * i
                endCol = startCol + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] == allyColor and endPiece[1] != "K":
                        if possiblePin == ():
                            possiblePin = (endRow, endCol, d[0], d[1])
                        else:
                            break
                    elif endPiece[0] == enemyColor:
                        pieceType = endPiece[1]
                        if (0 <= j <= 3 and pieceType == 'R') or (4 <= j <= 7 and pieceType == 'B') or \
                                (i == 1 and pieceType == 'P' and ((enemyColor == 'w' and 6 <= j <= 7) or
                                                                  (enemyColor == 'b' and 4 <= j <= 5))) or (
                                pieceType == 'Q') or (i == 1 and pieceType == 'K'):
                            if possiblePin == ():
                                inCheck = True
                                checks.append((endRow, endCol, d[0], d[1]))
                                break
                            else:
                                pins.append(possiblePin)
                                break
                        else:
                            break
                else:
                    break

        knightMoves = ((-2, -1), (-2, 1), (2, -1), (2, 1),
                       (-1, -2), (-1, 2), (1, -2), (1, 2))
        for m in knightMoves:
            endRow = startRow + m[0]
            endCol = startCol + m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] == enemyColor and endPiece[1] == 'N':
                    inCheck = True
                    checks.append((endRow, endCol, m[0], m[1]))
        return inCheck, pins, checks

    # bicie piona, ruch o 1 i ruch 2 dodawany do listy moves
    def getPawnMoves(self, row, column, moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == column:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        if self.whiteToMove:
            moveAmount = -1
            startRow = 6
            backRow = 0
            enemyColor = 'b'
            kingRow, kingCol = self.whiteKingLocation
        else:
            moveAmount = 1
            startRow = 1
            backRow = 7
            enemyColor = 'w'
            kingRow, kingCol = self.blackKingLocation

        if self.board[row + moveAmount][column] == "--":  # ruch o 1
            if not piecePinned or pinDirection == (moveAmount, 0):
                moves.append(Move((row, column), (row + moveAmount, column), self.board))
                if row == startRow and self.board[row + 2 * moveAmount][column] == "--":  # ruch o 2
                    moves.append(Move((row, column), (row + 2 * moveAmount, column), self.board))

        if column - 1 >= 0:  # bicie w lewo
            if not piecePinned or pinDirection == (moveAmount, -1):
                if self.board[row + moveAmount][column - 1][0] == enemyColor:
                    moves.append(Move((row, column), (row + moveAmount, column - 1), self.board))
                if (row + moveAmount, column - 1) == self.enpassantPossible:
                    attackingPiece = blockingPiece = False
                    if kingRow == row:
                        if kingCol < column:  # king is left of the pawn
                            # inside between king and pawn; outside range between pawn border
                            insideRange = range(kingCol + 1, column - 1)
                            outsideRange = range(column + 1, 8)
                        else:  # king is right of the pawn
                            insideRange = range(kingCol - 1, column, -1)
                            outsideRange = range(column - 2, -1, -1)
                        for i in insideRange:
                            if self.board[row][i] != '--':  # some piece other than enpassant pawn block
                                blockingPiece = True
                                break
                        for i in outsideRange:
                            square = self.board[row][i]
                            if square[0] == enemyColor and (square[1] == 'R' or square[1] == 'Q'):  # attacking piece
                                attackingPiece = True
                            elif square != '--':
                                blockingPiece = True
                        if not attackingPiece or blockingPiece:
                            moves.append(
                                Move((row, column), (row + moveAmount, column - 1), self.board, isEnpassantMove=True))

        if column + 1 <= 7:  # bicie w prawo
            if not piecePinned or pinDirection == (moveAmount, 1):
                if self.board[row + moveAmount][column + 1][0] == enemyColor:
                    moves.append(Move((row, column), (row + moveAmount, column + 1), self.board))
                if (row + moveAmount, column + 1) == self.enpassantPossible:
                    attackingPiece = blockingPiece = False
                    if kingRow == row:
                        if kingCol < column:  # king is left of the pawn
                            # inside between king and pawn; outside range between pawn border
                            insideRange = range(kingCol + 1, column)
                            outsideRange = range(column + 2, 8)
                        else:  # king is right of the pawn
                            insideRange = range(kingCol - 1, column + 1, -1)
                            outsideRange = range(column - 1, -1, -1)
                        for i in insideRange:
                            if self.board[row][i] != '--':  # some piece other than enpassant pawn block
                                blockingPiece = True
                                break
                        for i in outsideRange:
                            square = self.board[row][i]
                            if square[0] == enemyColor and (square[1] == 'R' or square[1] == 'Q'):  # attacking piece
                                attackingPiece = True
                            elif square != '--':
                                blockingPiece = True
                        if not attackingPiece or blockingPiece:
                            moves.append(
                                Move((row, column), (row + moveAmount, column + 1), self.board, isEnpassantMove=True))

    # adding all possible rook moves to the move list
    def getRookMoves(self, row, column, moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == column:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1))
        enemyColor = "b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1, 8):
                endRow = row + d[0] * i
                endCol = column + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    if not piecePinned or pinDirection == d or pinDirection == (-d[0], -d[1]):
                        endPiece = self.board[endRow][endCol]
                        if endPiece == "--":
                            moves.append(Move((row, column), (endRow, endCol), self.board))
                        elif endPiece[0] == enemyColor:
                            moves.append(Move((row, column), (endRow, endCol), self.board))
                            break
                        else:
                            break
                else:
                    break

    def getBishopMoves(self, row, column, moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == column:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break
        directions = ((-1, -1), (-1, 1), (1, -1), (1, 1))
        enemyColor = "b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1, 8):
                endRow = row + d[0] * i
                endCol = column + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    if not piecePinned or pinDirection == d or pinDirection == (-d[0], -d[1]):
                        endPiece = self.board[endRow][endCol]
                        if endPiece == "--":
                            moves.append(Move((row, column), (endRow, endCol), self.board))
                        elif endPiece[0] == enemyColor:
                            moves.append(Move((row, column), (endRow, endCol), self.board))
                            break
                        else:
                            break
                else:
                    break

    def getKnightMoves(self, row, column, moves):
        piecePinned = False
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == column:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break
        knightMoves = ((-2, -1), (-2, 1), (2, -1), (2, 1),
                       (-1, -2), (-1, 2), (1, -2), (1, 2))
        allyColor = "w" if self.whiteToMove else "b"
        for m in knightMoves:
            endRow = row + m[0]
            endCol = column + m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                if not piecePinned:
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] != allyColor:
                        moves.append(Move((row, column), (endRow, endCol), self.board))

    def getQueenMoves(self, row, column, moves):
        self.getBishopMoves(row, column, moves)
        self.getRookMoves(row, column, moves)

    def getKingMoves(self, row, column, moves):
        rowMoves = (-1, -1, -1, 0, 0, 1, 1, 1)
        colMoves = (-1, 0, 1, -1, 1, -1, 0, 1)
        allyColor = "w" if self.whiteToMove else "b"
        for i in range(8):
            endRow = row + rowMoves[i]
            endCol = column + colMoves[i]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor:
                    if allyColor == 'w':
                        self.whiteKingLocation = (endRow, endCol)
                    else:
                        self.blackKingLocation = (endRow, endCol)
                    inCheck, pins, checks = self.checkForPinsAndChecks()
                    if not inCheck:
                        moves.append(Move((row, column), (endRow, endCol), self.board))
                    if allyColor == 'w':
                        self.whiteKingLocation = (row, column)
                    else:
                        self.blackKingLocation = (row, column)

    def getCastleMoves(self, row, column, moves):
        if self.squareUnderAttack(row, column):
            return
        if (self.whiteToMove and self.currentCastlingRight.wks) or (
                not self.whiteToMove and self.currentCastlingRight.bks):
            self.getKingsideCastleMoves(row, column, moves)
        if (self.whiteToMove and self.currentCastlingRight.wqs) or (
                not self.whiteToMove and self.currentCastlingRight.bqs):
            self.getQueensideCastleMoves(row, column, moves)

    def getKingsideCastleMoves(self, row, column, moves):
        if self.board[row][column + 1] == "--" and self.board[row][column + 2] == "--":
            if not self.squareUnderAttack(row, column + 1) and not self.squareUnderAttack(row, column + 2):
                moves.append(Move((row, column), (row, column + 2), self.board, isCastleMove=True))

    def getQueensideCastleMoves(self, row, column, moves):
        if self.board[row][column - 1] == "--" and self.board[row][column - 2] == "--" and \
                self.board[row][column - 3] == '--':
            if not self.squareUnderAttack(row, column - 1) and not self.squareUnderAttack(row, column - 2):
                moves.append(Move((row, column), (row, column - 2), self.board, isCastleMove=True))

    def updateCastleRights(self, move):
        # if a rook is captured
        if move.pieceCaptured == 'wR':
            if move.endRow == 7:
                if move.endCol == 0:
                    self.currentCastlingRight.wqs = False
                elif move.endCol == 7:
                    self.currentCastlingRight.wks = False
        elif move.pieceCaptured == 'bR':
            if move.endRow == 0:
                if move.endCol == 0:
                    self.currentCastlingRight.bqs = False
                elif move.endCol == 7:
                    self.currentCastlingRight.bks = False
        # if Rook/King moved
        if move.pieceMoved == "wK":
            self.currentCastlingRight.wqs = False
            self.currentCastlingRight.wks = False
        elif move.pieceMoved == "bK":
            self.currentCastlingRight.bqs = False
            self.currentCastlingRight.bks = False
        elif move.pieceMoved == "wR":
            if move.startRow == 7:
                if move.startCol == 7:
                    self.currentCastlingRight.wks = False
                elif move.startCol == 0:
                    self.currentCastlingRight.wqs = False
        elif move.pieceMoved == "bR":
            if move.startRow == 0:
                if move.startCol == 7:
                    self.currentCastlingRight.bks = False
                elif move.startCol == 0:
                    self.currentCastlingRight.bqs = False


class CastleRights():
    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs


class Move:
    # maps keys to values
    # key : value
    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4,
                   "5": 3, "6": 2, "7": 1, "8": 0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}
    filesToCols = {"h": 7, "g": 6, "f": 5, "e": 4,
                   "d": 3, "c": 2, "b": 1, "a": 0}
    colsToFiles = {v: k for k, v in filesToCols.items()}

    def __init__(self, startSq, endSq, board, isEnpassantMove=False, isCastleMove=False):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        self.isPawnPromotion = (self.pieceMoved == 'wP' and self.endRow == 0) or (
                self.pieceMoved == 'bP' and self.endRow == 7)
        self.isEnpassantMove = isEnpassantMove
        if self.isEnpassantMove:
            self.pieceCaptured = 'wP' if self.pieceMoved == 'bP' else 'bP'
        self.isCastleMove = isCastleMove
        self.isCapture = self.pieceCaptured != '--'
        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol

    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False

    def __repr__(self):
        return repr(str(self.pieceMoved) + str(self.getRankFile(self.startRow, self.startCol)) +
                    str(self.getRankFile(self.endRow, self.endCol)))

    def getChessNotation(self):
        # you can add real chess notation
        return self.getRankFile(self.startRow, self.startCol) + " " + self.getRankFile(self.endRow, self.endCol)

    def getRankFile(self, row, column):
        return self.colsToFiles[column] + self.rowsToRanks[row]

    # toString pythonowy
    # notacja szachowa (PGN)
    def __str__(self):
        if self.isCastleMove:
            return 'O-O' if self.endCol == 6 else "O-O-O"
        endSquare = self.getRankFile(self.endRow, self.endCol)
        if self.pieceMoved[1] == 'P':
            if self.isCapture:
                return self.colsToFiles[self.startCol] + "x" + endSquare
            else:
                return endSquare

            # pawn promotion
        # jeśli 2 figury tego samego typu mg byc na tym samym miejscu gdzie byl ruch
        # trzeba dodac skad (z jakiej kolumny (np. 'd')) sie ruszyl
        # dodać szach (+) oraz mat (#)
        moveString = self.pieceMoved[1]
        if self.isCapture:
            moveString += 'x'
        return moveString + endSquare
