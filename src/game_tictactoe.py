
class TicTacToe():
    
    #coordinates of the cell for each possible line
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
        self.board = [[0 for y in range(3)] for x in range(3)]
    
    #a move by a player is valid if the cell is empty
    def is_valid_play(self, move, player):
        row = move // 3
        col = move % 3
        if self.board[row][col] == 0:
            return True
        else:
            return False
    
    #update the board with the move from a player
    def play(self, move, player):
        row = move // 3
        col = move % 3
        self.board[row][col] = player
    
    #indicate if a player has won or not, by checking if he has finished a line
    def has_won(self, player):
        for line in TicTacToe.lines:
            a, b, c = line
            if self.board[a[0]][a[1]]==player and self.board[b[0]][b[1]]==player and self.board[c[0]][c[1]]==player:
                return True
        return False
