# Game of Reversi
#rules reference: https://en.wikipedia.org/wiki/Reversi
import numpy as np
import itertools

class Reversi():

    def __init__(self):
        #0 = empty, 1 = occupied by player 1, 2 = occupied by player 2 
        self.board  = np.zeros((self.rows(), self.cols()))
        
        #set the initial state(Othello opening)
        pos = (self.rows()//2-1, self.rows()//2)
        for p1, p2 in itertools.product(pos, pos):
            self.board[p1][p2] = ((p1-pos[0])^(p2-pos[0]))+1

    
    def rows(self):
        return 4
        
    def cols(self):
        return 4
    
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
        x = move // self.rows()
        y = move % self.cols()
        #return self.board[x][y] == 0
        return len(self.__flip_discs(x, y, player)) > 0 
    
    #update the board with the move from a player
    def play(self, move, player):
        x = move // self.rows()
        y = move % self.cols()
        fd = self.__flip_discs(x, y, player)
        if len(fd)>0:
            self.board[x][y] = player
            for ix, iy in fd:
                self.board[ix][iy] = player
        
    
    #indicate if a player has won or not
    def has_won(self, player):
        point = np.sum(self.board == player)
        other_point = np.sum((self.board != player) & (self.board != 0))
        blank = np.sum(self.board == 0)
        if (point >= other_point) and (blank == 0):
                return True
        else:
            return False
    
    #draw if all cells are occupied and no player wins
    def is_draw(self):
        for x in range(self.rows()):
            for y in range(self.cols()):
                if self.board[x][y] == 0:
                    return False

        if self.has_won(player=1) or self.has_won(player=2):
            return False
            
        return True

    
    def __flip_discs(self, x, y, player):
        #list of possible straight 8 directions through the board
        #one direction is represented by the move variation on x and y axis
        #note : it also includes a useless "no move" direction 
        increment_funcs = (lambda x:x, lambda x:x+1, lambda x:x-1)
        directions = itertools.product(increment_funcs, increment_funcs)
        
        fd = []
        for f1, f2 in directions:
            dx, dy = f1(x), f2(y)
            stack = []
            while(True):
                # range out
                if (dx < 0) or (dx >= self.rows()) or \
                        (dy < 0) or (dy >= self.cols()):
                    stack = []
                    break
                # empty cell
                elif(self.board[dx][dy] == 0):
                    stack = []
                    break
                # reach player's disc
                elif(self.board[dx][dy] == player):
                    break
                # reach other player's disc
                else:
                    stack.append([dx, dy])
                    dx, dy = f1(dx), f2(dy)

            fd += stack
        return fd
