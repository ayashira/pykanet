
class TicTacToe():
    
    #coordinates of the cells for each possible line
    lines = [ [(0,0), (0,1), (0,2)],
          [(1,0), (1,1), (1,2)],
          [(2,0), (2,1), (2,2)],
          [(0,0), (1,0), (2,0)],
          [(0,1), (1,1), (2,1)],
          [(0,2), (1,2), (2,2)],
          [(0,0), (1,1), (2,2)],
          [(0,2), (1,1), (2,0)]
        ]
    
    def __init__(self):
        #3x3 board, 0 = empty, 1 = occupied by player 1, 2 = occupied by player 2 
        self.board = [[0 for y in range(self.rows())] for x in range(self.cols())]
        self.current_player = 1
        
    def rows(self):
        return 3
        
    def cols(self):
        return 3
    
    #for display : width and height of a cell when displaying the game
    def cell_size(self):
        return 80, 80
    
    #for display: label for cell at coordinates (x, y)
    def get_label(self, x, y):
        s = self.board[x][y]
        if s == 0:
            return ""
        elif s == 1:
            return "O"
        elif s == 2:
            return "X"
    
    #a move by a player is valid if the cell is empty
    def is_valid_play(self, move, player):
        x, y = move
        return self.board[x][y] == 0
    
    #update the board with the move from a player
    def play(self, move, player):
        x, y = move
        self.board[x][y] = player
        
        #update the current_player
        self.current_player = 2 if self.current_player == 1 else 1
    
    def get_current_player(self):
        return self.current_player
    
    #return -1 if the game is not finished, 0 if draw, 1 or 2 if one of the player wins
    def winner(self):
        for line in TicTacToe.lines:
            a, b, c = line
            if self.board[a[0]][a[1]] != 0 and \
               self.board[a[0]][a[1]] == self.board[b[0]][b[1]] == self.board[c[0]][c[1]]:
                #one of the player won, return the player id (1 or 2)
                return self.board[a[0]][a[1]]
        
        #no player has won yet, check for a draw
        for x in range(3):
            for y in range(3):
                if self.board[x][y] == 0:
                    #play still possible, game not finished
                    return -1
        
        #no play is possible anymore, this is a draw
        return 0
