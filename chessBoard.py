import numpy as np

class chessBoard:
    def __init__(self,position:str='rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR',showNotation:bool=True):
        self.pieces = [i for i in 'rnbqkpPRNBQK']
        self.showNotation = showNotation
        if position=='' or position.lower()=='empty':
            self.chessBoard =np.array([' * ' for i in range(64)]).reshape(-1,8)
            return None
        else:
            self.chessBoard = self.setPosition(position)
        
    def setPosition(self,fen):
        chessBoard =np.array(['*' for i in range(64)])
        rows = fen.split('/')
        index=0
        if len(rows)!=8:
            raise ValueError("Invalid FEN value.")
        for row in range(len(rows)):
            for piece in rows[row]:
                if piece.isdigit():
                    # print(f'{piece} is digit')
                    index+=int(piece)
                else:
                    chessBoard[index]=piece
                    index+=1
            index = 8*(row+1)
        return chessBoard.reshape(-1,8)

    def fen(self):
        fen=''
        for i in range(len(self.chessBoard)):
            count=0
            for piece in self.chessBoard[i]:
                if piece=='*':
                    count+=1
                else:
                    if count>0:
                        fen+=str(count)
                        count=0
                    fen+=piece
            if count>0:
                fen+=str(count)
                count=0
            fen+='/' if i!=7 else ''
        return fen
            
        
    def __str__(self):
        chessBoardStr = ''
        for row in range(len(self.chessBoard)):
            chessBoardStr+=f' {8-row} ' if self.showNotation==True else ''
            for piece in self.chessBoard[row]:
                chessBoardStr+=f' {piece} ' #Additional Spaces for better looks
            chessBoardStr+='\n'
        chessBoardStr+=''.join([f' {file} ' for file in ' abcdefgh']) if self.showNotation else ''
        return chessBoardStr
        
    def __getitem__(self,index):
        return self.chessBoard[index]

    def __setitem__(self,index,value):
        if isinstance(index,int):
            self.chessBoard[index]=value
        elif isinstance(index,tuple):
            self.chessBoard[index[0]][index[1]]=value