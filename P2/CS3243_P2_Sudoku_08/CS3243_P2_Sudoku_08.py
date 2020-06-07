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
        self.all_domains = {}
        self.all_degree = None
        self.constraints = None
        self.memo = {}
        
        #self.pq = list()
   
    
    def solve(self):
        # TODO: Write your code here
        self.get_constraints()
        self.getRV()
        #print(self.constraints[1][1])
        #print(self.all_domains[(1,1)])
        
        #print(self.constraints[7][6])

        if self.complete():
            return self.ans

        return self.backtrack()

    
    def get_constraints(self):
        '''Get a list of all (20) needed constraints for each square'''
        self.constraints = [[list() for _ in range(self.size)] \
                            for _ in range(self.size)]
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
            
                
    
    # copy.deepcopy is slow
    # 2d copy
    def deepcopy(self, lsts):
        return [list(lst) for lst in lsts]

    # 3d copy
    def deepercopy(self, lsts):
        return [self.deepcopy(lst) for lst in lsts]

    def prints(self):
        for row in self.ans:
            print(row)
        print()
    
    def backtrack(self):
        if self.complete():
            return self.ans
        
        #self.getRV()


        #RV, deg, row, col = heappop(self.pq)
        
        row, col = self.getVar()
        if row is None:
            return False

        ord_domain = self.leastCV(row, col)
        #print(self.all_domains)
        #self.prints()
        #n_puzzle = Sudoku(self.ans)
        #n_puzzle.constraints = self.constraints
        #n_puzzle.all_domains = self.all_domains

        domain = self.all_domains[(row,col)]
        #print(row, col, domain)
        del self.all_domains[(row,col)]

        while ord_domain:
            cv, num = heappop(ord_domain)
            
            changed_doms = self.update_domains(num, row, col)

            if self.inference(row, col, num):

                res = self.backtrack()
                if res:
                    return res
            self.ans[row][col] = 0
            self.revert_domains(changed_doms, num)
        #add back the domain if unsuccessful
        self.all_domains[(row,col)] = domain

    def getVar(self):
        minRV = min(x[0] for x in self.all_domains.values())
        if minRV == 0:
            return None, None
        all_minRV = list(filter(lambda x: x[1][0] == minRV, self.all_domains.items() ))
        all_minRV = [x[0] for x in all_minRV]
        
        curVar = all_minRV[0]
        minDeg = self.degree(*curVar)
        if len(all_minRV) > 1:
            
            for i, j in all_minRV:
                curDeg = self.degree(i,j)
                if curDeg < minDeg:
                    minDeg = curDeg
                    curVar = (i,j)

        return curVar
    
    def update_domains(self, num, row, col):
        self.ans[row][col] = num
        num -= 1
        changed = []
        for i, j in self.constraints[row][col]:
            if self.ans[i][j]:
                continue
            if self.all_domains[(i,j)][1][num]:
                self.all_domains[(i,j)][1][num] = False
                self.all_domains[(i,j)][0] -= 1
                changed.append((i,j))
        return changed

    def revert_domains(self, changed, num):

        num -= 1
        for i, j in changed:
            #if self.ans[i][j]:
            #    continue
            self.all_domains[(i,j)][1][num] = True
            self.all_domains[(i,j)][0] += 1
    
    def complete(self):
        '''Check for complete puzzle'''
        for i in range(self.size):
            for j in range(self.size):
                if self.ans[i][j] == 0:
                    return False
        return True
    
    def getRV(self):
        '''Get Remaining Values as priority queue'''
        #self.all_domains =  [[list() for _ in range(self.size)] \
        #                    for _ in range(self.size)]
        #self.all_domains = {}
        for i in range(self.size):
            for j in range(self.size):
                # skip if already filled
                if self.ans[i][j]: continue
                
                domain = self.getDomain(i,j)
                rv = domain.count(True)
                #self.all_domains[i][j] = domain
                self.all_domains[(i,j)] = [rv, domain]
                
                #heappush(self.pq, (domain.count(True), self.degree(i,j), i, j))

    def getDomain(self, row, col):
        '''Get Domain for a single cell'''
        # bool array, 0-8 corresponds to numbers 1-9
        cell = [True] * self.size

        # Check rows and columns
        for i in range(self.size):
            num_r = self.ans[row][i]
            num_c = self.ans[i][col]
            if num_r:
                cell[num_r - 1] = False
            if num_c:
                cell[num_c - 1] = False

        # Check boxes
        box_r, box_c = self.getBox(row, col)
        for i in range(3):
            for j in range(3):
                num = self.ans[box_r + i][box_c + j]
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
            if self.ans[row][i] == 0 and i != col and self.all_domains[(row,i)][1][num]:
                count += 1
            if self.ans[i][col] == 0 and i != row and self.all_domains[(i,col)][1][num]:
                count += 1

        box_r, box_c = self.getBox(row, col)
        for i in range(3):
            for j in range(3):
                c_r, c_c = box_r + i, box_c + j
                # skip if already accounted for in row/col check above
                if c_r == row or c_c == col: continue
                if self.ans[c_r][c_c] == 0 and self.all_domains[(c_r,c_c)][1][num]:
                    count += 1
        return count
    
    def leastCV(self, row, col):
        lst = list()
        for i in range(self.size):
            if self.all_domains[(row,col)][1][i]:
                heappush(lst, (self.cv(row,col,i+1), i+1))
        return lst

    def inference(self, row, col, num):
        #self.ans[row][col] = num
        #if self.complete():
        #    return True
        num -= 1
        #changed = []
        
        for i, j in self.constraints[row][col]:

            # skip if already assigned
            
            if self.ans[i][j]:
                continue

            #remain = self.all_domains[(i,j)][0]
            if self.all_domains[(i,j)][1][num]:
                self.all_domains[(i,j)][1][num] = False
                self.all_domains[(i,j)][0] -= 1
                #remain -= 1
            
            else: #already constrained before
                continue
            
            #remaining = self.all_domains[(i,j)][1]
            remain = self.all_domains[(i,j)][0]
            valid = True
            if remain == 0:
                #self.all_domains[(i,j)][1][num] = True
                #self.all_domains[(i,j)][0] += 1
                valid = False
                #return False
            if remain == 1:
            #    #n_puzzle = Sudoku(self.ans)
            #    #n_puzzle.constraints = self.constraints
            #    #n_puzzle.all_domains = self.deepercopy(self.all_domains)
                domain = self.copy_domain(i,j)
                del self.all_domains[(i,j)]
                n_num = remaining.index(True) + 1
                self.ans[i][j] = n_num
                valid = self.inference(i, j, n_num)
                self.all_domains[(i,j)] = domain
                self.ans[i][j] = 0

                #if not self.inference(i,j, n_num):
                #    return False
            
            self.all_domains[(i,j)][1][num] = True
            self.all_domains[(i,j)][0] += 1
            if not valid:
                return False

        return True

    def copy_domain(self, i, j):
        domain = self.all_domains[(i,j)]
        return [domain[0],list(domain[1])]
                
        

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
