from chessBoard import chessBoard


class Game:
    def __init__(self, position='rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'):
        self.board = chessBoard(position)
        self.fileMapping = dict(zip([i for i in 'abcdefgh'], [i for i in range(8)]))
        self.history = []
        self.history.append(self.board.fen())
        self.K, self.k = [], []
        self.updateKing()
        self.possibleMoves = dict()
        self.IsStaleMate = {'w':False, 'b':False}
        self.CheckMateOrStaleMate = None

    # input format is ['a1','b2'] where a1 is the square from which the piece will be moved and b2 is the square to which square the piece will be moved
    def move(self,move,forced=False):
        promotion = (move[2] if len(move)>2 else 'Q')
        move=move[:2]
        From, To = self.decodeMove(move)
        if(self.board[From[0]][From[1]] == '*'):
            raise Exception("The square is empty")

        self.board.halfMoves = (0 if (self.board[From[0]][From[1]].lower()=='p' or self.board[To[0]][To[1]]!='*') else self.board.halfMoves+1)
        self.board.fullMoves += (1 if self.board.turn=='b' else 0)
        # Code for Move Revert / Cheating / Debugging
        if forced:
            self.board[To[0]][To[1]] = self.board[From[0]][From[1]]
            self.board[From[0]][From[1]] = '*'
            self.board.turn = 'w' if self.board.turn == 'b' else 'b'
            self.updateKing()
            self.possibleMoves = dict()
            return

        # Validating if the correct color's piece is moved
        if self.board[From[0]][From[1]].isupper() and self.board.turn != 'w':
            raise Exception("Not your turn")
        elif self.board[From[0]][From[1]].islower() and self.board.turn != 'b':
            raise Exception("Not your turn")
        
        possibleMoves = [i[:2] for i in self.PossibleMoves(From)]
        if list(To) in possibleMoves:
            #Handling special cases of Pawns (En passant, Promotion)
            self.board.enPassant = '-'
            if(self.board[From[0]][From[1]] in ['P','p']):
                if((From[0]==1 and To[0]==3) or (From[0]==6 and To[0]==4)):
                    self.board.enPassant = self.encodePosition([To[0]+( 1 if From[0]==6 else -1),To[1]])
                if promotion.lower() in ['q','r','n','b']:
                    self.board[From[0]][From[1]] = promotion.upper() if(From[0]==1 and self.board[From[0]][From[1]]=='P') else self.board[From[0]][From[1]]
                    self.board[From[0]][From[1]] = promotion.lower() if(From[0]==6 and self.board[From[0]][From[1]]=='p') else self.board[From[0]][From[1]]
                if(From[1]!=To[1] and self.board[To[0]][To[1]]=='*'):
                    self.board[To[0]+ (1 if self.board[From[0]][From[1]]=="P" else -1)][To[1]]='*'
            #Handling special cases of King (Castling)
            elif self.board[From[0]][From[1]] in ['K','k']:
                if self.board[From[0]][From[1]]=='K':
                    self.board.castle['K'] = False
                    self.board.castle['Q'] = False
                else:
                    self.board.castle['k'] = False
                    self.board.castle['q'] = False
                if abs(To[1]-From[1])>1:
                    if(To[1]==2):
                        testGame = Game(self.board.fen())
                        if self.board.turn=='w':
                            testGame.move([testGame.encodePosition([7,4]),testGame.encodePosition( [7,3] )], forced=True)
                            if(testGame.isChecked()[self.board.turn]):
                                raise Exception("Castling passes through check!")
                            self.board[To[0]][3] = self.board[To[0]][0]
                            self.board[To[0]][0] = '*'
                        elif self.board.turn=='b':
                            testGame.move([testGame.encodePosition([0,4]),testGame.encodePosition( [0,3] )], forced=True)
                            if(testGame.isChecked()[self.board.turn]):
                                raise Exception("Castling passes through check!")
                            self.board[To[0]][3] = self.board[To[0]][0]
                            self.board[To[0]][0] = '*'
                    elif(To[1]==6):
                        testGame = Game(self.board.fen())
                        if self.board.turn=='w':
                            testGame.move([testGame.encodePosition([7,4]),testGame.encodePosition( [7,5] )], forced=True)
                            if(testGame.isChecked()[self.board.turn]):
                                raise Exception("Castling passes through check!")
                            self.board[To[0]][5] = self.board[To[0]][7]
                            self.board[To[0]][7] = '*'
                        elif self.board.turn=='b':
                            testGame.move([testGame.encodePosition([0,4]),testGame.encodePosition( [0,5] )], forced=True)
                            if(testGame.isChecked()[self.board.turn]):
                                raise Exception("Castling passes through check!")
                            self.board[To[0]][5] = self.board[To[0]][7]
                            self.board[To[0]][7] = '*'
            #Disabling Castle on Rook Move
            elif self.board[From[0]][From[1]] in ['R','r']:
                self.board.castle['K'] = False if From == (7,7) else self.board.castle['K']
                self.board.castle['Q'] = False if From == (7,0) else self.board.castle['Q']
                self.board.castle['k'] = False if From == (0,7) else self.board.castle['k']
                self.board.castle['q'] = False if From == (0,0) else self.board.castle['q']
            #Moving the piece
            self.board[To[0]][To[1]] = self.board[From[0]][From[1]]
            self.board[From[0]][From[1]] = '*'
        else:
            raise Exception("Invalid Move")
        
        self.updateKing()
        # Validate if the move is safe
        if self.isChecked()[self.board.turn]:
            self.board = chessBoard(self.history[-1])
            self.updateKing()
            raise Exception("You will be in check")

        self.board.turn = 'w' if self.board.turn == 'b' else 'b'
        self.history.append(self.board.fen())
        self.CheckMateOrStaleMate = self.checkMateorStaleMate()
        self.updateKing()
        self.possibleMoves = dict()


    def checkMateorStaleMate(self):
        for turn in ['w','b']:
            checked = self.isChecked()[turn]
            stalemate = self.isStaleMate()[turn]
            if checked and stalemate:
                return 'CheckMate'
            elif stalemate:
                return 'StaleMate'
        return None

    def isStaleMate(self):
        staleMateCombinations = [
            {'K','k'},
            {'K','k','B'},
            {'K','k','b'},
            {'K','k','N'},
            {'K','k','n'}
        ]
        allPieces=self.allPieces('w')+self.allPieces('b')
        allPieces=self.squareToPiece(allPieces)
        for turn in ['w','b']:
            if self.board.halfMoves>=100:
                self.IsStaleMate[turn]=True
                continue
            elif  [i.split(" ")[0] for i in self.history].count(self.board.fen().split(" ")[0]) >2:
                self.IsStaleMate[turn] = True
                continue
            elif len(allPieces)<=3 and set(allPieces) in staleMateCombinations:
                self.IsStaleMate[turn]=True
                continue
            self.IsStaleMate[turn] = None
            for i in self.allPieces(turn):
                testGame = Game(self.board.fen())
                for j in testGame.PossibleMoves(i):
                    testGame.board = chessBoard(self.board.fen())
                    j = j[:2]
                    testGame.move(self.encodeMove([i, j]),forced=True)
                    testGame.board.turn=turn
                    if not testGame.isChecked()[testGame.board.turn]:
                        self.IsStaleMate[turn] = False
                        break
                if self.IsStaleMate[turn]!= None:
                    break
            self.IsStaleMate[turn] = True if self.IsStaleMate[turn] ==None else False
        return self.IsStaleMate

    def isChecked(self):
        checked = {'w': False, 'b': False}
        if 'q' in self.squareToPiece(self.linear(self.K)['b']) or 'r' in self.squareToPiece(self.linear(self.K)['b']):
            checked['w'] = True
        if 'q' in self.squareToPiece(self.diagonal(self.K)['b']) or 'b' in self.squareToPiece(self.diagonal(self.K)['b']):
            checked['w'] = True
        if 'n' in self.squareToPiece(self.knight(self.K)['b']):
            checked['w'] = True
        if 'k' in self.squareToPiece(self.king(self.K)['b']):
            checked['w'] = True
        if self.K[0] > 0 and ((self.K[1] > 0 and self.board[self.K[0] - 1][self.K[1] - 1] == 'p') or (self.K[1] < 7 and self.board[self.K[0] - 1][self.K[1] + 1] == 'p')):
            checked['w'] = True
        if 'Q' in self.squareToPiece(self.linear(self.k)['w']) or 'R' in self.squareToPiece(self.linear(self.k)['w']):
            checked['b'] = True
        if 'Q' in self.squareToPiece(self.diagonal(self.k)['w']) or 'B' in self.squareToPiece(self.diagonal(self.k)['w']):
            checked['b'] = True
        if 'N' in self.squareToPiece(self.knight(self.k)['w']):
            checked['b'] = True
        if 'K' in self.squareToPiece(self.king(self.k)['w']):
            checked['b'] = True
        if self.k[0] < 7 and ((self.k[1] > 0 and self.board[self.k[0] + 1] [self.k[1] - 1] == 'P') or (self.k[1] < 7 and self.board[self.k[0] + 1][self.k[1] + 1] == 'P')):
            checked['b'] = True
        return checked



    def revertMove(self):
        if len(self.history)<2:
            raise Exception("No move has been made yet")
        self.history.pop()
        self.board = chessBoard(self.history[-1])
        self.updateKing()
    
    def squareToPiece(self, squares):
        pieces = []
        for square in squares:
            pieces.append(self.board[square[0]][square[1]])
        return pieces

    def decodePosition(self, move):
        pos = (8 - int(move[1]), self.fileMapping[move[0].lower()])
        return pos

    def encodePosition(self, move):
        pos = chr(move[1] + 97) + str(8 - move[0])
        return pos

    # input format is ['a1','b2'] where a1 and b2 are squares on the chessboard
    # output format is [(7,0),(7,1)] where (7,0) and (7,1) are indexes of squares gives as move in function arguments
    def decodeMove(self, move):
        From = (8 - int(move[0][1]), self.fileMapping[move[0][0].lower()])
        to = (8 - int(move[1][1]), self.fileMapping[move[1][0].lower()])
        return [From, to]

    def encodeMove(self, move):
        From = chr(move[0][1] + 97) + str(8 - move[0][0])
        to = chr(move[1][1] + 97) + str(8 - move[1][0])
        return [From, to]

    # input format of piece is [r,c] where r and c are row and column index of the piece
    # output is an array of all possible moves in format [r,c] where r and c are row and column index of the square where the piece can move
    def PossibleMoves(self, piece):
        pieceEncoded = self.encodePosition(piece)
        if pieceEncoded in self.possibleMoves.keys():
            return self.possibleMoves[pieceEncoded]
        moves = []
        row, col = piece
        if self.board[row][col] == 'P':
            if self.board[row - 1][col] == '*':
                if row==1:
                    for i in ["Q","R","N","B"]:
                        moves.append([row-1,col,i])
                else:
                    moves.append([row - 1, col])
            if row == 6 and self.board[row - 1][col] == '*' and self.board[row - 2][col] == '*':
                moves.append([row - 2, col])
            if col != 7 and self.board[row - 1][col + 1].islower():
                if row==1:
                    for i in ["Q","R","N","B"]:
                        moves.append([row-1,col+1,i])
                else:
                    moves.append([row - 1, col + 1])
            if col != 0 and self.board[row - 1][col - 1].islower():
                if row==1:
                    for i in ["Q","R","N","B"]:
                        moves.append([row-1,col-1,i])
                else:
                    moves.append([row - 1, col - 1])
            # For en passant
            if col != 7 and row == 3 and self.board[row][col + 1] == 'p' and not self.board[row - 1][col + 1].isupper() and self.encodePosition([row-1,col+1])==self.board.enPassant:
                moves.append([row - 1, col + 1])
            if col != 0 and row == 3 and self.board[row][col - 1] == 'p' and not self.board[row - 1][col - 1].isupper() and self.encodePosition([row-1,col-1])==self.board.enPassant:
                moves.append([row - 1, col - 1] )
            self.possibleMoves[pieceEncoded] = moves
            return self.possibleMoves[pieceEncoded]
        if self.board[row][col] == 'p':
            if self.board[row + 1][col] == '*':
                if row==6:
                    for i in ["q","r","n","b"]:
                        moves.append([row+1,col,i])
                else:
                    moves.append([row + 1, col])
            if row == 1 and self.board[row + 1][col] == '*' and self.board[row + 2][col] == '*':
                moves.append([row + 2, col])
            if col != 7 and self.board[row + 1][col + 1].isupper():
                if row==6:
                    for i in ["q","r","n","b"]:
                        moves.append([row+1,col+1,i])
                else:
                    moves.append([row + 1, col + 1])
            if col != 0 and self.board[row + 1][col - 1].isupper():
                if row==6:
                    for i in ["q","r","n","b"]:
                        moves.append([row+1,col-1,i])
                else:
                    moves.append([row + 1, col - 1])
            # For en passant
            if col != 7 and row == 4 and self.board[row][col + 1] == 'P' and not self.board[row + 1][col + 1].islower() and self.encodePosition([row+1,col+1])==self.board.enPassant:
                moves.append([row + 1, col + 1])
            if col != 0 and row == 4 and self.board[row][col - 1] == 'P' and not self.board[row + 1][col - 1].islower() and self.encodePosition([row+1,col-1])==self.board.enPassant:
                moves.append([row + 1, col - 1])
            self.possibleMoves[pieceEncoded] = moves
            return self.possibleMoves[pieceEncoded]

        # Movement of Rooks
        if self.board[row][col] == 'R':
            moves = self.linear(piece)
            self.possibleMoves[pieceEncoded] = moves['*'] + moves['b']
            return self.possibleMoves[pieceEncoded]

        if self.board[row][col] == 'r':
            moves = self.linear(piece)
            self.possibleMoves[pieceEncoded] = moves['*'] + moves['w']
            return self.possibleMoves[pieceEncoded]

        # Movement of Bishops
        if self.board[row][col] == 'B':
            moves = self.diagonal(piece)
            self.possibleMoves[pieceEncoded] = moves['*'] + moves['b']
            return self.possibleMoves[pieceEncoded]

        if self.board[row][col] == 'b':
            moves = self.diagonal(piece)
            self.possibleMoves[pieceEncoded] = moves['*'] + moves['w']
            return self.possibleMoves[pieceEncoded]

        if self.board[row][col] == 'N':
            moves = self.knight(piece)
            self.possibleMoves[pieceEncoded] = moves['*'] + moves['b']
            return self.possibleMoves[pieceEncoded]

        if self.board[row][col] == 'n':
            moves = self.knight(piece)
            self.possibleMoves[pieceEncoded] = moves['*'] + moves['w']
            return self.possibleMoves[pieceEncoded]

        if self.board[row][col] == 'Q':
            linear = self.linear(piece)
            diagonal = self.diagonal(piece)
            self.possibleMoves[pieceEncoded] = linear['*'] + linear['b'] + diagonal['*'] + diagonal['b']
            return self.possibleMoves[pieceEncoded]

        if self.board[row][col] == 'q':
            linear = self.linear(piece)
            diagonal = self.diagonal(piece)
            self.possibleMoves[pieceEncoded] = linear['*'] + linear['w'] + diagonal['*'] + diagonal['w']
            return self.possibleMoves[pieceEncoded]

        if self.board[row][col] == 'K':
            moves = self.king(piece)
            if self.board.castle['K'] and self.board[7][7] == 'R' and self.board[7][6] == self.board[7][5] == '*':
                moves['*'].append([7, 6])
            if self.board.castle['Q'] and self.board[7][0]=='R' and self.board[7][1]==self.board[7][2]==self.board[7][
                3]=='*':
                moves['*'].append([7, 2])
            self.possibleMoves[pieceEncoded] = moves['*'] + moves['b']
            return self.possibleMoves[pieceEncoded]
        if self.board[row][col] == 'k':
            moves = self.king(piece)
            if self.board.castle['k'] and self.board[0][7]=='r' and self.board[0][6]==self.board[0][5]=='*':
                moves['*'].append([0, 6] )
            if self.board.castle['q'] and self.board[0][0]=='r' and self.board[0][1]==self.board[0][2]==self.board[0][3]=='*':
                moves['*'].append([0, 2])
            self.possibleMoves[pieceEncoded] = moves['*'] + moves['w']
            return self.possibleMoves[pieceEncoded]
        return []

    # input format of square is [r,c] where r and c are row and column index of the square
    # output format is {'*':[moves],'w':[moves],'b':[moves]}
    def linear(self, square):
        moves = {'*': [], 'w': [], 'b': []}
        row, col = square
        r, c = row + 1, col
        while r <= 7:
            if self.board[r][c] != '*':
                moves['w' if self.board[r][c].isupper() else 'b'].append([r,c])
                break
            else:
                moves['*'].append([r, c])
                r += 1
        r = row - 1
        while r >= 0:
            if self.board[r][c] != '*':
                moves['w' if self.board[r][c].isupper() else 'b'].append([r,c])
                break
            else:
                moves['*'].append([r, c])
                r -= 1
        r, c = row, col + 1
        while c <= 7:
            if self.board[r][c] != '*':
                moves['w' if self.board[r][c].isupper() else 'b'].append([r,c])
                break
            else:
                moves['*'].append([r, c])
                c += 1
        c = col - 1
        while c >= 0:
            if self.board[r][c] != '*':
                moves['w' if self.board[r][c].isupper() else 'b'].append([r,c])
                break
            else:
                moves['*'].append([r, c])
                c -= 1
        return moves

    def diagonal(self, square):
        moves = {'*': [], 'w': [], 'b': []}
        row, col = square
        r, c = row + 1, col + 1
        while r <= 7 and c <= 7:
            if self.board[r][c] != '*':
                moves['w' if self.board[r][c].isupper() else 'b'].append([r,c])
                break
            else:
                moves['*'].append([r, c])
                r, c = r + 1, c + 1
        r, c = row - 1, col + 1
        while r >= 0 and c <= 7:
            if self.board[r][c] != '*':
                moves['w' if self.board[r][c].isupper() else 'b'].append([r,c])
                break
            else:
                moves['*'].append([r, c])
                r, c = r - 1, c + 1
        r, c = row + 1, col - 1
        while r <= 7 and c >= 0:
            if self.board[r][c] != '*':
                moves['w' if self.board[r][c].isupper() else 'b'].append([r,c])
                break
            else:
                moves['*'].append([r, c])
                r, c = r + 1, c - 1
        r, c = row - 1, col - 1
        while r >= 0 and c >= 0:
            if self.board[r][c] != '*':
                moves['w' if self.board[r][c].isupper() else 'b'].append([r,c])
                break
            else:
                moves['*'].append([r, c])
                r, c = r - 1, c - 1
        return moves

    def knight(self, square):
        moves = {'*': [], 'w': [], 'b': []}
        row, col = square
        possibilities = [[row + 2, col + 1], [row + 1, col + 2], [row - 1, col - 2], [row - 2, col - 1],
                         [row - 2, col + 1], [row + 2, col - 1], [row + 1, col - 2], [row - 1, col + 2]]
        for i in possibilities:
            if i[0] >= 0 and i[0] <= 7 and i[1] >= 0 and i[1] <= 7:
                if self.board[i[0]][i[1]] == '*':
                    moves['*'].append(i)
                else:
                    moves['w' if self.board[i[0]][i[1]].isupper() else 'b'].append(i)
        return moves

    def king(self, square):
        row, col = square
        moves = {'*': [], 'w': [], 'b': []}
        possibilities = [[row + 1, col + 1], [row - 1, col - 1], [row, col + 1], [row, col - 1], [row + 1, col],
                         [row - 1, col], [row + 1, col - 1], [row - 1, col + 1]]
        for i in possibilities:
            if i[0] >= 0 and i[0] <= 7 and i[1] >= 0 and i[1] <= 7:
                if self.board[i[0]][i[1]] == '*':
                    moves['*'].append(i)
                else:
                    moves['w' if self.board[i[0]][i[1]].isupper() else 'b'].append(i)
        return moves

    def updateKing(self):
        for rank in range(len(self.board.chessBoard)):
            for file in range(len(self.board[rank])):
                if self.board[rank][file] == 'K':
                    self.K = [rank, file]
                elif self.board[rank][file] == 'k':
                    self.k = [rank, file]
        if not self.K or not self.k:
            raise Exception("There is no king in the game")

    def allPieces(self, colour):
        squares = []
        for rank in range(len(self.board.chessBoard)):
            for file in range(len(self.board[rank])):
                if self.board[rank][file].isupper() and colour == 'w':
                    squares.append([rank, file])
                if self.board[rank][file].islower() and colour == 'b':
                    squares.append([rank, file])
        return squares
    
    def __str__(self):
        string = str(self.board)
        string+=f"\nMove: {'White' if self.board.turn=='w' else 'Black'}"
        string+=f"\nMove Number : {self.board.fullMoves}"
        string+=f"\nCastling Rights : {self.board.castle}"
        string+=f"\nMoves till last capture or pawn move : {self.board.halfMoves}"
        string+=f"\nEn passant available : {self.board.enPassant}"
        return string
