from copy import deepcopy
from game import Game, COLOR


class ReversiBot(object):
    """Automatically playing reversi games."""

    # Constant numbers
    # Infinity
    INF = 10000
    # 8 directions to search
    DIRECTIONS = [(-1, -1), (-1, 0), (-1, 1),
                  (0, -1), (0, 1),
                  (1, -1), (1, 0), (1, 1)]

    # Scores for different type of cells
    SCORE_CORNER = 100
    SCORE_AROUND = -10
    SCORE_BOUND = 10
    SCORE_NORMAL = 1

    # Record colors
    my_color: COLOR
    opponent_color: COLOR

    def analyze(self, game: Game, depth: int) -> tuple:
        assert game.state.is_running() and depth > 0
        self.my_color = game.my_color
        self.opponent_color = game.opponent_color
        # Build minimax game tree and choose max value
        move, _ = self._negamax(game.board, depth, -self.INF, self.INF, True)
        return move

    def _negamax(self, board: list, depth: int, alpha: int, beta: int,
                 is_max: bool) -> tuple:
        # Find best move using negamax strategy with alpha-beta pruning
        flag = 1 if is_max else -1
        # Leaf node
        if depth <= 0:
            return None, flag * self._evaluate(board)
        # Get current legal moves
        legal_moves = self._search_legal_moves(board, is_max)
        # Neither could not move
        if len(legal_moves) == 0:
            opponent_legal_moves = self._search_legal_moves(board, not is_max)
            if len(opponent_legal_moves) == 0:
                return None, flag * self._evaluate(board)
            else:
                _, score = self._negamax(board, depth - 1, -beta, -alpha,
                                         not is_max)
                return None, -score
        # Try each move and do pruning
        if is_max:
            my_color, opponent_color = self.my_color, self.opponent_color
        else:
            my_color, opponent_color = self.opponent_color, self.my_color
        # Try each move
        max_move, max_score = None, -self.INF
        for move, directions in legal_moves.items():
            # Copy a new board and make move
            new_board = deepcopy(board)
            row, col = move
            new_board[row][col] = my_color
            for d in directions:
                r, c = row + d[0], col + d[1]
                while new_board[r][c] == opponent_color:
                    new_board[r][c] = my_color
            _, score = self._negamax(new_board, depth - 1, -beta, -alpha,
                                     not is_max)
            score = -score
            # Pruning, and keep move with maximum score
            if score > alpha:
                if score >= beta:
                    return move, score
                alpha = max(alpha, score)
            if score > max_score:
                max_move, max_score = move, score
        return max_move, max_score

    def _search_legal_moves(self, board: list, is_max: bool) -> dict:
        def _search_available_directions() -> list:
            d_list = []
            # Search in 8 directions
            for d in self.DIRECTIONS:
                r, c = row + d[0], col + d[1]
                count = 0
                while 0 <= r < len(board) and 0 <= c < len(board[0]) \
                        and board[r][c] == opponent_color:
                    count += 1
                    r, c = row + d[0], col + d[1]
                # Requires opponent's color count > 0 and meet my color at last
                if count > 0 and 0 <= r < len(board) and 0 <= c < len(board[0]):
                    if board[r][c] == my_color:
                        d_list.append(d)
                return d_list

        # Assign colors
        if is_max:
            my_color, opponent_color = self.my_color, self.opponent_color
        else:
            my_color, opponent_color = self.opponent_color, self.my_color
        # Search legal moves for black / white color
        legal_moves = {}
        for row in range(len(board)):
            for col in range(len(board[0])):
                if board[row][col] == COLOR.UNTOUCHED:
                    directions = _search_available_directions()
                    if len(directions) > 0:
                        move = (row, col)
                        legal_moves[move] = directions
        return legal_moves

    def _evaluate(self, board: list) -> int:
        # Heuristic way of calculating board score
        size = len(board)
        # Score weights: cells with different positions have different weights
        weights = [[0 for _ in range(size)] for _ in range(size)]
        bound = {0, size - 1}
        around = {0, 1, size - 2, size - 1}
        for row in range(size):
            for col in range(size):
                # Normal positions
                if 0 < row < size - 1 and 0 < col < size - 1:
                    weights[row][col] = self.SCORE_NORMAL
                # Most important positions: corner
                elif row in bound and col in bound:
                    weights[row][col] = self.SCORE_CORNER
                # Undesired positions: cells around corners
                elif row in around and col in around:
                    weights[row][col] = self.SCORE_AROUND
                # Boundary positions but neither corners nor corners' neighbors
                else:
                    weights[row][col] = self.SCORE_BOUND
        # Cell score: calculate sum of weighted cells
        cell_score = 0
        for row in range(size):
            for col in range(size):
                if board[row][col] == self.my_color:
                    cell_score += weights[row][col]
                elif board[row][col] == self.opponent_color:
                    cell_score -= weights[row][col]
        # Freedom score: see how many probabilities have been left for opponent
        opponent_moves = self._search_legal_moves(board, False)
        my_moves = self._search_legal_moves(board, True)
        freedom_score = 0
        if len(opponent_moves) == 0:
            freedom_score += 100
        if len(my_moves) == 0:
            freedom_score -= 100
        # Total score
        score = cell_score + freedom_score
        return score
