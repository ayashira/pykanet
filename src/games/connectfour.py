
class ConnectFour():
    '''
        Game of Connect Four
        rules reference: https://en.wikipedia.org/wiki/Connect_Four
    '''
    
    def __init__(self):
        # 0 = empty, 1 = occupied by player 1, 2 = occupied by player 2 
        self.board = [[0 for y in range(self.rows())] for x in range(self.cols())]
        self.current_player = 1
    
    def rows(self):
        return 6
        
    def cols(self):
        return 7
    
    # for display : width and height of a cell when displaying the game
    def cell_size(self):
        return 50, 50
    
    # for display: label for cell at coordinates (x, y)
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
    
    # update the board with the move from a player
    def play(self, move, player):
        #TODO
        
        # update the current_player
        self.current_player = 2 if self.current_player == 1 else 1

    def get_current_player(self):
        return self.current_player
    
    # must return -1 if game not finished, 0 if draw, 1 or 2 if player 1 or 2 has won
    def winner(self):
        #TODO
        pass
