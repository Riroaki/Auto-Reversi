import random
from itertools import combinations_with_replacement
from enum import Enum


class COLOR(Enum):
    """State of a cell: black / white / untouched."""
    BLACK = 1
    WHITE = 0
    UNTOUCHED = -1


class GAMESTATE(Enum):
    """State of game:
    - initializing
    - game running: white's turn / black's turn,
    - game finished: black win / white win / draw.
    """
    INITIALIZING = 0
    RUNNING_BLACK = 1
    RUNNING_WHITE = 2
    WIN_BLACK = 3
    WIN_WHITE = 4
    DRAW = 5

    def is_running(self):
        return self in [GAMESTATE.RUNNING_WHITE, GAMESTATE.RUNNING_BLACK]

    def is_finished(self):
        return self in [GAMESTATE.WIN_BLACK, GAMESTATE.WIN_WHITE,
                        GAMESTATE.DRAW]


class Game(object):
    """Reversi game."""

    # Size of game board
    BOARD_SIZE = 8
    # 8 directions to search
    DIRECTIONS = [(-1, -1), (-1, 0), (-1, 1),
                  (0, -1), (0, 1),
                  (1, -1), (1, 0), (1, 1)]

    def __init__(self):
        self.board = [[COLOR.UNTOUCHED for _ in range(self.BOARD_SIZE)] for
                      _ in range(self.BOARD_SIZE)]
        self._state = GAMESTATE.INITIALIZING
        self._legal_moves = {}
        self._my_color = None
        self._opponent_color = None
        self._remain = 0
        self._white_count = 0
        self._black_count = 0
        # Record continuous rounds with no legal moves
        self._no_move_round = 0

    def _switch_side(self):
        # Switch black / white side
        assert self._state.is_running()
        if self._state == GAMESTATE.RUNNING_BLACK:
            self.state = GAMESTATE.RUNNING_WHITE
        else:
            self.state = GAMESTATE.RUNNING_BLACK
        # Check legal moves
        legal_moves = self._search_legal_moves()
        # Change state if no legal moves could be made
        if len(legal_moves) > 0:
            self._no_move_round = 0
            self._legal_moves = legal_moves
        else:
            self._no_move_round += 1
            # Both sides could not make legal moves: game is over
            if self._no_move_round >= 2:
                self._end()

    def start(self, black_first: bool = True) -> None:
        # Initialize board
        colors = [COLOR.BLACK, COLOR.WHITE]
        random.shuffle(colors)
        self.board[3][3] = colors[0]
        self.board[3][4] = colors[1]
        self.board[4][3] = colors[1]
        self.board[4][4] = colors[0]
        # Initialize game data
        self._count_board()
        # Initialize game state
        if black_first:
            self.state = GAMESTATE.RUNNING_BLACK
        else:
            self.state = GAMESTATE.RUNNING_WHITE
        self._legal_moves = self._search_legal_moves()

    def move(self, row: int, col: int) -> None:
        try:
            # Search available directions
            available_directions = self._legal_moves[(row, col)]
            # Reverse on available directions
            self.board[row][col] = self._my_color
            for d in available_directions:
                r, c = row + d[0], col + d[1]
                while self.board[r][c] == self._opponent_color:
                    self.board[r][c] = self._my_color
                    r, c = r + d[0], c + d[1]
            # Check game count and state
            self._count_board()
            if self._remain == 0:
                self._end()
            else:
                self._switch_side()
        except KeyError:  # Not legal move
            print('Not a legal move!')
            return

    def _search_legal_moves(self) -> dict:
        # Check whether in running status
        assert self._state.is_running()
        legal_moves = {}
        # Iterates on each cell
        for row in range(self.BOARD_SIZE):
            for col in range(self.BOARD_SIZE):
                if self.board[row][col] == COLOR.UNTOUCHED:
                    directions = self._search_available_directions(row, col)
                    # No available directions: illegal
                    if len(directions) > 0:
                        move = (row, col)
                        legal_moves[move] = directions
        return legal_moves

    def _search_available_directions(self, row: int, col: int) -> list:
        directions = []
        # Search in 8 directions
        for d in self.DIRECTIONS:
            r, c = row + d[0], col + d[1]
            count = 0
            while 0 <= r < self.BOARD_SIZE and 0 <= c < self.BOARD_SIZE \
                    and self.board[r][c] == self._opponent_color:
                r, c = r + d[0], c + d[1]
                count += 1
            # Requires opponent's color count > 0 and meet my color in the end
            if count > 0:
                if 0 <= r < self.BOARD_SIZE and 0 <= c < self.BOARD_SIZE:
                    if self.board[r][c] == self._my_color:
                        directions.append(d)
        return directions

    def _count_board(self):
        # Count numbers of each side
        white, black, remain = 0, 0, 0
        for row in range(self.BOARD_SIZE):
            for col in range(self.BOARD_SIZE):
                white += self.board[row][col] == COLOR.WHITE
                black += self.board[row][col] == COLOR.BLACK
                remain += self.board[row][col] == COLOR.UNTOUCHED
        self._remain = remain
        self._white_count = white
        self._black_count = black

    def _end(self):
        if self._white_count == self._black_count:
            self.state = GAMESTATE.DRAW
        elif self._white_count > self._black_count:
            self.state = GAMESTATE.WIN_WHITE
        else:
            self.state = GAMESTATE.WIN_BLACK

    @property
    def my_color(self) -> COLOR:
        return self._my_color

    @property
    def opponent_color(self) -> COLOR:
        return self._opponent_color

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value: GAMESTATE):
        self._state = value
        if value == GAMESTATE.RUNNING_BLACK:
            self._my_color = COLOR.BLACK
            self._opponent_color = COLOR.WHITE
        elif value == GAMESTATE.RUNNING_WHITE:
            self._my_color = COLOR.WHITE
            self._opponent_color = COLOR.BLACK

    def show(self):
        signs = {
            COLOR.UNTOUCHED: '_',
            COLOR.BLACK: '*',
            COLOR.WHITE: 'O'
        }
        legal_move_sign = '.'
        # Display game board
        for row in range(len(self.board)):
            for col in range(len(self.board[0])):
                if (row, col) in self._legal_moves:
                    print(legal_move_sign, end=' ')
                else:
                    print(signs[self.board[row][col]], end=' ')
            print()
