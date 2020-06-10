# CS3243 Introduction to Artificial Intelligence
# Project 2, Part 1: Sudoku

import sys
import copy
from heapq import heappop, heappush
from time import time

# Running script: given code can be run with the command:
# python file.py, ./path/to/init_state.txt ./output/output.txt

class Sudoku(object):
    def __init__(self, puzzle):
        # you may add more attributes if you need
        self.puzzle = puzzle # self.puzzle is a list of lists
        self.ans = self.deepcopy(puzzle) # self.ans is a list of lists
        self.size = len(self.puzzle)
        self.all_domains = {}
        self.all_degrees = None
        self.constraints = None
        #self.st = time()
   
    
    def solve(self):
        # TODO: Write your code here

        # Sudoku Variables represented by (i,j) 
        # corresponding to row and column (0-based)
        # Sudoku Values are all numbers each variable can take - 0-9
        # Sudoku Constraints are that each row, column, box consisting
        # of 9 Variables can only have 1 occurence of each value
        
        # Get constraints, and remaining valid values for each variable
        self.get_constraints()
        self.getRV()
        self.get_degrees()

        return self.backtrack()

    # you may add more classes/functions if you think is useful
    # However, ensure all the classes/functions are in this file ONLY
    # Note that our evaluation scripts only call the solve method.
    # Any other methods that you write should be used within the solve() method.

    def complete(self):
        '''Check for complete puzzle, assumes valid starting board'''
        return len(self.all_domains) == 0
    
    def get_constraints(self):
        '''Get a 2d tuple array of all (20) constraints for each variable
        Constraints are also variables'''
        self.constraints = tuple(tuple(list() for _ in range(self.size)) \
                            for _ in range(self.size))
        for i in range(self.size):
            for j in range(self.size):
                for k in range(self.size):
                    if i != k:
                        self.constraints[i][j].append((k,j))
                    if j != k:
                        self.constraints[i][j].append((i,k))
                
                box_r, box_c = self.getBox(i, j)
                for r in range(3):
                    for c in range(3):
                        c_r, c_c = box_r + r, box_c + c
                        if c_r == i or c_c == j: continue
                        self.constraints[i][j].append((c_r,c_c))
    
    def getRV(self):
        '''Get Remaining Values (RV) of each variable in a dictionary
        RV is the values a variable can take - 0-9 if no constraints'''
        for i in range(self.size):
            for j in range(self.size):
                # skip if already filled
                if self.ans[i][j]: continue
                
                domain = self.getDomain(i,j)
                rv = domain.count(True)
                self.all_domains[(i,j)] = [rv, domain]
    
    def get_degrees(self):
        '''Get degree of each variable in a list of lists'''
        self.all_degrees = [[0 for _ in range(self.size)] \
                            for _ in range(self.size)]
        for i in range(self.size):
            for j in range(self.size):
                # skip if already filled
                if self.ans[i][j]: continue
                self.all_degrees[i][j] = self.degree(i,j)
               
    def backtrack(self):
        '''Backtrack algorithm from AIMA'''
        if self.complete():
            return self.ans
        
        # Get next variable using MRV heuristic
        var = self.getVar()
        if var is None:
            return
        row, col = var

        changed_degs = self.update_degrees(row, col)

        # Get order of domain using LCV heuristic
        ord_domain = self.leastCV(row, col)
        # Get the current domain dictionary, delete the domain of the current variable
        domain = self.all_domains[(row,col)]
        del self.all_domains[(row,col)]

        # for num in ordered domain
        while ord_domain:
            cv, num = heappop(ord_domain)
            
            # Update domains if num is assigned to variable
            changed_doms = self.update_domains(num, row, col)

            # Check inferences
            if self.inference(row, col, num):
                # Recursive backtrack
                res = self.backtrack()
                # If valid, assigned puzzle will be returned
                if res:
                    return res

            # Revert domains if unsuccessful
            self.ans[row][col] = 0
            self.revert_domains(changed_doms, num)

        # Add back the domain for variable if unsuccessful
        self.all_domains[(row,col)] = domain
        self.revert_degrees(changed_degs)

    def getVar(self):
        '''Get variable with minimum remaining values (MRV)'''   
        
        # Obtain a list of all var with RV == minRV
        domain_items = self.all_domains.items()
        all_min_var = [domain_items[0][0]]
        minRV = domain_items[0][1][0]
        for var, rv_domain in self.all_domains.items():
            curRV = rv_domain[0]
            if curRV < minRV:
                minRV = curRV
                all_min_var = [var]
            elif curRV == minRV:
                all_min_var.append(var)
  
        # Obtain variable with minimum degree
        cur_var = all_min_var[0]
        #min_deg = self.degree(*cur_var)
        min_deg = self.all_degrees[cur_var[0]][cur_var[1]]
        if len(all_min_var) > 1:
            for i, j in all_min_var:
                cur_deg = self.all_degrees[i][j]
                if cur_deg < min_deg:
                    min_deg = cur_deg
                    cur_var = (i,j)

        return cur_var

    def update_degrees(self, row, col):
        '''Updates all degree values with an assignment on variable row,col'''
        changes = []
        for i, j in self.constraints[row][col]:
            if self.ans[i][j]: continue
            self.all_degrees[i][j] -= 1
            changes.append((i,j))
        return changes

    def revert_degrees(self, changes):
        '''Reverts degree value changes made in update_degrees'''
        for i,j in changes:
            self.all_degrees[i][j] += 1

    def degree(self, row, col):
        '''Get the degree count of a variable'''
        count = 0

        for i, j in self.constraints[row][col]:
            if self.ans[i][j] == 0:
                count += 1
        return count
    
    def update_domains(self, num, row, col):
        '''Update all domains for an assignment num to variable row,col
        Returns the changed variable domains'''
        # Assign num
        self.ans[row][col] = num
        num -= 1 # 0-based indexing
        changed = []
        for i, j in self.constraints[row][col]:
            if self.ans[i][j]:
                continue
            # If not previously blocked, update and add to change list
            if self.all_domains[(i,j)][1][num]:
                self.all_domains[(i,j)][1][num] = False
                self.all_domains[(i,j)][0] -= 1
                changed.append((i,j))
        return changed

    def revert_domains(self, changed, num):
        '''Revert domains'''
        num -= 1 # 0-based indexing
        for i, j in changed:
            self.all_domains[(i,j)][1][num] = True
            self.all_domains[(i,j)][0] += 1

    def getDomain(self, row, col):
        '''Get Domain (RV) for a single cell'''
        # bool array, 0-8 corresponds to numbers 1-9
        cell = [True] * self.size

        for i, j in self.constraints[row][col]:
            num = self.ans[i][j]
            if num:
                cell[num - 1] = False

        return cell

    def getBox(self, row, col):
        ''' Returns top left row, col variable for a box'''
        return row - row % 3, col - col % 3

    def cv(self, row, col, num):
        '''Constraining value (CV) for a specific num at a row, col'''
        count = 0
        num -= 1 # 0-based

        for i, j in self.constraints[row][col]:
            if self.ans[i][j] == 0 and self.all_domains[(i,j)][1][num]:
                count += 1

        return count
    
    def leastCV(self, row, col):
        '''Returns a list of num ordered by CV for a specific variable'''
        lst = list()
        for i in range(self.size):
            if self.all_domains[(row,col)][1][i]:
                heappush(lst, (self.cv(row,col,i+1), i+1))
        return lst

    def inference(self, row, col, num):
        '''Returns whether an assignment may be valid'''
        num -= 1
        
        for i, j in self.constraints[row][col]:
            # skip if already assigned
            if self.ans[i][j]:
                continue

            if self.all_domains[(i,j)][1][num]:
                remain = self.all_domains[(i,j)][0] - 1
            else: #already constrained before
                continue

            # If no remaining values left, invalid assignment
            if remain == 0:
                return False

        return True
                
    # copy.deepcopy is slow
    # 2d copy
    def deepcopy(self, lsts):
        return [list(lst) for lst in lsts]

    # for debugging
    def prints(self):
        for row in self.ans:
            print(row)
        print()

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
