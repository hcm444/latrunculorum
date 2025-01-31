import argparse
import chess
import sys
import chess_state
import evaluators
import minimax
import time

argparser = argparse.ArgumentParser()
argparser.add_argument('--player', "-p", default="white", type=str, help="'[w]hite' or '[b]lack'; the bot player's color")

class Bot:
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
    if player == chess.WHITE:
        value, m = b.choose_move()
        if m:
            print(value, m.uci())
            b.make_move(m)
            print(b.state, "\n")
    while True:
        try:
            m = chess.Move.from_uci(input("Your move: "))
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
