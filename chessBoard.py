class chessBoard:
    def __init__(self, position: str = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1',
                 showNotation: bool = True):
        self.pieces = [i for i in 'rnbqkpPRNBQK']
        self.showNotation = showNotation
        self.turn = ""
        self.castle = {'K' : True, 'Q' : True, 'k' : True, 'q' : True} #White King Side Castle, White Queen Side castle, Black King Side Castle, Black Queen Side Castle
        self.enPassant = ""
        self.halfMoves, self.fullMoves = 0, 0
        if position == '' or position.lower() == 'empty':
            self.chessBoard = [[' * ' for i in range(8)] for j in range(8)]
            return None
        else:
            self.chessBoard = self.setPosition(position)

    def setPosition(self, fen):
        chessBoard = ['*' for i in range(64)]
        pos = fen.split(" ")
        self.turn = pos[1]
        self.Kcastle = "K" in pos[2]
        self.kcastle = "k" in pos[2]
        self.Qcastle = "Q" in pos[2]
        self.qcastle = "q" in pos[2]
        self.enPassant = pos[3]
        self.halfMoves = int(pos[4])
        self.fullMoves = int(pos[5])
        rows = pos[0].split('/')
        index = 0
        if len(rows) != 8:
            raise ValueError("Invalid FEN value.")
        for row in range(len(rows)):
            for piece in rows[row]:
                if piece.isdigit():
                    # print(f'{piece} is digit')
                    index += int(piece)
                else:
                    chessBoard[index] = piece
                    index += 1
            index = 8 * (row + 1)
        cb = chessBoard.copy()
        chessBoard = [cb[8*i:(8*i)+8] for i in range(8)]
        return chessBoard

    def fen(self):
        fen = ''
        for i in range(len(self.chessBoard)):
            count = 0
            for piece in self.chessBoard[i]:
                if piece == '*':
                    count += 1
                else:
                    if count > 0:
                        fen += str(count)
                        count = 0
                    fen += piece
            if count > 0:
                fen += str(count)
                count = 0
            fen += '/' if i != 7 else ''
        fen += " " + self.turn + " "
        castling = "".join(["K" if self.Kcastle else "", "Q" if self.Qcastle else "", "k" if self.kcastle else "","q" if self.qcastle else ""])
        if not castling:
            fen += "- "
        else:
            fen += castling + " "
        fen += self.enPassant + " " + str(self.halfMoves) + " " + str(self.fullMoves)
        return fen

    def __str__(self):
        chessBoardStr = ''
        for row in range(len(self.chessBoard)):
            chessBoardStr += f' {8 - row} ' if self.showNotation == True else ''
            for piece in self.chessBoard[row]:
                chessBoardStr += f' {piece} '  # Additional Spaces for better looks
            chessBoardStr += '\n'
        chessBoardStr += ''.join([f' {file} ' for file in ' abcdefgh']) if self.showNotation else ''
        return chessBoardStr

    def __getitem__(self, index):
        return self.chessBoard[index]

    def __setitem__(self, index, value):
        if isinstance(index, int):
            self.chessBoard[index] = value
        elif isinstance(index, tuple):
            self.chessBoard[index[0]][index[1]] = value