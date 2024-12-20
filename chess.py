from logic import Game

def main():
    mygame=Game()
    print(mygame.board)
    move=False
    while True:
        move=[i for i in input(f'{"White" if mygame.turn=="W" else "Black"}s turn\n Make your move: ').split(' ')]
        if move==['End']:
            print("Game ended")
            break
        else :
            mygame.move(move)
            print(mygame.board)

if __name__=='__main__':
    main()