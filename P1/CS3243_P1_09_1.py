# CS3243 Introduction to Artificial Intelligence
# Project 1: k-Puzzle

import os
import sys
from time import time

from collections import deque

# Running script on your own - given code can be run with the command:
# python file.py, ./path/to/init_state.txt ./output/output.txt

class Puzzle(object):
    def __init__(self, init_state, goal_state):
        # you may add more attributes if you think is useful
        self.init_state = init_state
        self.goal_state = goal_state
        self.actions = list()
        self.zero = (0,0) #location of 0

    def solve(self):
        #TODO
        # implement your search algorithm here
        st = time()
        if not self.solvable():
            return ["UNSOLVABLE"]
        dir = ('UP', 'DOWN', 'LEFT', 'RIGHT')
        vis = {} #bool array
        q = deque()
        q.append(self)
        vis[self.make_int()] = True 
        # c = 1
        while q:
            # c+=1
            # if c>5: break
            curr_puzzle = q.popleft()
            for d in dir:
                next_state = curr_puzzle.next_state(d)
                # if next state invalid or visited skip
                # if next_state: 
                    # print(next_state.make_int())
                    # print("vis", vis)
                    # print (next_state.init_state in vis)
                if (not next_state) or next_state.make_int() in vis: 
                    continue 
                if next_state.init_state == self.goal_state:
                    # print (next_state.actions)
                    print 'fn took %.2f seconds' % (time() - st)
                    return next_state.actions
                q.append(next_state)
                vis[next_state.make_int()] = True
         # sample output 
    
    
    # you may add more functions if you think is useful
    def set_actions(self, actions):
        self.actions = actions
    
    def set_zero(self, zero):
        self.zero = zero
    
    def flatten(self):
        return [num for row in self.init_state for num in row]
    
    def make_int(self):
        return int(''.join(str(e) for e in self.flatten()))
    
    # To determine solvability
    def solvable(self):
        width = len(self.init_state)
        lst = self.flatten()
        size = len(lst)
        # Use conditions of inversions
        # https://www.cs.bham.ac.uk/~mdr/teaching/modules04/java2/TilesSolvability.html
        inv, row, zrow = 0, 0, 0
        for i in range(size):
            if (i and i % width == 0):
                row += 1
            # Store zero row
            if (lst[i] == 0):
                zrow = row
                self.set_zero((row, i % width))
                continue
            # Check for inversions here
            for j in range(i + 1, size):
                if (lst[j] and lst[i] > lst[j]):
                    inv += 1
        
        even_inv = inv % 2 == 0
        # If grid width is odd, inversions must be even
        if width % 2:
            return even_inv 
        
        # If grid width is even,
        # if inv is odd, blank row is even from bottom (1-based)
        # if inv is even, blank row is odd from bottom (1-based)
        return even_inv == zrow % 2

    
    # def find_zero(self, state):
        # for i in range(len(state)):
            # for j in range(len(state[0])):
                # if state[i][j] == 0:
                    # return i, j
                    
    # Returns a puzzle state given a direction
    def next_state(self, dir):
        i, j = self.zero
        
        r, c = self.get_direction(dir)
        n_i, n_j = i + r, j + c
        # If out of bounds invalid, return None
        if (n_i < 0 or n_i >= len(self.init_state[0]) \
            or n_j < 0 or n_j >= len(self.init_state)): 
            return None
        
        # Set init variables for new puzzle state
        new_zeros = (n_i, n_j)
        new_actions = list(self.actions)
        new_actions.append(dir)
        next_num = self.init_state[n_i][n_j]
        # Copy the current_state
        new_state = [row[:] for row in self.init_state]
        
        new_state[i][j] = next_num
        new_state[n_i][n_j] = 0
        # self.printg(new_state)
        # Initialize new puzzle state
        new_puzzle = Puzzle(new_state, self.goal_state)
        new_puzzle.set_actions(new_actions)
        new_puzzle.set_zero(new_zeros)
        return new_puzzle
    
    def get_direction(self, dir):
        dict = {'UP' : (1,0), 'DOWN' : (-1,0), 'RIGHT' : (0,-1), 'LEFT' : (0,1)}
        return dict[dir]
    
    def printg(self, grid):
        for row in grid:
            print(row)
        print()



if __name__ == "__main__":
    # do NOT modify below

    # argv[0] represents the name of the file that is being executed
    # argv[1] represents name of input file
    # argv[2] represents name of destination output file
    if len(sys.argv) != 3:
        raise ValueError("Wrong number of arguments!")

    try:
        f = open(sys.argv[1], 'r')
    except IOError:
        raise IOError("Input file not found!")

    lines = f.readlines()
    
    # n = num rows in input file
    n = len(lines)
    # max_num = n to the power of 2 - 1
    max_num = n ** 2 - 1

    # Instantiate a 2D list of size n x n
    init_state = [[0 for i in range(n)] for j in range(n)]
    goal_state = [[0 for i in range(n)] for j in range(n)]
    

    i,j = 0, 0
    for line in lines:
        for number in line.split(" "):
            if number == '':
                continue
            value = int(number , base = 10)
            if  0 <= value <= max_num:
                init_state[i][j] = value
                j += 1
                if j == n:
                    i += 1
                    j = 0

    for i in range(1, max_num + 1):
        goal_state[(i-1)//n][(i-1)%n] = i
    goal_state[n - 1][n - 1] = 0

    puzzle = Puzzle(init_state, goal_state)
    ans = puzzle.solve()

    with open(sys.argv[2], 'a') as f:
        for answer in ans:
            f.write(answer+'\n')







