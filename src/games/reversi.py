# Game of Reversi
#rules reference: https://en.wikipedia.org/wiki/Reversi

class Reversi():
    
    def __init__(self):
        #0 = empty, 1 = occupied by player 1, 2 = occupied by player 2 
        self.board = [[0 for y in range(self.rows())] for x in range(self.cols())]
    
    def rows(self):
        return 8
        
    def cols(self):
        return 8
    
    #for display : width and height of a cell when displaying the game
    def cell_size(self):
        return 40, 40
    
    #for display: label for cell at coordinates (x, y)
    def get_label(self, x, y):
        s = self.board[x][y]
        if s == 0:
            return ""
        elif s == 1:
            return "O"
        elif s == 2:
            return "X"
    
    def is_valid_play(self, move, player):
        #TODO
        pass
    
    #update the board with the move from a player
    def play(self, move, player):
        #TODO
        pass
    
    #indicate if a player has won or not
    def has_won(self, player):
        #TODO
        pass
    
    #draw if all cells are occupied and no player wins
    def is_draw(self):
        #TODO
        pass
