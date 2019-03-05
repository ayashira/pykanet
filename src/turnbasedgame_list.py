#All turn-based games should be added here to link "game names" and classes

from game_tictactoe import TicTacToe

class TurnBasedGame_List():
    
    def get_game_from_name(game_name):
        if game_name.endswith("tic_tac_toe"):
            return TicTacToe()
