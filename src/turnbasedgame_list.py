#All turn-based games should be added here to link "game names" and classes

from game_tictactoe import TicTacToe
from game_connectfour import ConnectFour
from game_reversi import Reversi

class TurnBasedGame_List():
    
    def get_game_from_name(game_name):
        if game_name.endswith("tic_tac_toe"):
            return TicTacToe()
        elif game_name.endswith("connect_four"):
            return ConnectFour()
        elif game_name.endswith("reversi"):
            return Reversi()
