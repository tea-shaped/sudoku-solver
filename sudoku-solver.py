from copy import deepcopy
import math
import copy

def sudoku_cells():
    cells = []
    for i in range(0, 9):
        for j in range(0, 9):
            cells.append((i, j))
    return cells


def sudoku_arcs():
    arcs = []
    cells = sudoku_cells()
    for cell_A in cells:
        for cell_B in cells:
            cond_A = cell_A != cell_B
            cond_B = cell_A[0] == cell_B[0]
            cond_C = cell_A[1] == cell_B[1]
            cond_D = cell_A[0] // 3 == cell_B[0] // 3 and cell_A[1] // 3 == \
                     cell_B[1] // 3

            if (cond_B or cond_C) and cond_A:
                arcs.append((cell_A, cell_B))
                continue
            if cond_D and cond_A:
                arcs.append((cell_A, cell_B))
    return arcs


def read_board(path):
    board = {}
    file = open(path, 'r')
    i = 0
    for l in file:
        line = l.rstrip('\r\n')
        j = 0
        for c in line:
            if c == '*':
                board[(i, j)] = {1, 2, 3, 4, 5, 6, 7, 8, 9}
            if c != '*':
                board[(i, j)] = {int(c)}
            j = j + 1
        i = i + 1

    return board


class Sudoku(object):
    CELLS = sudoku_cells()
    ARCS = sudoku_arcs()

    def __init__(self, board):
        print(board)
        self.board = board

    def get_values(self, cell):
        return self.board[cell]

    def remove_inconsistent_values(self, cell1, cell2):
        if len(self.board[cell2]) == 1:
            for x in self.board[cell1]:
                if x in self.board[cell2]:
                    self.board[cell1].remove(x)
                    return True
            return False
        if len(self.board[cell2]) != 1:
            return False

    def infer_ac3(self):
        copy = deepcopy(self.ARCS)
        while copy:
            cells = copy.pop(0)
            if self.remove_inconsistent_values(cells[0], cells[1]):
                for a in self.ARCS:
                    if a[1] == cells[0]:
                        if a[0] != cells[1]:
                            copy.append(a)

    def infer_improved(self):
        copy = deepcopy(self.board)
        self.infer_ac3()
        for c in self.CELLS:
            cell_values = list(self.get_values(c))
            if len(cell_values) > 1:
                for v in cell_values:
                    row, col, squ = 0, 0, 0
                    arcs_row = []
                    for i in range(0, 9):
                        if i != c[1]:
                            arcs_row.append((c[0], i))
                    for a in arcs_row:
                        if v in self.get_values(a):
                            row = row + 1

                    arcs_col = []
                    for i in range(0, 9):
                        if i != c[0]:
                            arcs_col.append((i, c[1]))
                    for a in arcs_col:
                        if v in self.get_values(a):
                            col = col + 1

                    arcs_square = []
                    pos = c[0] // 3, c[1] // 3
                    val_A = pos[0] * 3
                    val_B = pos[1] * 3

                    for r in range(val_A, val_A + 3):
                        for cl in range(val_B, val_B + 3):
                            if r != c[0] or cl != c[1]:
                                arcs_square.append((r, cl))

                    for a in arcs_square:
                        if v in self.get_values(a):
                            squ = squ + 1

                    if not (row > 0 and col > 0 and squ > 0):
                        self.board[c] = {v}
                        break

        self.infer_ac3()
        if copy != self.board:
            self.infer_improved()


    def next_vals(self, next):
        copy = deepcopy(self.board)
        next_vals = list(self.get_values(next))
        for v in next_vals:
            copy[next] = {v}
            next_board = deepcopy(copy)
            yield Sudoku(next_board)

    def infer_with_guessing(self):
        q = [self]
        while q:
            f = q.pop()
            f.infer_improved()

            solved = True
            cells = f.CELLS
            for c in cells:
                if len(f.get_values(c)) != 1:
                    solved = False
                    break
                if len(f.get_values(c)) == 1:
                    continue

            if solved:
                self.board = f.board
                return f

            solvable = True
            cells = f.CELLS
            for c in cells:
                if len(f.get_values(c)) == 0:
                    solvable = False
                    break
                if len(f.get_values(c)) != 0:
                    continue

            if solvable:
                pos_vals = float('inf')
                next_cell = ()
                cells = f.CELLS
                for c in cells:
                    if pos_vals > len(f.get_values(c)) > 1:
                        next_cell = c
                        pos_vals = len(f.get_values(c))

                for v in f.next_vals(next_cell):
                    q.append(v)

            if not solvable:
                continue

        return self
