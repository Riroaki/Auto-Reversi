from game import Game
from bot import ReversiBot

heading = """
 _____    _____   _     _   _____   _____    _____   _
|  _  \  | ____| | |   / / | ____| |  _  \  /  ___/ | |
| |_| |  | |__   | |  / /  | |__   | |_| |  | |___  | |
|  _  /  |  __|  | | / /   |  __|  |  _  /  \___  \ | |
| | \ \  | |___  | |/ /    | |___  | | \ \   ___| | | |
|_|  \_\ |_____| |___/     |_____| |_|  \_\ /_____/ |_|
"""

# Depth of minimax tree
DEPTH = 5


def main():
    game = Game()
    bot = ReversiBot()
    # Start game
    print(heading)
    game.start()
    game.show()
    print('You play black, and play first.')
    is_my_turn = True
    while True:
        try:
            # Human play
            if is_my_turn:
                row, col = list(map(int, input('Enter your play: [row] [col]\n'
                                               '>> ').split(' ')))
                game.move(row, col)
            # Auto play
            else:
                row, col = bot.analyze(game, DEPTH)
                game.move(row, col)
            # Display board & switch turn
            game.show()
            is_my_turn = not is_my_turn
            if game.state.is_finished():
                break
        except KeyboardInterrupt:
            print('Okay, bye')
            break
        except Exception as e:
            print(e)


if __name__ == '__main__':
    main()
