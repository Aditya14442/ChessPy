import pygame,sys
from logic import Game


pygame.init()
win_height,win_width=1024,1024
square_height,square_width=win_height//8,win_width//8

screen = pygame.display.set_mode((win_width,win_height))
pygame.display.set_caption("ChessPy")
clock=pygame.time.Clock()

game = Game()

highlightedSquares=[]
selectedPiece=[0,0]

images = {
    'K': pygame.image.load("./resources/chessPieces/white-king.png"),
    'k': pygame.image.load("./resources/chessPieces/black-king.png"),
    'Q': pygame.image.load("./resources/chessPieces/white-queen.png"),
    'q': pygame.image.load("./resources/chessPieces/black-queen.png"),
    'N': pygame.image.load("./resources/chessPieces/white-knight.png"),
    'n': pygame.image.load("./resources/chessPieces/black-knight.png"),
    'R': pygame.image.load("./resources/chessPieces/white-rook.png"),
    'r': pygame.image.load("./resources/chessPieces/black-rook.png"),
    'B': pygame.image.load("./resources/chessPieces/white-bishop.png"),
    'b': pygame.image.load("./resources/chessPieces/black-bishop.png"),
    'P': pygame.image.load("./resources/chessPieces/white-pawn.png"),
    'p': pygame.image.load("./resources/chessPieces/black-pawn.png"),
}
boardColour={
    "White": (222, 184, 135),
    "Black":(101, 67, 33)
}

GameEnded=False

def drawBoard():
    for i in range(8):
        for j in range(8):
            pygame.draw.rect(screen,boardColour["White" if (i+j)%2==0 else "Black"],(square_width*i,
                                                                                   square_height*j,
                                                                                   square_width,square_height))
def placePieces():
    for rank in range(len(game.board.chessBoard)):
        for file in range(len(game.board[rank])):
            if game.board[rank][file]!='*':
                screen.blit(pygame.transform.scale(images[game.board[rank][file]],(square_width,square_height)),
                            (file*square_width,
                                                                             rank*square_height))
def highlightSquare(squarePosition,hColour=(0,255,0)):
    squarePosition=squarePosition[:2][::-1]
    pygame.draw.rect(screen,hColour,(square_width*squarePosition[0],square_height*squarePosition[1],square_width,
                                     square_height))
def showText(text,size=72,padding=20):
    text_surface=pygame.font.Font(None, size).render(text, True, (255, 255, 255))
    position = ((win_width-text_surface.get_width())//2,(win_height-text_surface.get_height())//2)
    pygame.draw.rect(screen,(0,0,0),(position[0]-padding,position[1]-padding,text_surface.get_width()+(2*padding),
                                     text_surface.get_height()+(2*padding)))
    screen.blit(text_surface,position)
while True:
    screen.fill((0, 0, 0))
    GameEnded=game.CheckMateOrStaleMate
    drawBoard()
    for event in pygame.event.get():
        if event.type==pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type==pygame.MOUSEBUTTONDOWN:
            mouseX,mouseY=event.pos[::-1]
            mouseX=mouseX//square_width
            mouseY=mouseY//square_height
            if selectedPiece and selectedPiece==[mouseX,mouseY]:
                selectedPiece=[]
            elif selectedPiece and [mouseX,mouseY] in highlightedSquares:
                try:
                    game.move(game.encodeMove([selectedPiece,[mouseX,mouseY]]))
                    highlightedSquares=[]
                    selectedPiece=[]
                    continue
                except Exception as e:
                    print(e)
                    highlightedSquares=[]
                    selectedPiece=[]
                    continue
            else:
                selectedPiece=[mouseX,mouseY]
            highlightedSquares = []
            if selectedPiece:
                for i in game.PossibleMoves(selectedPiece):
                    highlightedSquares.append(i[:2])

    for i in highlightedSquares:
        highlightSquare(i)


    placePieces()
    if GameEnded:
        showText(f'Game ended by {GameEnded}')
    pygame.display.flip()
    clock.tick(60)