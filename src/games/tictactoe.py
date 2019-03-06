
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
        x = move // 3
        y = move % 3
        return self.board[x][y] == 0
    
    #update the board with the move from a player
    def play(self, move, player):
        row = move // 3
        col = move % 3
        self.board[row][col] = player
    
    #indicate if a player has won or not, by checking if he has finished a line
    def has_won(self, player):
        for line in TicTacToe.lines:
            a, b, c = line
            if self.board[a[0]][a[1]] == self.board[b[0]][b[1]] == self.board[c[0]][c[1]] == player:
                return True
        return False
    
    #draw if all cells are occupied and no player wins
    def is_draw(self):
        for x in range(3):
            for y in range(3):
                if self.board[x][y] == 0:
                    return False
        
        if self.has_won(player=1) or self.has_won(player=2):
            return False
            
        return True
