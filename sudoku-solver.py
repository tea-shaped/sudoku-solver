############################################################
# CIS 521: Homework 4
############################################################

student_name = "Ann-Katrin Reuel"

############################################################
# Imports
############################################################

from copy import deepcopy
import math
import copy


############################################################
#  Sudoku
############################################################

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




############################################################
# Section 2: Dominoes Games
############################################################

def create_dominoes_game(rows, cols):
    board = []
    for y in range(rows):
        temp = []
        for x in range(cols):
            temp.append(False)
        board.append(temp)
    return DominoesGame(board)


class DominoesGame(object):

    # Required
    def __init__(self, board):
        self.board = board
        self.rows = len(board)
        self.cols = len(board[0])

    def get_board(self):
        return self.board

    def reset(self):
        for r in range(self.rows):
            for c in range(self.cols):
                self.board[r][c] = False

    def is_legal_move(self, row, col, vertical):
        result = False
        if 0 <= row < self.rows and 0 <= col < self.cols:
            if not vertical:
                if col + 1 < self.cols and not self.board[row][col] and not \
                        self.board[row][col + 1]:
                    result = True
            if vertical:
                if row + 1 < self.rows and not self.board[row][col] and not \
                        self.board[row + 1][col]:
                    result = True

        return result

    def legal_moves(self, vertical):
        for r in range(self.rows):
            for c in range(self.cols):
                if self.is_legal_move(r, c, vertical):
                    yield r, c

    def perform_move(self, row, col, vertical):
        if self.is_legal_move(row, col, vertical):
            if not vertical:
                self.board[row][col + 1] = True
                self.board[row][col] = True
            if vertical:
                self.board[row + 1][col] = True
                self.board[row][col] = True

    def game_over(self, vertical):
        if not list(self.legal_moves(vertical)):
            return True
        return False

    def copy(self):
        board = []
        for r in self.board:
            board.append(r[:])
        copy = DominoesGame(board)
        return copy

    def successors(self, vertical):
        for m in self.legal_moves(vertical):
            x, y = m
            game = self.copy()
            game.perform_move(x, y, vertical)
            yield (x, y), game

    def get_random_move(self, vertical):
        pass

    # Required
    def get_best_move(self, vertical, limit):
        is_max = True
        return self.alpha_beta(is_max, None, vertical, limit, -float('inf'),
                               float('inf'))

    def alpha_beta(self, is_max, m, vertical, limit, alpha, beta):
        i = 0
        move = m
        if is_max:
            val = float('-inf')
            if self.game_over(vertical) or limit == 0:
                temp = len(list(self.successors(vertical))) - len(
                    list(self.successors(not vertical)))
                return move, temp, 1

            for x, y in list(self.successors(vertical)):
                _, temp, cnt = y.alpha_beta(not is_max, x, not vertical,
                                            limit - 1, alpha, beta)
                i = i + cnt
                if temp > val:
                    val = temp
                    move = x
                if val >= beta:
                    return move, val, i
                if val > alpha:
                    alpha = val

        if not is_max:
            val = float('inf')
            if self.game_over(vertical) or limit == 0:
                temp = len(list(self.successors(not vertical))) - len(
                    list(self.successors(vertical)))
                return move, temp, 1

            for x, y in list(self.successors(vertical)):
                _, temp, cnt = y.alpha_beta(not is_max, x, not vertical,
                                            limit - 1, alpha, beta)
                i = i + cnt
                if temp < val:
                    val = temp
                    move = x
                if val <= alpha:
                    return move, val, i
                if val < beta:
                    beta = val

        return move, val, i


############################################################
# Section 3: Feedback
############################################################

# Just an approximation is fine.
feedback_question_1 = 20

feedback_question_2 = """
I found the implementation of solutions that don't overtime difficult.
"""

feedback_question_3 = """
I loved that we had GUIs available to test our solution.
"""
