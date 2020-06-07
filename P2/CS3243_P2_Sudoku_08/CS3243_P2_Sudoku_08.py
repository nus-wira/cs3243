# CS3243 Introduction to Artificial Intelligence
# Project 2, Part 1: Sudoku

import sys
import copy
from heapq import heappop, heappush

# Running script: given code can be run with the command:
# python file.py, ./path/to/init_state.txt ./output/output.txt

class Sudoku(object):
    def __init__(self, puzzle):
        # you may add more attributes if you need
        self.puzzle = puzzle # self.puzzle is a list of lists
        self.ans = self.deepcopy(puzzle) # self.ans is a list of lists
        self.size = len(self.puzzle)
        self.all_domains = [[list() for _ in range(self.size)] \
                            for _ in range(self.size)]
        self.pq = list()
        self.constraints = [[list() for _ in range(self.size)] \
                            for _ in range(self.size)]
        
        
   
    
    def solve(self):
        # TODO: Write your code here
        self.get_constraints()
        
        if self.complete():
            return self.ans

        
        return self.backtrack(self)     
            
        # self.ans is a list of lists
        return None

    
    def get_constraints(self):
        '''Get a list of all (20) needed constraints for each square'''
        for i in range(self.size):
            for j in range(self.size):
                for k in range(self.size):
                    if i != k:
                        self.constraints[i][j].append((i,k))
                    if j != k:
                        self.constraints[i][j].append((k,j))
                
                box_r, box_c = self.getBox(i, j)
                for r in range(3):
                    for c in range(3):
                        c_r, c_c = box_r + r, box_c + c
                        if c_r == r or c_c == c: continue
                        self.constraints[i][j].append((c_r,c_c))
            
                
    
    # copy.deepcopy is slow
    def deepcopy(self, state):
        return list(map(list, state))


    def prints(self):
        for row in self.ans:
            print(row)
        print()
    
    def backtrack(self):
        if self.complete():
            return self.ans
        
        self.getRV()
        RV, deg, row, col = heappop(self.pq)
        self.prints()
        if RV == 0:
            return
        
        print( self.leastCV(row, col))
        
        for cv, num in puzzle.leastCV(row, col, puzzle):
##            print(row, col)
##            print(puzzle.ans[row][col])
##            print (cv, num)
##            print(puzzle.ans)
            n_puzzle = Sudoku(puzzle.ans)
            n_puzzle.constraints = puzzle.constraints
            n_puzzle.all_domains = copy.deepcopy(puzzle.all_domains)
            
            
            if n_puzzle.inference(row, col, num):
                print('test')
                res = n_puzzle.backtrack(n_puzzle)
                if res:
                    return res
        
    
    def complete(self):
        '''Check for complete puzzle'''
        for i in range(self.size):
            for j in range(self.size):
                if self.ans[i][j] == 0:
                    return False
        return True
    
    def getRV(self):
        '''Get Remaining Values as priority queue'''
        for i in range(self.size):
            for j in range(self.size):
                # skip if already filled
                if self.ans[i][j]: continue
                
                domain = self.getDomain(i,j)
                self.all_domains[i][j] = domain
                
                heappush(self.pq, (domain.count(True), self.degree(i,j), i, j))

    def getDomain(self, row, col):
        '''Get Domain for a single cell'''
        # bool array, 0-8 corresponds to numbers 1-9
        cell = [True] * self.size

        # Check rows and columns
        for i in range(self.size):
            num_r = self.puzzle[row][i]
            num_c = self.puzzle[i][col]
            if num_r:
                cell[num_r - 1] = False
            if num_c:
                cell[num_c - 1] = False

        # Check boxes
        box_r, box_c = self.getBox(row, col)
        for i in range(3):
            for j in range(3):
                num = self.puzzle[box_r + i][box_c + j]
                if num:
                    cell[num - 1] = False

        return cell

    def getBox(self, row, col):
        return row - row % 3, col - col % 3
    
    def degree(self, row, col):
        count = 0
        for i in range(self.size):
            if self.ans[row][i] == 0:
                count += 1
            if self.ans[i][col] == 0:
                count += 1

        box_r, box_c = self.getBox(row, col)
        for i in range(3):
            for j in range(3):
                c_r, c_c = box_r + i, box_c + j
                # skip if already accounted for in row/col check above
                if c_r == row or c_c == col: continue
                if self.ans[c_r][c_c] == 0:
                    count += 1
        return count

    def cv(self, row, col, num):
        '''Constraining value for a specific num at a row, col'''
        count = 0
        num -= 1 # 0-based
        for i in range(self.size):
##            print(self.all_domains[row])
##            print(self.ans[row])
            if puzzle.ans[row][i] == 0 and i != col and puzzle.all_domains[row][i][num]:
                count += 1
            if puzzle.ans[i][col] == 0 and i != row and puzzle.all_domains[i][col][num]:
                count += 1

        box_r, box_c = self.getBox(row, col)
        for i in range(3):
            for j in range(3):
                c_r, c_c = box_r + i, box_c + j
                # skip if already accounted for in row/col check above
                if c_r == row or c_c == col: continue
                if puzzle.ans[c_r][c_c] == 0 and puzzle.all_domains[c_r][c_c][num]:
                    count += 1
        return count
    
    def leastCV(self, row, col):
        lst = list()
        for i in range(self.size):
            if puzzle.all_domains[row][col][i]:
                heappush(lst, (self.cv(row,col,i+1), i+1))
        return lst

    def inference(self, row, col, num):
        self.ans[row][col] = num
        num -= 1
##        print(row, col, num)
##        print(self.ans[row][col])
##        print(row, col)
##        print(self.constraints[row][col])
        for i, j in self.constraints[row][col]:

            # skip if already assigned
            
            if self.ans[i][j]:
                continue

            self.all_domains[i][j][num] = False
            remaining = self.all_domains[i][j]
            remain = remaining.count(True)
            if remain == 0:
                return False
            if remain == 1:
                if not self.inference(row, col, remaining.index(True) + 1):
                    return False
        return True
                
        

    # you may add more classes/functions if you think is useful
    # However, ensure all the classes/functions are in this file ONLY
    # Note that our evaluation scripts only call the solve method.
    # Any other methods that you write should be used within the solve() method.

if __name__ == "__main__":
    # STRICTLY do NOT modify the code in the main function here
    if len(sys.argv) != 3:
        print ("\nUsage: python CS3243_P2_Sudoku_XX.py input.txt output.txt\n")
        raise ValueError("Wrong number of arguments!")

    try:
        f = open(sys.argv[1], 'r')
    except IOError:
        print ("\nUsage: python CS3243_P2_Sudoku_XX.py input.txt output.txt\n")
        raise IOError("Input file not found!")

    puzzle = [[0 for i in range(9)] for j in range(9)]
    lines = f.readlines()

    i, j = 0, 0
    for line in lines:
        for number in line:
            if '0' <= number <= '9':
                puzzle[i][j] = int(number)
                j += 1
                if j == 9:
                    i += 1
                    j = 0

    sudoku = Sudoku(puzzle)
    ans = sudoku.solve()

    with open(sys.argv[2], 'a') as f:
        for i in range(9):
            for j in range(9):
                f.write(str(ans[i][j]) + " ")
            f.write("\n")
