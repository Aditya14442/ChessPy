from chessBoard import chessBoard
class Game:
    def __init__(self,position='rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR',turn='W'):
        self.board = chessBoard(position)
        self.turn= turn
        self.fileMapping = dict(zip([i for i in 'abcdefgh'],[i for i in range(8)]))
        self.history=[]
        self.castelingRights=[1,1]
        self.K,self.k=False,False
        for rank in range(len(self.board.chessBoard)):
            for file in range(len(self.board[rank])):
                if self.board[rank][file]=='K':
                    self.K=[rank,file]
                elif self.board[rank][file]=='k':
                    self.k=[rank,file]
        if not self.K or not self.k:
            raise Exception("There is no king in the game")
            
    # input format is ['a1','b2'] where a1 is the square from which the piece will be moved and b2 is the square to which square the piece will be moved
    def move(self,move,forced=False):
        From,to = self.decodeMove(move)

        #Code for Move Revert / Cheating / Debugging
        if forced:
            self.board[to[0]][to[1]]=self.board[From[0]][From[1]]
            self.board[From[0]][From[1]] = '*'
            return

        
        if self.board[From]=='*':
            raise Exception("There is no piece on the square")
        
        #Checking If player is trying to move his piece or opponent's piece
        if self.board[From[0]][From[1]].isupper() and self.turn!='W':
            raise Exception("Not your turn")
        elif self.board[From[0]][From[1]].islower() and self.turn!='B':
            raise Exception("Not your turn")

        
        if list(to) in self.PossibleMoves(From):
            self.history.append(move+[self.board[to[0]][to[1]]])
            self.board[to[0]][to[1]]=self.board[From[0]][From[1]]
            self.board[From[0]][From[1]] = '*'
        else:
            raise Exception("Invalid Move")
            
        if self.turn=='W' and self.isChecked()['W']:
            self.revertMove()
            raise Exception('You are in check')
        elif self.turn=='B' and self.isChecked()['B']:
            self.revertMove()
            raise Exception('You are in check')
        
        self.turn = 'W' if self.turn=='B' else 'B'


    def squareToPiece(self,squares):
        pieces=[]
        for square in squares:
            pieces.append(self.board[square[0]][square[1]])
        return pieces
    def isChecked(self):
        checked = {'W':False,'B':False}
        if 'q' in self.squareToPiece(self.linear(self.K)['B']) or 'r' in self.squareToPiece(self.linear(self.K)['B']):
            checked['W']=True
        if 'q' in self.squareToPiece(self.diagonal(self.K)['B']) or 'b' in self.squareToPiece(self.diagonal(self.K)['B']):
            checked['W']=True
        if 'n' in self.squareToPiece(self.knight(self.K)['B']):
            checked['W']=True
        if self.board[self.K[0]-1,self.k[1]-1]=='p' or self.board[self.K[0]-1,self.k[1]+1]=='p':
            checked['W']=True
        if 'Q' in self.squareToPiece(self.linear(self.k)['W']) or 'R' in self.squareToPiece(self.linear(self.k)['W']):
            checked['B']=True
        if 'Q' in self.squareToPiece(self.diagonal(self.k)['W']) or 'B' in self.squareToPiece(self.diagonal(self.k)['W']):
            checked['B']=True
        if 'N' in self.squareToPiece(self.knight(self.k)['W']):
            checked['B']=True
        if self.board[self.k[0]+1,self.k[1]-1]=='P' or self.board[self.k[0]+1,self.k[1]+1]=='P':
            checked['B']=True
        return checked
    
    #To do - Revert En Passant
    def revertMove(self):
        if not self.history:
            raise Exception("No move has been made yet")
        lastMove = self.history[-1][:2]
        self.move(lastMove[::-1],forced=True)
        lastMoveDecoded=self.decodeMove(lastMove)
        self.board[lastMoveDecoded[1][0]][lastMoveDecoded[1][1]]=self.history[-1][-1]
        self.history.pop()

    # input format is ['a1','b2'] where a1 and b2 are squares on the chessboard
    # output format is [(7,0),(7,1)] where (7,0) and (7,1) are indexes of squares gives as move in function arguments
    def decodeMove(self,move):
        From = (8-int(move[0][1]),self.fileMapping[move[0][0].lower()])
        to = (8-int(move[1][1]),self.fileMapping[move[1][0].lower()])
        
        #To Do - Add  suppotr for usual chess move notation
        #For now the format is ['e2','e4']
        return [From,to]

    # input format of piece is [r,c] where r and c are row and column index of the piece
    # output is an array of all possible moves in format [r,c] where r and c are row and column index of the square where the piece can move
    def PossibleMoves(self,piece):
        moves=[]
        row,col=piece
        if self.board[row][col] =='P':
            if self.board[row-1][col]=='*':
                moves.append([row-1,col])
            if self.board[row-1][col]=='*' and self.board[row-2][col]=='*' and row==6:
                moves.append([row-2,col])
            if col!=7 and self.board[row-1][col+1].islower():
                moves.append([row-1,col+1])
            if col!=0 and self.board[row-1][col-1].islower():
                moves.append([row-1,col-1])
            #For en passant
            if col!=7 and row==3 and self.board[row][col+1]=='p' and not self.board[row-1,col+1].isupper() and len(self.history)>0 and self.decodeMove(self.history[-1][:2])==[(row-2,col+1),(row,col+1)]:
                moves.append([row-1,col+1])
            if col!=0 and row==3 and self.board[row][col-1]=='p' and not self.board[row-1,col-1].isupper() and len(self.history)>0 and self.decodeMove(self.history[-1][:2])==[(row-2,col-1),(row,col-1)]:
                moves.append([row-1,col-1])
            return moves
        if self.board[row][col] =='p':
            if self.board[row+1][col]=='*':
                moves.append([row+1,col])
            if self.board[row+1][col]=='*' and self.board[row+2][col]=='*' and row==1:
                moves.append([row+2,col])
            if col!=7 and self.board[row+1][col+1].isupper():
                moves.append([row+1,col+1])
            if col!=0 and self.board[row+1][col-1].isupper():
                moves.append([row+1,col-1])
            #For en passant
            if col!=7 and row==4 and self.board[row][col+1]=='P' and not self.board[row+1,col+1].islower() and len(self.history)>0 and self.decodeMove(self.history[-1][:2])==[(row+2,col+1),(row,col+1)]:
                moves.append([row+1,col+1])
            if col!=0 and row==4 and self.board[row][col-1]=='P' and not self.board[row+1,col-1].islower() and len(self.history)>0 and self.decodeMove(self.history[-1][:2])==[(row+2,col-1),(row,col-1)]:
                moves.append([row+1,col-1])
            return moves

        # Movement of Rooks
        if self.board[row][col] =='R':
            moves = self.linear(piece)
            return moves['*']+moves['B']
            
        if self.board[row][col] =='r':
            moves = self.linear(piece)
            return moves['*']+moves['W']

        # Movement of Bishops
        if self.board[row][col]=='B':
            moves = self.diagonal(piece)
            return moves['*']+moves['B']

        if self.board[row][col]=='b':
            moves = self.diagonal(piece)
            return moves['*']+moves['W']

        
        if self.board[row][col]=='N':
            moves = self.knight(piece)
            return moves['*']+moves['B']

        if self.board[row][col]=='n':
            moves = self.knight(piece)
            return moves['*']+moves['W']

        if self.board[row][col]=='Q':
            linear = self.linear(piece)
            diagonal = self.diagonal(piece)
            return linear['*']+linear['B'] + diagonal['*']+ diagonal['B']

        if self.board[row][col]=='q':
            linear = self.linear(piece)
            diagonal = self.diagonal(piece)
            return linear['*']+linear['W'] + diagonal['*']+ diagonal['W']
            
        if self.board[row][col]=='K':
            moves = self.king(piece)
            return moves['*']+moves['B']
        if self.board[row][col]=='k':
            moves = self.king(piece)
            return moves['*']+moves['W']
        return []

    # input format of square is [r,c] where r and c are row and column index of the square
    # output format is {'*':[moves],'W':[moves],'B':[moves]}
    def linear(self,square):
        moves={'*':[],'W':[],'B':[]}
        row,col=square
        r,c=row+1,col
        while r<=7:
            if self.board[r][c]!='*':
                if self.board[r][c].isupper():
                    moves['W'].append([r,c])
                elif self.board[r][c].islower():
                    moves['B'].append([r,c])
                break
            else:
                moves['*'].append([r,c])
                r+=1
        r=row-1
        while r>=0:
            if self.board[r][c]!='*':
                if self.board[r][c].isupper():
                    moves['W'].append([r,c])
                elif self.board[r][c].islower():
                    moves['B'].append([r,c])
                break
            else:
                moves['*'].append([r,c])
                r-=1
        r,c=row,col+1
        while c<=7:
            if self.board[r][c]!='*':
                if self.board[r][c].isupper():
                    moves['W'].append([r,c])
                elif self.board[r][c].islower():
                    moves['B'].append([r,c])
                break
            else:
                moves['*'].append([r,c])
                c+=1
        c=col-1
        while c>=0:
            if self.board[r][c]!='*':
                if self.board[r][c].isupper():
                    moves['W'].append([r,c])
                elif self.board[r][c].islower():
                    moves['B'].append([r,c])
                break
            else:
                moves['*'].append([r,c])
                c-=1
        return moves
        
    def diagonal(self,square):
        moves={'*':[],'W':[],'B':[]}
        row,col=square
        r,c=row+1,col+1
        while r<=7 and c<=7:
            if self.board[r][c]!='*':
                if self.board[r][c].isupper():
                    moves['W'].append([r,c])
                elif self.board[r][c].islower():
                    moves['B'].append([r,c])
                break
            else:
                moves['*'].append([r,c])
                r,c=r+1,c+1
        r,c=row-1,col+1
        while r>=0 and c<=7:
            if self.board[r][c]!='*':
                if self.board[r][c].isupper():
                    moves['W'].append([r,c])
                elif self.board[r][c].islower():
                    moves['B'].append([r,c])
                break
            else:
                moves['*'].append([r,c])
                r,c=r-1,c+1
        r,c=row+1,col-1
        while r<=7 and c>=0:
            if self.board[r][c]!='*':
                if self.board[r][c].isupper():
                    moves['W'].append([r,c])
                elif self.board[r][c].islower():
                    moves['B'].append([r,c])
                break
            else:
                moves['*'].append([r,c])
                r,c=r+1,c-1
        r,c=row-1,col-1
        while r>=0 and c>=0:
            if self.board[r][c]!='*':
                if self.board[r][c].isupper():
                    moves['W'].append([r,c])
                elif self.board[r][c].islower():
                    moves['B'].append([r,c])
                break
            else:
                moves['*'].append([r,c])
                r,c=r-1,c-1
        return moves
    def knight(self,square):
        moves={'*':[],'W':[],'B':[]}
        row,col=square
        possibilities = [[row+2,col+1],[row+1,col+2],[row-1,col-2],[row-2,col-1],[row-2,col+1],[row+2,col-1],[row+1,col-2],[row-1,col+2]]
        for i in possibilities:
            if i[0]>=0 and i[0]<=7 and i[1]>=0 and i[1]<=7:
                if self.board[i[0]][i[1]].isupper():
                    moves['W'].append(i)
                elif self.board[i[0]][i[1]].islower():
                    moves['B'].append(i)
                elif self.board[i[0]][i[1]]=='*':
                    moves['*'].append(i)
        return moves
    def king(self,square):
        row,col=square
        moves={'*':[],'W':[],'B':[]}
        possibilities=[[row+1,col+1],[row-1,col-1],[row,col+1],[row,col-1],[row+1,col],[row-1,col],[row+1,col-1],[row-1,col+1]]
        for i in possibilities:
            if i[0]>=0 and i[0]<=7 and i[1]>=0 and i[1]<=7:
                if self.board[i[0]][i[1]].isupper():
                    moves['W'].append(i)
                elif self.board[i[0]][i[1]].islower():
                    moves['B'].append(i)
                elif self.board[i[0]][i[1]]=='*':
                    moves['*'].append(i)
        return moves
