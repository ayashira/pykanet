'''
    Class to create a game object from the game name
    All game names/classes should be added here 
'''

from games.tictactoe import TicTacToe
from games.connectfour import ConnectFour
from games.reversi import Reversi

class TurnBasedGameList():
    
    def get_game_from_name(game_name):
        if game_name.endswith("tic_tac_toe"):
            return TicTacToe()
        elif game_name.endswith("connect_four"):
            return ConnectFour()
        elif game_name.endswith("reversi"):
            return Reversi()
