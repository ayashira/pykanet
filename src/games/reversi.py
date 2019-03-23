'''
    Game of Reversi
    rules reference: https://en.wikipedia.org/wiki/Reversi
'''

import numpy as np
import itertools

class Reversi():

    def __init__(self, rows=8, cols=8):
        self._rows=rows
        self._cols=cols
        
        # 0 = empty, 1 = occupied by player 1, 2 = occupied by player 2 
        self.board  = np.zeros((self.rows(), self.cols()))
        self.current_player = 1
        
        # set the initial state(Othello opening)
        pos = (self.rows()//2-1, self.rows()//2)
        for p1, p2 in itertools.product(pos, pos):
            self.board[p1][p2] = ((p1-pos[0])^(p2-pos[0]))+1
    
    def rows(self):
        return self._rows
    
    def cols(self):
        return self._cols
    
    # for display : width and height of a cell when displaying the game
    def cell_size(self):
        return 40, 40
    
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
        x, y  = move
        return len(self.__flip_discs(x, y, player)) > 0
    
    # update the board with the move from a player
    def play(self, move, player):
        x, y = move
        fd = self.__flip_discs(x, y, player)
        if len(fd)>0:
            self.board[x][y] = player
            for ix, iy in fd:
                self.board[ix][iy] = player

        # update the current_player
        # same player plays again if opponent has no possible move
        next_player = 2 if self.current_player == 1 else 1
        if self._play_possible(next_player):
            self.current_player = next_player
    
    def get_current_player(self):
        return self.current_player
    
    # returns -1 if game is not finished, 0 if draw, 1 or 2 if player 1 or 2 has won
    def winner(self):
        blank = np.sum(self.board == 0)
        if blank > 0:
            # if any of the player can still play, game is not finished
            next_player = 2 if self.current_player == 1 else 1
            if self._play_possible(next_player) or self._play_possible(self.current_player):
                return -1
        
        # game is finished
        # the winner is the player with most discs
        point_1 = np.sum(self.board == 1)
        point_2 = np.sum(self.board == 2)
        
        if point_1 > point_2:
            return 1
        elif point_1 < point_2:
            return 2
        else:
            # point_1 == point_2, this is a draw
            return 0
    
    def __flip_discs(self, x, y, player):
        # list of possible straight 8 directions through the board
        # one direction is represented by the move variation on x and y axis
        # note : it also includes a useless "no move" direction 
        increment_funcs = (lambda x:x, lambda x:x+1, lambda x:x-1)
        directions = itertools.product(increment_funcs, increment_funcs)
        
        fd = []
        
        # non-empty cell
        if self.board[x][y] != 0:
            return fd

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
    
    def _play_possible(self, player):
        for row in range(self.rows()):
            for col in range(self.cols()):
                if len(self.__flip_discs(row, col, player)) > 0:
                    return True
        
        return False

# tests
if __name__ == '__main__':
    # check that a player cannot play
    reversi = Reversi(4, 4)
    reversi.board[0] = np.ones(4)*1
    reversi.board[1] = np.ones(4)*1
    reversi.board[2] = np.ones(4)*2
    reversi.current_player = 2
    if reversi._play_possible(2):
        print("FAIL. Player 2 should not be able to play.")
    else:
        print("OK")
