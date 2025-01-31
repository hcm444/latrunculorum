import chess
import chess_state

class MaterialEvaluator(object):
    def __init__(self, q=9, r=5, b=3, n=3, p=1):
        self.q, self.r, self.b, self.n, self.p = q, r, b, n, p
        self.values = {
            chess.PAWN: p,
            chess.KNIGHT: n,
            chess.BISHOP: b,
            chess.ROOK: r,
            chess.QUEEN: q,
        }

    def __call__(self, board):
        acc = 0
        for square, piece in board.piece_map().items():  # More efficient iteration
            acc += self.values.get(piece.piece_type, 0) * (1 if piece.color == chess.WHITE else -1)
        return acc


center = set([chess.D4, chess.D5, chess.E4, chess.E5])

class CenterControlEvaluator(object):
    def __call__(self, board):
        acc = 0
        for move in board.legal_moves:
            if move.to_square in center:  # Fix undefined variable
                acc += (1 if board.turn == chess.WHITE else -1)
        return acc


class MobilityEvaluator(object):
    def __call__(self, board):
        """For now, just return the number of legal moves"""
        return (len(list(board.legal_moves)) *
                (1 if board.turn == chess.WHITE else -1))
        

class KingSafetyEvaluator(object):
    def __call__(self, board):
        acc = 0

        if board.is_check():
            acc += -2 if board.turn == chess.WHITE else 2

        # This is probably stupid; we're already searching to some depth; this
        # probably only serves to preferentially increase depth by one for this
        # particular heuristic.
        for move in board.legal_moves:
            board.push(move)
            if board.is_check():
                acc += -1 if board.turn == chess.White else 1
            board.pop()

        return acc

class CompoundEvaluate(object):
    def __init__(self, evaluator_pairs=None):
        self.evaluators = evaluator_pairs or [(1, MaterialEvaluator())]

    def __call__(self, board):
        acc = 0
        for weight, evaluator in self.evaluators:
            acc += weight * evaluator(board)
        return acc
