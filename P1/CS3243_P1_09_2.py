# CS3243 Introduction to Artificial Intelligence
# Project 1: k-Puzzle

import os
import sys
from heapq import heappop, heappush
from collections import deque

# Running script on your own - given code can be run with the command:
# python file.py, ./path/to/init_state.txt ./output/output.txt

class Puzzle(object):
    def __init__(self, init_state, goal_state):
        # you may add more attributes if you think is useful
        self.init_state = init_state
        self.goal_state = goal_state
        self.pq = list()
        self.visited = set()
        self.n = len(self.init_state)
        self.n_square = self.n * self.n
        self.goal_state_index_list = self.index(goal_state)
        
    def solve(self):
        if not self.check_solvable(self.init_state):
            return ['UNSOLVABLE']

        zero_index = self.find_zero_index(self.init_state)
        heuristic = self.heuristic(self.init_state)
        cost = 0
        heappush(self.pq, (cost + heuristic, cost, self.init_state, zero_index, list()))
        
        direction = {'UP':(1,0), 'DOWN':(-1,0), 'LEFT':(0,1), 'RIGHT':(0,-1)}

        while self.pq:
            total, current_cost, current_node, current_zero_index, action_list = heappop(self.pq)
            if current_node == self.goal_state:
                return action_list
            row, col = current_zero_index
            current_node_tuple = self.list_to_tuple(current_node)
            if current_node_tuple not in self.visited:

                self.visited.add(current_node_tuple)

                for i in direction:
                    move = self.move(current_node, row, col, i, direction)
                    if move and self.list_to_tuple(move) not in self.visited:
                        
                        new_action_list = list(action_list)
                        new_action_list.append(i)
                        if current_node == self.goal_state:
                            return action_list
                        r, c = direction[i]
                        new_heuristic = self.heuristic(move)
                        new_cost = current_cost + 1
                        heappush(self.pq, (new_heuristic + new_cost, new_cost, move, (row+r,col+c), new_action_list))
                
        return ['UNSOLVABLE']

    # you may add more functions if you think is useful

    def heuristic(self, state):
        current_state_index_list = self.index(state)
        manhattan_distance = 0
        for i in range(self.n_square):
            x_curr, y_curr = current_state_index_list[i]
            x_goal, y_goal = self.goal_state_index_list[i]
            manhattan_distance += abs(x_goal - x_curr) + abs(y_goal - y_curr)
        return manhattan_distance
    
    def index(self, state):
        index_list = [(0,0)] * (self.n_square)
        for i in range(self.n):
            for j in range(self.n):
                index_list[state[i][j]] = (i,j)
        return index_list

    
    def flatten(self, state):
        new_state = list()
        for row in state:
            for col in row:
                if col:
                    new_state.append(col)
        return new_state

    def check_solvable(self, state):
        row,col = self.find_zero_index(state)
        flat_state = self.flatten(state)
        inversion = 0
        for i in range(len(flat_state)):
            for j in range(len(flat_state) - i):
                if flat_state[i] > flat_state[i+j]:
                    inversion += 1
        if self.n % 2 == 0:
            return (inversion % 2 != 0 and row % 2 == 0) or (inversion % 2 == 0 and row % 2 != 0)
        else:
            return inversion % 2 == 0
    
    def deepcopy(self, state):
        return list(map(list, state))
    
    def list_to_tuple(self, state):
        return tuple(map(tuple,state))
    
    def find_zero_index(self, state):
        for row in range(self.n):
            for col in range(self.n):
                if state[row][col] == 0:
                    return (row, col)

    def move(self, state, row, col, i, direction):
        if (col == 0 and i == 'RIGHT') or (col == self.n - 1 and i == 'LEFT') or (row == 0 and i == 'DOWN') or (row == self.n - 1 and i == 'UP'):
            return False
        new_state = self.deepcopy(state)
        r, c = direction[i]
        new_state[row + r][col + c], new_state[row][col] = new_state[row][col], new_state[row + r][col + c]
        return new_state

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
