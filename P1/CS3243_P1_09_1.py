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
        self.init_state_flat = self.flatten(init_state)
        self.init_state_int = self.make_int(init_state)
        self.goal_int = self.make_int(self.goal_state)
        self.width = len(init_state)
        self.zero = 0 #location of 0, index 0 at top left

    def solve(self):
        #TODO
        # implement your search algorithm here
        st = time()
        if not self.solvable():
            return ["UNSOLVABLE"]
        direction = ('UP', 'DOWN', 'LEFT', 'RIGHT')
        vis = {} #bool array
        q = deque() #queue for BFS
        state_str = ''.join(str(e) for e in self.init_state_flat)
        state = State(self.actions, self.init_state_int, self.width, self.zero)
        q.append(state)
        vis[state.state_int] = True

        #BFS
        while q:
            curr_puzzle = q.popleft()
            for d in direction:
                next_state = curr_puzzle.next_state(d)
                if not next_state or next_state.state_int in vis: 
                    continue
                if next_state.state_int == self.make_int(self.goal_state):
                    print 'fn took %.2f seconds' % (time() - st) #to check time
                    return next_state.actions
                q.append(next_state)
                vis[next_state.state_int] = True    
    
    # you may add more functions if you think is useful    
    def flatten(self, state):
        return [num for row in state for num in row]

    # Used for representation of board as k digit num
    def make_int(self, state):
        return int(''.join(str(e) for e in self.flatten(state)))
    
    # To determine solvability
    def solvable(self):
        width = self.width
        lst = self.init_state_flat
        size = self.width * self.width
        # Use conditions of inversions
        # https://www.cs.bham.ac.uk/~mdr/teaching/modules04/java2/TilesSolvability.html
        inv, row, zrow = 0, 0, 0
        for i in range(size):
            if (i and i % width == 0):
                row += 1
            # Store zero row
            if (lst[i] == 0):
                zrow = row
                self.zero = row * width + i % width
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

class State(object):
    def __init__(self, actions, state_int, width, zero):
        self.actions = actions
        
        self.state_int = state_int        
        self.width = width
        self.k = self.width * self.width
        self.zero = zero #location of 0, index 0 at top left
        self.set_state_str()

    def set_state_str(self):
        state_str = str(self.state_int)
        if len(state_str) < self.k:
            self.state_str = '0' + state_str
        else:
            self.state_str = state_str

    def get_next_zero(self, direction):
        d = {'DOWN' : -self.width, 'UP' : self.width, 'LEFT' : 1, 'RIGHT' : -1}
        
        #check for RIGHT LEFT out of bounds
        if direction == 'LEFT' and (self.zero % self.width) + 1 == self.width or \
           direction == 'RIGHT' and self.zero % self.width == 0:
            return
        
        new_zero = self.zero + d[direction]
        

        # check for UP DOWN out of bounds
        if new_zero < 0 or new_zero >= self.k:
            return
        
        return new_zero

    # Returns a puzzle state given a direction
    def next_state(self, direction):
        next_zero = self.get_next_zero(direction)
        if next_zero is None: return # return if out of bounds
        
        # Set init variables for new puzzle state
        new_actions = list(self.actions) # This step is still too slow
        new_actions.append(direction)
        # Get next state as an int
        new_state = self.next_state_int(next_zero)
        

        # Initialize new  state
        return State(new_actions, new_state, self.width, next_zero)

    # Returns next state_int given an index
    def next_state_int(self, idx):
        num = int(self.state_str[idx])
        new_int = self.state_int
        new_int -= num * 10 ** (self.k - 1 - idx)
        new_int += num * 10 ** (self.k - 1 - self.zero)
        return new_int
        

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







