import chess

class ChessState(chess.Board):
    def __init__(self, evaluate=None, memoize=False, fen=chess.STARTING_FEN):
        self.evaluate = evaluate if evaluate else (lambda _: 0)
        self.memoize = memoize
        self.values = {} if memoize else None
        super().__init__(fen=fen)  # Ensure the board is initialized with the correct FEN


    def __str__(self):
        result = ['  A B C D E F G H']
        for i in range(8):
            row = [str(8 - i) + ' ']
            for j in range(8):
                piece = self.piece_at(chess.square(j, 7 - i))
                row.append(piece.symbol() if piece else '.')
            result.append(' '.join(row))
        return '\n'.join(result)

    def winner(self):
        if self.is_stalemate() or self.is_insufficient_material() or self.can_claim_draw():
            return None
        if not self.is_game_over():
            return False
        return chess.WHITE if self.turn == chess.BLACK else chess.BLACK

    def hashable(self):
        return (
            self.occupied_co[chess.WHITE],
            self.occupied_co[chess.BLACK],
            self.pawns, self.knights, self.bishops, self.rooks, self.queens, self.kings
        )

    def value(self):
        if self.is_checkmate():
            return float("-1000") if self.turn == chess.WHITE else float(
                "1000")  # Assign a large positive/negative value
        if self.is_stalemate() or self.is_insufficient_material() or self.can_claim_draw():
            return 0  # Draw positions should be evaluated as 0

        # Default evaluation
        return self.evaluate(self)

    def moves(self):
        for move in self.legal_moves:
            self.push(move)
            yield move, self
            self.pop()

    def do(self, move):
        new_state = ChessState(evaluate=self.evaluate, fen=self.fen(), memoize=self.memoize)
        new_state.push(move)
        return new_state

    def is_terminal(self):
        return self.is_game_over()
