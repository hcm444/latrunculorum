import argparse
import io
import chess
import chess_state
import evaluators
import minimax
argparser = argparse.ArgumentParser()
argparser.add_argument('--player', "-p", default="white", type=str, help="'[w]hite' or '[b]lack'; the bot player's color")
class Bot:
    def reset_game(self):
        self.state.reset()
        self.state.board = chess.Board()  # Ensure proper starting position
        self.player = chess.WHITE

    def __init__(self, player=chess.WHITE, searchdepth=5, evaluate=None, transposition_tables=True):
        self.state = chess_state.ChessState(
            evaluate=evaluate if evaluate else evaluators.MaterialEvaluator(),
            memoize=transposition_tables
        )
        self.player = player
        self.searchdepth = searchdepth
        self.wins = 0
        self.loses = 0
        self.stalemates = 0

    def reset_game(self):
        self.state.reset()
        self.player = chess.WHITE

    def choose_move(self):
        value, move = minimax.alphabeta(
            self.state,
            player=minimax.MAX if self.player == chess.WHITE else minimax.MIN,
            maxdepth=self.searchdepth
        )
        if move is None:
            legal_moves = list(self.state.legal_moves)
            if legal_moves:
                move = legal_moves[0]
        return value, move

    def make_move(self, move):
        if move and self.state.is_legal(move):
            if self.state.piece_type_at(move.from_square) == chess.PAWN or self.state.piece_at(move.to_square):
                self.state.values.clear()
            self.state.push(move)

    def analyze_position(self, fen):
        """Analyze a given FEN position and return the evaluation score."""
        self.state.board = chess.Board(fen)  # Load the position
        self.player = self.state.board.turn  # Update the player's turn

        value, _ = minimax.alphabeta(
            self.state,
            player=minimax.MAX if self.player == chess.WHITE else minimax.MIN,
            maxdepth=self.searchdepth
        )
        return value


class Supervisor:
    def __init__(self, number):
        self.bots = [Bot() for _ in range(number)]

    def begin(self):
        print("Starting bot matches...")
        while True:
            for bot in self.bots:
                for other_bot in self.bots:
                    if bot == other_bot:
                        continue
                    if bot.state.is_game_over() or other_bot.state.is_game_over():
                        print("Game over! Resetting...")
                        bot.reset_game()
                        other_bot.reset_game()
                        continue
                    value1, move1 = bot.choose_move()
                    if move1:
                        bot.make_move(move1)
                    value2, move2 = other_bot.choose_move()
                    if move2:
                        other_bot.make_move(move2)
                    print(other_bot.state)

def main():
    supervisor = Supervisor(3)
    supervisor.begin()

def main1(player=chess.WHITE, searchdepth=5):
    b = Bot(player=player, searchdepth=searchdepth)
    print("Initial Board State:")
    print(b.state, "\n")

    if player == chess.WHITE:
        value, m = b.choose_move()
        if m:
            print(value, m.uci())
            b.make_move(m)
            print(b.state, "\n")

    while True:
        try:
            move_str = input("Your move: ")
            m = chess.Move.from_uci(move_str)
            if not b.state.is_legal(m):
                raise ValueError
        except ValueError:
            print("Illegal move! Try again.")
            continue

        b.make_move(m)
        print(b.state, "\n")

        if b.state.is_game_over():
            print("Game over!")
            break

        value, m = b.choose_move()
        if m:
            print(value, m.uci())
            b.make_move(m)
            print(b.state, "\n")

        if b.state.is_game_over():
            print("Game over!")
            break



if __name__ == "__main__":
    args = argparser.parse_args()
    main1(player=chess.WHITE if args.player.lower().startswith("w") else chess.BLACK)

#Handler to use as a PGN analyzer. It actually worked on my local website
def analyze_pgn(pgn_data):
    """Analyze all moves in a PGN file with a lower depth for faster performance."""
    game = chess.pgn.read_game(io.StringIO(pgn_data))
    if game is None:
        return []

    bot = Bot(searchdepth=3)  # Reduce depth from 5 → 3 for speed
    bot.state.board = game.board()

    analysis_results = []
    move_number = 1

    for move in game.mainline_moves():
        bot.make_move(move)
        evaluation = bot.analyze_position(bot.state.fen())

        try:
            move_san = bot.state.board.san(move)
        except (AssertionError, ValueError):
            move_san = move.uci()

        analysis_results.append({
            "move_number": move_number,
            "move_san": move_san,
            "fen": bot.state.fen(),
            "evaluation": evaluation
        })

        move_number += 1

    return analysis_results



