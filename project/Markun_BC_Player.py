"""
CSE415 Project Option_1
by Bingkun Li (bingkunl) and Yuchen Wang (mark96)
3/11/2018
"""

import itertools
import random
import time


BLACK = 0
WHITE = 1

INIT_TO_CODE = {'p': 2, 'P': 3, 'c': 4, 'C': 5, 'l': 6, 'L': 7, 'i': 8, 'I': 9,
                'w': 10, 'W': 11, 'k': 12, 'K': 13, 'f': 14, 'F': 15, '-': 0}

CODE_TO_INIT = {0: '-', 2: 'p', 3: 'P', 4: 'c', 5: 'C', 6: 'l', 7: 'L', 8: 'i', 9: 'I',
                10: 'w', 11: 'W', 12: 'k', 13: 'K', 14: 'f', 15: 'F'}


def who(piece): return piece % 2


def parse(bs):  # bs is board string
    """Translate a board string into the list of lists representation."""
    b = [[0, 0, 0, 0, 0, 0, 0, 0] for r in range(8)]
    rs9 = bs.split("\n")
    rs8 = rs9[1:]  # eliminate the empty first item.
    for iy in range(8):
        rss = rs8[iy].split(' ')
        for jx in range(8):
            b[iy][jx] = INIT_TO_CODE[rss[jx]]
    return b


def introduce():
    introduction = """My name is Markun, who is design by Bingkun Li(bingkunl) and Yuchen Wang(mark96)"""
    return introduction


def prepare(player2Nickname):
    pass


def nickname():
    return "Markun"


INITIAL = parse('''
c l i w k i l f
p p p p p p p p
- - - - - - - -
- - - - - - - -
- - - - - - - -
- - - - - - - -
P P P P P P P P
F L I W K I L C
''')


class BC_state:
    def __init__(self, old_board=INITIAL, whose_move=WHITE):
        new_board = [r[:] for r in old_board]
        self.board = new_board
        self.whose_move = whose_move

    def __repr__(self):
        s = ''
        for r in range(8):
            for c in range(8):
                s += CODE_TO_INIT[self.board[r][c]] + " "
            s += "\n"
        if self.whose_move == WHITE:
            s += "WHITE's move"
        else:
            s += "BLACK's move"
        s += "\n"
        return s

    def __eq__(self, other):
        if not (type(other) == type(self)):
            return False
        if self.whose_move != other.whose_move:
            return False
        try:
            b1 = self.board
            b2 = other.board
            for i in range(8):
                for j in range(8):
                    if b1[i][j] != b2[i][j]:
                        return False
            return True
        except Exception as e:
            return False


def test_starting_board():
    init_state = BC_state(INITIAL, WHITE)
    print(init_state)


TimeOut = False


def opponent(player):
    if player == WHITE:
        return BLACK
    else:
        return WHITE


def makeMove(currentState, currentRemark, timeLimit=10):
    global TimeOut
    TimeOut = False
    initTime = time.clock()
    newState = decideBest(currentState, currentState, "", 1, initTime, timeLimit, 1)
    for ply in range(2, 15):
        nextState = decideBest(currentState, currentState, "", 1, initTime, timeLimit, ply)
        if nextState[-1] == False:
            newState = nextState
        else:
            break
    return [[newState[3], BC_state(newState[2].board, newState[2].whose_move)], random.choice(PUNTS)]


PUNTS = ["Nico Nico Ni!",
         "The match is so boring.",
         "Hey! Someone's behind you.",
         "You really aren't a strong rival.",
         "If I were you, I would quit the game.",
         "Hmm, good job But I will win the game",
         "Do you really know the rule of this game?",
         "Come on. Give it up. It's a waste of time",
         "I think it's the time to make my last move.",
         "Welcome to adult world, I will teach you a lesson!",
         "I am the marvelous spectacular greatest Mr. Mastermind."]


def decideBest(state, first, desc, level, initTime, timeLimit, plyLeft):
    global TimeOut
    if plyLeft == 0:
        return [staticEval(state), state, first, desc, level, TimeOut]
    if state.whose_move == WHITE:
        provisional = [-100000, state, first, desc, level, TimeOut]
    else:
        provisional = [100000, state, first, desc, level, TimeOut]
    for s in look_for_child(state):
        if level == 1:
            first = BC_state(s[1], opponent(state.whose_move))
            desc = s[0]
        currTime = time.clock()
        if (currTime - initTime) > (timeLimit * 0.75):
            TimeOut = True
            provisional[-1] = TimeOut
            break
        newVal = decideBest(BC_state(s[1], opponent(state.whose_move)), first, desc, level+1,
                            initTime, timeLimit, plyLeft-1)
        if (state.whose_move == WHITE and newVal[0] > provisional[0]) or\
           (state.whose_move == BLACK and newVal[0] < provisional[0]):
            provisional = newVal
        if (state.whose_move == WHITE and newVal[0] == provisional[0]) or\
           (state.whose_move == BLACK and newVal[0] == provisional[0]):
            rint = random.randint(0, 1)
            if rint == 0:
                provisional = newVal
    return provisional


piece_vals = [0, 0, -10, 10, -20, 20, -20, 20, -30, 30, -80, 80, -1000, 1000, -20, 20]


def staticEval(state):
    return sum([sum([piece_vals[j] for j in i]) for i in state.board])


def look_for_child(state):
    board = state.board
    player = state.whose_move
    children = []
    for i in range(8):
        for j in range(8):
            piece = board[i][j]
            if who(piece) == player and piece != 0:
                new_boards = find_child(piece, i, j, board, player)
                children.extend(new_boards)
    return children


def copy_board(board):
    new_board = [[0, 0, 0, 0, 0, 0, 0, 0] for r in range(8)]
    for i in range(8):
        for j in range(8):
            new_board[i][j] = board[i][j]
    return new_board


def move_desc_helper(r1, c1, r2, c2):
    return [(r1, c1 ), (r2 , c2 )]


def find_child(piece, row, col, board, player):
    child_boards = []

    if is_frozen(row, col, board, player):
        return child_boards
    if CODE_TO_INIT[piece].lower() == 'p':
        child_boards.extend(pincer(piece, row, col, board, player))
    if CODE_TO_INIT[piece].lower() == 'k':
        child_boards.extend(king(piece, row, col, board, player))
    if CODE_TO_INIT[piece].lower() == 'w':
        child_boards.extend(withdrawer(piece, row, col, board, player))
    if CODE_TO_INIT[piece].lower() == 'l':
        child_boards.extend(leaper(piece, row, col, board, player))
    if CODE_TO_INIT[piece].lower() == 'c':
        child_boards.extend(coordinator(piece, row, col, board, player))
    if CODE_TO_INIT[piece].lower() == 'f':
        if imitate_frozen(row, col, board, player):
            return child_boards
        child_boards.extend(freezer(piece, row, col, board))
    if CODE_TO_INIT[piece].lower() == 'i':
        child_boards.extend(imitator(piece, row, col, board, player))

    return child_boards


def is_frozen(row, col, board, player):
    neighbors = itertools.product([-1, 0, 1], [-1, 0, 1])
    for neighbor in neighbors:
        temp_r = row + neighbor[0]
        temp_c = col + neighbor[1]
        if 0 <= temp_r < 8 and 0 <= temp_c < 8:
            if who(board[temp_r][temp_c]) != player and CODE_TO_INIT[board[temp_r][temp_c]].lower() == 'f':
                return True
    return False


def imitate_frozen(row, col, board, player):
    neighbors = itertools.product([-1, 0, 1], [-1, 0, 1])
    for neighbor in neighbors:
        temp_r = row + neighbor[0]
        temp_c = col + neighbor[1]
        if 0 <= temp_r < 8 and 0 <= temp_c < 8:
            if who(board[temp_r][temp_c]) != player and CODE_TO_INIT[board[temp_r][temp_c]].lower() == 'i':
                return True
    return False


def pincer(piece, row, col, board, player):
    child_boards = []
    # no.1
    k = 1
    while col + k <= 7:
        if board[row][col + k] == 0:
            new_board = copy_board(board)
            new_board[row][col + k] = piece
            new_board[row][col] = 0
            pincer_helper(row, col + k, new_board, player)
            move_desc = move_desc_helper(row, col, row, col + k)
            child_boards.append([move_desc, new_board])
        else:
            break
        k = k + 1
    # no.2
    k = 1
    while col - k >= 0:
        if board[row][col - k] == 0:
            new_board = copy_board(board)
            new_board[row][col - k] = piece
            new_board[row][col] = 0
            pincer_helper(row, col - k, new_board, player)
            move_desc = move_desc_helper(row, col, row, col - k)
            child_boards.append([move_desc, new_board])
        else:
            break
        k = k + 1
    # no.3
    k = 1
    while row + k <= 7:
        if board[row + k][col] == 0:
            new_board = copy_board(board)
            new_board[row + k][col] = piece
            new_board[row][col] = 0
            pincer_helper(row + k, col, new_board, player)
            move_desc = move_desc_helper(row, col, row + k, col)
            child_boards.append([move_desc, new_board])
        else:
            break
        k = k + 1
    # no.4
    k = 1
    while row - k >= 0:
        if board[row - k][col] == 0:
            new_board = copy_board(board)
            new_board[row - k][col] = piece
            new_board[row][col] = 0
            pincer_helper(row - k, col, new_board, player)
            move_desc = move_desc_helper(row, col, row - k, col)
            child_boards.append([move_desc, new_board])
        else:
            break
        k = k + 1
    # # no.5
    # k = 1
    # while k + row < 8 and k + col < 8:
    #     if board[row + k][col + k] == 0:
    #         new_board = copy_board(board)
    #         new_board[row + k][col + k] = piece
    #         new_board[row][col] = 0
    #         pincer_helper(row + k, col + k, new_board, player)
    #         move_desc = move_desc_helper(row, col, row + k, col + k)
    #         child_boards.append([move_desc, new_board])
    #     else:
    #         break
    #     k = k + 1
    # # no.6
    # k = 1
    # while row - k > -1 and col + k < 8:
    #     if board[row - k][col + k] == 0:
    #         new_board = copy_board(board)
    #         new_board[row - k][col + k] = piece
    #         new_board[row][col] = 0
    #         pincer_helper(row - k, col + k, new_board, player)
    #         move_desc = move_desc_helper(row, col, row - k, col + k)
    #         child_boards.append([move_desc, new_board])
    #     else:
    #         break
    #     k = k + 1
    # # no.7
    # k = 1
    # while k + row < 8 and col - k > -1:
    #     if board[row + k][col - k] == 0:
    #         new_board = copy_board(board)
    #         new_board[row + k][col - k] = piece
    #         new_board[row][col] = 0
    #         pincer_helper(row + k, col - k, new_board, player)
    #         move_desc = move_desc_helper(row, col, row + k, col - k)
    #         child_boards.append([move_desc, new_board])
    #     else:
    #         break
    #     k = k + 1
    # # no.8
    # k = 1
    # while row - k > -1 and col - k > -1:
    #     if board[row - k][col - k] == 0:
    #         new_board = copy_board(board)
    #         new_board[row - k][col - k] = piece
    #         new_board[row][col] = 0
    #         pincer_helper(row - k, col - k, new_board, player)
    #         move_desc = move_desc_helper(row, col, row - k, col - k)
    #         child_boards.append([move_desc, new_board])
    #     else:
    #         break
    #     k = k + 1

    return child_boards


def pincer_helper(row, col, board, player):
    for i in [-2, 0, 2]:
        for j in [-2, 0, 2]:
            if i * j == 0:
                temp_r = row + i
                temp_c = col + j
                if 0 <= temp_r < 8 and 0 <= temp_c < 8:
                    be_captured_r = row + int(i / 2)
                    be_captured_c = col + int(j / 2)
                    if board[temp_r][temp_c] != 0 and board[be_captured_r][be_captured_c] != 0 and \
                        who(board[temp_r][temp_c]) == player and who(board[be_captured_r][be_captured_c]) != player:
                            board[be_captured_r][be_captured_c] = 0
                            return


def withdrawer(piece, row, col, board, current_player):
    new_boards = []
    # no.1
    k = 1
    while col + k < 8:
        if board[row][col + k] == 0:
            new_board = copy_board(board)
            new_board[row][col + k] = piece
            new_board[row][col] = 0
            if col > 0 and who(board[row][col - 1]) != current_player and board[row][col - 1] != 0:
                new_board[row][col - 1] = 0
            move_desc = move_desc_helper(row, col, row, col + k)
            new_boards.append([move_desc, new_board])
        else:
            break
        k = k + 1
    # no.2
    k = 1
    while col - k > -1:
        if board[row][col - k] == 0:
            new_board = copy_board(board)
            new_board[row][col - k] = piece
            new_board[row][col] = 0
            if col < 7 and who(board[row][col + 1]) != current_player and board[row][col + 1] != 0:
                new_board[row][col + 1] = 0
            move_desc = move_desc_helper(row, col, row, col - k)
            new_boards.append([move_desc, new_board])
        else:
            break
        k = k + 1
    # no.3
    k = 1
    while row + k < 8:
        if board[row + k][col] == 0:
            new_board = copy_board(board)
            new_board[row + k][col] = piece
            new_board[row][col] = 0
            if row > 0 and who(board[row - 1][col]) != current_player and board[row - 1][col] != 0:
                new_board[row - 1][col] = 0
            move_desc = move_desc_helper(row, col, row + k, col)
            new_boards.append([move_desc, new_board])
        else:
            break
        k = k + 1
    # no.4
    k = 1
    while row - k > -1:
        if board[row - k][col] == 0:
            new_board = copy_board(board)
            new_board[row - k][col] = piece
            new_board[row][col] = 0
            if row < 7 and who(board[row + 1][col]) != current_player and board[row + 1][col] != 0:
                new_board[row + 1][col] = 0
            move_desc = move_desc_helper(row, col, row - k, col)
            new_boards.append([move_desc, new_board])
        else:
            break
        k = k + 1
    # no.5
    k = 1
    while k + row < 8 and k + col < 8:
        if board[row + k][col + k] == 0:
            new_board = copy_board(board)
            new_board[row + k][col + k] = piece
            new_board[row][col] = 0
            if row > 0 and col > 0 and who(board[row - 1][col - 1]) != current_player and board[row - 1][col - 1] != 0:
                new_board[row - 1][col - 1] = 0
            move_desc = move_desc_helper(row, col, row + k, col + k)
            new_boards.append([move_desc, new_board])
        else:
            break
        k = k + 1
    # no.6
    k = 1
    while row - k > -1 and col + k < 8:
        if board[row - k][col + k] == 0:
            new_board = copy_board(board)
            new_board[row - k][col + k] = piece
            new_board[row][col] = 0
            if row < 7 and col > 0 and who(board[row + 1][col - 1]) != current_player and board[row + 1][col - 1] != 0:
                new_board[row + 1][col - 1] = 0
            move_desc = move_desc_helper(row, col, row - k, col + k)
            new_boards.append([move_desc, new_board])
        else:
            break
        k = k + 1
    # no.7
    k = 1
    while k + row < 8 and col - k > -1:
        if board[row + k][col - k] == 0:
            new_board = copy_board(board)
            new_board[row + k][col - k] = piece
            new_board[row][col] = 0
            if row > 0 and col < 7 and who(board[row - 1][col + 1]) != current_player and board[row - 1][col + 1] != 0:
                new_board[row - 1][col + 1] = 0
            move_desc = move_desc_helper(row, col, row + k, col - k)
            new_boards.append([move_desc, new_board])
        else:
            break
        k = k + 1
    # no.8
    k = 1
    while row - k > -1 and col - k > -1:
        if board[row - k][col - k] == 0:
            new_board = copy_board(board)
            new_board[row - k][col - k] = piece
            new_board[row][col] = 0
            if row < 7 and col < 7 and who(board[row + 1][col + 1]) != current_player and board[row + 1][col + 1] != 0:
                new_board[row + 1][col + 1] = 0
            move_desc = move_desc_helper(row, col, row - k, col - k)
            new_boards.append([move_desc, new_board])
        else:
            break
        k = k + 1

    return new_boards


def leaper(piece, row, col, board, current_player):
    new_boards = []
    # no.1
    k = 1
    while col + k < 8:
        if board[row][col + k] == 0:
            new_board = copy_board(board)
            new_board[row][col + k] = piece
            new_board[row][col] = 0
            move_desc = move_desc_helper(row, col, row, col + k)
            new_boards.append([move_desc, new_board])
        else:
            break
        k = k + 1
    if col + k < 7 and board[row][col + k + 1] == 0:
        if who(board[row][col + k]) != current_player and board[row][col + k] != 0:
            new_board = copy_board(board)
            new_board[row][col + k + 1] = piece
            new_board[row][col + k] = 0
            new_board[row][col] = 0
            move_desc = move_desc_helper(row, col, row, col + k + 1)
            new_boards.append([move_desc, new_board])
    # no.2
    k = 1
    while col - k > -1:
        if board[row][col - k] == 0:
            new_board = copy_board(board)
            new_board[row][col - k] = piece
            new_board[row][col] = 0
            move_desc = move_desc_helper(row, col, row, col - k)
            new_boards.append([move_desc, new_board])
        else:
            break
        k = k + 1
    if col + k > 0 and board[row][col - k - 1] == 0:
        if who(board[row][col - k]) != current_player and board[row][col - k] != 0:
            new_board = copy_board(board)
            new_board[row][col - k - 1] = piece
            new_board[row][col - k] = 0
            new_board[row][col] = 0
            move_desc = move_desc_helper(row, col, row, col - k - 1)
            new_boards.append([move_desc, new_board])
    # no.3
    k = 1
    while row + k < 8:
        if board[row + k][col] == 0:
            new_board = copy_board(board)
            new_board[row + k][col] = piece
            new_board[row][col] = 0
            move_desc = move_desc_helper(row, col, row + k, col)
            new_boards.append([move_desc, new_board])
        else:
            break
        k = k + 1
    if row + k < 7 and board[row + k + 1][col] == 0:
        if who(board[row + k][col]) != current_player and board[row + k][col] != 0:
            new_board = copy_board(board)
            new_board[row + k + 1][col] = piece
            new_board[row + k][col] = 0
            new_board[row][col] = 0
            move_desc = move_desc_helper(row, col, row + k + 1, col)
            new_boards.append([move_desc, new_board])
    # no.4
    k = 1
    while row - k > -1:
        if board[row - k][col] == 0:
            new_board = copy_board(board)
            new_board[row - k][col] = piece
            new_board[row][col] = 0
            move_desc = move_desc_helper(row, col, row - k, col)
            new_boards.append([move_desc, new_board])
        else:
            break
        k = k + 1
    if row - k > 0 and board[row - k - 1][col] == 0:
        if who(board[row - k][col]) != current_player and board[row - k][col] != 0:
            new_board = copy_board(board)
            new_board[row - k - 1][col] = piece
            new_board[row - k][col] = 0
            new_board[row][col] = 0
            move_desc = move_desc_helper(row, col, row - k - 1, col)
            new_boards.append([move_desc, new_board])
    # no.5
    k = 1
    while k + row < 8 and k + col < 8:
        if board[row + k][col + k] == 0:
            new_board = copy_board(board)
            new_board[row + k][col + k] = piece
            new_board[row][col] = 0
            move_desc = move_desc_helper(row, col, row + k, col + k)
            new_boards.append([move_desc, new_board])
        else:
            break
        k = k + 1
    if row + k < 7 and col + k < 7 and board[row + k + 1][col + k + 1] == 0:
        if who(board[row + k][col + k]) != current_player and board[row + k][col + k] != 0:
            new_board = copy_board(board)
            new_board[row + k + 1][col + k + 1] = piece
            new_board[row + k][col + k] = 0
            new_board[row][col] = 0
            move_desc = move_desc_helper(row, col, row + k + 1, col + k + 1)
            new_boards.append([move_desc, new_board])
    # no.6
    k = 1
    while row - k > -1 and col + k < 8:
        if board[row - k][col + k] == 0:
            new_board = copy_board(board)
            new_board[row - k][col + k] = piece
            new_board[row][col] = 0
            move_desc = move_desc_helper(row, col, row - k, col + k)
            new_boards.append([move_desc, new_board])
        else:
            break
        k = k + 1
    if row - k > 0 and col + k < 7 and board[row - k - 1][col + k + 1] == 0:
        if who(board[row - k][col + k]) != current_player and board[row - k][col + k] != 0:
            new_board = copy_board(board)
            new_board[row - k - 1][col + k + 1] = piece
            new_board[row - k][col + k] = 0
            new_board[row][col] = 0
            move_desc = move_desc_helper(row, col, row - k - 1, col + k + 1)
            new_boards.append([move_desc, new_board])
    # no.7
    k = 1
    while k + row < 8 and col - k > -1:
        if board[row + k][col - k] == 0:
            new_board = copy_board(board)
            new_board[row + k][col - k] = piece
            new_board[row][col] = 0
            move_desc = move_desc_helper(row, col, row + k, col - k)
            new_boards.append([move_desc, new_board])
        else:
            break
        k = k + 1
    if row + k < 7 and col - k > 0 and board[row + k + 1][col - k - 1] == 0:
        if who(board[row + k][col - k]) != current_player and board[row + k][col - k] != 0:
            new_board = copy_board(board)
            new_board[row + k + 1][col - k - 1] = piece
            new_board[row + k][col - k] = 0
            new_board[row][col] = 0
            move_desc = move_desc_helper(row, col, row + k + 1, col - k - 1)
            new_boards.append([move_desc, new_board])
    # no.8
    k = 1
    while row - k > -1 and col - k > -1:
        if board[row - k][col - k] == 0:
            new_board = copy_board(board)
            new_board[row - k][col - k] = piece
            new_board[row][col] = 0
            move_desc = move_desc_helper(row, col, row - k, col - k)
            new_boards.append([move_desc, new_board])
        else:
            break
        k = k + 1
    if row - k > 0 and col - k > 0 and board[row - k - 1][col - k - 1] == 0:
        if who(board[row - k][col - k]) != current_player and board[row - k][col - k] != 0:
            new_board = copy_board(board)
            new_board[row - k - 1][col - k - 1] = piece
            new_board[row - k][col - k] = 0
            new_board[row][col] = 0
            move_desc = move_desc_helper(row, col, row - k - 1, col - k - 1)
            new_boards.append([move_desc, new_board])

    return new_boards


def coordinator(piece, row, col, board, current_player):
    new_boards = []
    # no.1
    k = 1
    while col + k < 8:
        if board[row][col + k] == 0:
            new_board = copy_board(board)
            new_board[row][col + k] = piece
            new_board[row][col] = 0
            coordinator_helper(row, col + k, new_board, current_player)
            move_desc = move_desc_helper(row, col, row, col + k)
            new_boards.append([move_desc, new_board])
        else:
            break
        k = k + 1
    # no.2
    k = 1
    while col - k > -1:
        if board[row][col - k] == 0:
            new_board = copy_board(board)
            new_board[row][col - k] = piece
            new_board[row][col] = 0
            coordinator_helper(row, col - k, new_board, current_player)
            move_desc = move_desc_helper(row, col, row, col - k)
            new_boards.append([move_desc, new_board])
        else:
            break
        k = k + 1
    # no.3
    k = 1
    while row + k < 8:
        if board[row + k][col] == 0:
            new_board = copy_board(board)
            new_board[row + k][col] = piece
            new_board[row][col] = 0
            coordinator_helper(row + k, col, new_board, current_player)
            move_desc = move_desc_helper(row, col, row + k, col)
            new_boards.append([move_desc, new_board])
        else:
            break
        k = k + 1
    # no.4
    k = 1
    while row - k > -1:
        if board[row - k][col] == 0:
            new_board = copy_board(board)
            new_board[row - k][col] = piece
            new_board[row][col] = 0
            coordinator_helper(row - k, col, new_board, current_player)
            move_desc = move_desc_helper(row, col, row - k, col)
            new_boards.append([move_desc, new_board])
        else:
            break
        k = k + 1
    # no.5
    k = 1
    while k + row < 8 and k + col < 8:
        if board[row + k][col + k] == 0:
            new_board = copy_board(board)
            new_board[row + k][col + k] = piece
            new_board[row][col] = 0
            coordinator_helper(row + k, col + k, new_board, current_player)
            move_desc = move_desc_helper(row, col, row + k, col + k)
            new_boards.append([move_desc, new_board])
        else:
            break
        k = k + 1
    # no.6
    k = 1
    while row - k > -1 and col + k < 8:
        if board[row - k][col + k] == 0:
            new_board = copy_board(board)
            new_board[row - k][col + k] = piece
            new_board[row][col] = 0
            coordinator_helper(row - k, col + k, new_board, current_player)
            move_desc = move_desc_helper(row, col, row - k, col + k)
            new_boards.append([move_desc, new_board])
        else:
            break
        k = k + 1
    # no.7
    k = 1
    while k + row < 8 and col - k > -1:
        if board[row + k][col - k] == 0:
            new_board = copy_board(board)
            new_board[row + k][col - k] = piece
            new_board[row][col] = 0
            coordinator_helper(row + k, col - k, new_board, current_player)
            move_desc = move_desc_helper(row, col, row + k, col - k)
            new_boards.append([move_desc, new_board])
        else:
            break
        k = k + 1
    # no.8
    k = 1
    while row - k > -1 and col - k > -1:
        if board[row - k][col - k] == 0:
            new_board = copy_board(board)
            new_board[row - k][col - k] = piece
            new_board[row][col] = 0
            coordinator_helper(row - k, col - k, new_board, current_player)
            move_desc = move_desc_helper(row, col, row - k, col - k)
            new_boards.append([move_desc, new_board])
        else:
            break
        k = k + 1

    return new_boards


def coordinator_helper(row, col, board, current_player):
    for i in range(8):
        for j in range(8):
            current_piece = board[i][j]
            if current_piece == 12 + current_player:
                if who(board[row][j]) != current_player:
                    board[row][j] = 0
                if who(board[i][col]) != current_player:
                    board[i][col] = 0
            return


def freezer(piece, row, col, board):
    new_boards = []
    # no.1
    k = 1
    while col + k < 8:
        if board[row][col + k] == 0:
            new_board = copy_board(board)
            new_board[row][col + k] = piece
            new_board[row][col] = 0
            move_desc = move_desc_helper(row, col, row, col + k)
            new_boards.append([move_desc, new_board])
        else:
            break
        k = k + 1
    # no.2
    k = 1
    while col - k > -1:
        if board[row][col - k] == 0:
            new_board = copy_board(board)
            new_board[row][col - k] = piece
            new_board[row][col] = 0
            move_desc = move_desc_helper(row, col, row, col - k)
            new_boards.append([move_desc, new_board])
        else:
            break
        k = k + 1
    # no.3
    k = 1
    while row + k < 8:
        if board[row + k][col] == 0:
            new_board = copy_board(board)
            new_board[row + k][col] = piece
            new_board[row][col] = 0
            move_desc = move_desc_helper(row, col, row + k, col)
            new_boards.append([move_desc, new_board])
        else:
            break
        k = k + 1
    # no.4
    k = 1
    while row - k > -1:
        if board[row - k][col] == 0:
            new_board = copy_board(board)
            new_board[row - k][col] = piece
            new_board[row][col] = 0
            move_desc = move_desc_helper(row, col, row - k, col)
            new_boards.append([move_desc, new_board])
        else:
            break
        k = k + 1
    # no.5
    k = 1
    while k + row < 8 and k + col < 8:
        if board[row + k][col + k] == 0:
            new_board = copy_board(board)
            new_board[row + k][col + k] = piece
            new_board[row][col] = 0
            move_desc = move_desc_helper(row, col, row + k, col + k)
            new_boards.append([move_desc, new_board])
        else:
            break
        k = k + 1
    # no.6
    k = 1
    while row - k > -1 and col + k < 8:
        if board[row - k][col + k] == 0:
            new_board = copy_board(board)
            new_board[row - k][col + k] = piece
            new_board[row][col] = 0
            move_desc = move_desc_helper(row, col, row - k, col + k)
            new_boards.append([move_desc, new_board])
        else:
            break
        k = k + 1
    # no.7
    k = 1
    while k + row < 8 and col - k > -1:
        if board[row + k][col - k] == 0:
            new_board = copy_board(board)
            new_board[row + k][col - k] = piece
            new_board[row][col] = 0
            move_desc = move_desc_helper(row, col, row + k, col - k)
            new_boards.append([move_desc, new_board])
        else:
            break
        k = k + 1
    # no.8
    k = 1
    while row - k > -1 and col - k > -1:
        if board[row - k][col - k] == 0:
            new_board = copy_board(board)
            new_board[row - k][col - k] = piece
            new_board[row][col] = 0
            move_desc = move_desc_helper(row, col, row - k, col - k)
            new_boards.append([move_desc, new_board])
        else:
            break
        k = k + 1

    return new_boards


def king(piece, row, col, board, player):
    child_boards = []

    neighbors = itertools.product([-1, 0, 1], [-1, 0, 1])
    for neighbor in neighbors:
        temp_r = row + neighbor[0]
        temp_c = col + neighbor[1]
        if 0 <= temp_r < 8 and 0 <= temp_c < 8:
            if board[temp_r][temp_c] == 0 or who(board[temp_r][temp_c]) != player:
                temp = copy_board(board)
                temp[temp_r][temp_c] = piece
                temp[row][col] = 0
                move_desc = move_desc_helper(row, col, temp_r, temp_c)
                child_boards.append([move_desc, temp])

    return child_boards


def imitator(piece, row, col, board, player):
    child_boards = []
    # no.1
    k = 1
    while col + k < 8:
        if board[row][col + k] == 0:
            new_board = copy_board(board)
            new_board[row][col + k] = piece
            new_board[row][col] = 0
            move_desc = move_desc_helper(row, col, row, col + k)
            child_boards.append([move_desc, new_board])

            w_board = copy_board(new_board)
            if col > 0 and who(board[row][col - 1]) != player and CODE_TO_INIT[board[row][col - 1]].lower() == 'w':
                w_board[row][col - 1] = 0
            w_move_desc = move_desc_helper(row, col, row, col + k)
            child_boards.append([w_move_desc, w_board])

            p_board = copy_board(new_board)
            imitate_pincer(row, col + k, p_board, player)
            p_move_desc = move_desc_helper(row, col, row, col + k)
            child_boards.append([p_move_desc, p_board])

            c_board = copy_board(new_board)
            for i in range(8):
                for j in range(8):
                    if c_board[i][j] == c_board[row][col + k] + 4:
                        if who(c_board[i][col + k]) != player and CODE_TO_INIT[c_board[i][col + k]].lower() == 'c':
                            c_board[i][col + k] = 0
                    if who(c_board[row][j]) != player and CODE_TO_INIT[c_board[row][j]].lower() == 'c':
                            c_board[row][j] = 0
            c_move_desc = move_desc_helper(row, col, row, col + k)
            child_boards.append([c_move_desc, c_board])
        else:
            break
        k = k + 1
    if col + k < 7 and board[row][col + k + 1] == 0:
        if who(board[row][col + k]) != player and board[row][col + k] != 0:
            new_board = copy_board(board)
            new_board[row][col + k + 1] = piece
            new_board[row][col + k] = 0
            new_board[row][col] = 0
            move_desc = move_desc_helper(row, col, row, col + k + 1)
            child_boards.append([move_desc, new_board])
    # no.2
    k = 1
    while col - k > -1:
        if board[row][col - k] == 0:
            new_board = copy_board(board)
            new_board[row][col - k] = piece
            new_board[row][col] = 0
            move_desc = move_desc_helper(row, col, row, col - k)
            child_boards.append([move_desc, new_board])

            w_board = copy_board(new_board)
            if col < 7 and who(board[row][col + 1]) != player and CODE_TO_INIT[board[row][col + 1]].lower() == 'w':
                w_board[row][col + 1] = 0
            w_move_desc = move_desc_helper(row, col, row, col - k)
            child_boards.append([w_move_desc, w_board])

            p_board = copy_board(new_board)
            imitate_pincer(row, col - k, p_board, player)
            p_move_desc = move_desc_helper(row, col, row, col - k)
            child_boards.append([p_move_desc, p_board])

            c_board = copy_board(new_board)
            for i in range(8):
                for j in range(8):
                    if c_board[i][j] == c_board[row][col - k] + 4:
                        if who(c_board[i][col - k]) != player and CODE_TO_INIT[c_board[i][col - k]].lower() == 'c':
                            c_board[i][col - k] = 0
                    if who(c_board[row][j]) != player and CODE_TO_INIT[c_board[row][j]].lower() == 'c':
                            c_board[row][j] = 0
            c_move_desc = move_desc_helper(row, col, row, col - k)
            child_boards.append([c_move_desc, c_board])
        else:
            break
        k = k + 1
    if col + k > 0 and board[row][col - k - 1] == 0:
        if who(board[row][col - k]) != player and board[row][col - k] != 0:
            new_board = copy_board(board)
            new_board[row][col - k - 1] = piece
            new_board[row][col - k] = 0
            new_board[row][col] = 0
            move_desc = move_desc_helper(row, col, row, col - k - 1)
            child_boards.append([move_desc, new_board])
    # no.3
    k = 1
    while row + k < 8:
        if board[row + k][col] == 0:
            new_board = copy_board(board)
            new_board[row + k][col] = piece
            new_board[row][col] = 0
            move_desc = move_desc_helper(row, col, row + k, col)
            child_boards.append([move_desc, new_board])

            w_board = copy_board(new_board)
            if row > 0 and who(board[row - 1][col]) != player and CODE_TO_INIT[board[row - 1][col]].lower() == 'w':
                w_board[row - 1][col] = 0
            w_move_desc = move_desc_helper(row, col, row + k, col)
            child_boards.append([w_move_desc, w_board])

            p_board = copy_board(new_board)
            imitate_pincer(row + k, col, p_board, player)
            p_move_desc = move_desc_helper(row, col, row + k, col)
            child_boards.append([p_move_desc, p_board])

            c_board = copy_board(new_board)
            for i in range(8):
                for j in range(8):
                    if c_board[i][j] == c_board[row + k][col] + 4:
                        if who(c_board[i][col]) != player and CODE_TO_INIT[c_board[i][col]].lower() == 'c':
                            c_board[i][col] = 0
                        if who(c_board[row + k][j]) != player and CODE_TO_INIT[c_board[row + k][j]].lower() == 'c':
                            c_board[row + k][j] = 0
            c_move_desc = move_desc_helper(row, col, row + k, col)
            child_boards.append([c_move_desc, c_board])
        else:
            break
        k = k + 1
    if row + k < 7 and board[row + k + 1][col] == 0:
        if who(board[row + k][col]) != player and board[row + k][col] != 0:
            new_board = copy_board(board)
            new_board[row + k + 1][col] = piece
            new_board[row + k][col] = 0
            new_board[row][col] = 0
            move_desc = move_desc_helper(row, col, row + k + 1, col)
            child_boards.append([move_desc, new_board])
    # no.4
    k = 1
    while row - k > -1:
        if board[row - k][col] == 0:
            new_board = copy_board(board)
            new_board[row - k][col] = piece
            new_board[row][col] = 0
            move_desc = move_desc_helper(row, col, row - k, col)
            child_boards.append([move_desc, new_board])

            w_board = copy_board(new_board)
            if row < 7 and who(board[row + 1][col]) != player and CODE_TO_INIT[board[row + 1][col]].lower() == 'w':
                w_board[row + 1][col] = 0
            w_move_desc = move_desc_helper(row, col, row - k, col)
            child_boards.append([w_move_desc, w_board])

            p_board = copy_board(new_board)
            imitate_pincer(row - k, col, p_board, player)
            p_move_desc = move_desc_helper(row, col, row - k, col)
            child_boards.append([p_move_desc, p_board])

            c_board = copy_board(new_board)
            for i in range(8):
                for j in range(8):
                    if c_board[i][j] == c_board[row - k][col] + 4:
                        if who(c_board[i][col]) != player and CODE_TO_INIT[c_board[i][col]].lower() == 'c':
                            c_board[i][col] = 0
                        if who(c_board[row - k][j]) != player and CODE_TO_INIT[c_board[row - k][j]].lower() == 'c':
                            c_board[row - k][j] = 0
            c_move_desc = move_desc_helper(row, col, row - k, col)
            child_boards.append([c_move_desc, c_board])
        else:
            break
        k = k + 1
    if row - k > 0 and board[row - k - 1][col] == 0:
        if who(board[row - k][col]) != player and board[row - k][col] != 0:
            new_board = copy_board(board)
            new_board[row - k - 1][col] = piece
            new_board[row - k][col] = 0
            new_board[row][col] = 0
            move_desc = move_desc_helper(row, col, row - k - 1, col)
            child_boards.append([move_desc, new_board])
    # no.5
    k = 1
    while k + row < 8 and k + col < 8:
        if board[row + k][col + k] == 0:
            new_board = copy_board(board)
            new_board[row + k][col + k] = piece
            new_board[row][col] = 0
            move_desc = move_desc_helper(row, col, row + k, col + k)
            child_boards.append([move_desc, new_board])

            w_board = copy_board(new_board)
            if row > 0 and col > 0 and who(board[row - 1][col - 1]) != player and \
                    CODE_TO_INIT[board[row - 1][col - 1]].lower() == 'w':
                w_board[row - 1][col - 1] = 0
            w_move_desc = move_desc_helper(row, col, row + k, col + k)
            child_boards.append([w_move_desc, w_board])

            p_board = copy_board(new_board)
            imitate_pincer(row + k, col + k, p_board, player)
            p_move_desc = move_desc_helper(row, col, row + k, col + k)
            child_boards.append([p_move_desc, p_board])

            c_board = copy_board(new_board)
            for i in range(8):
                for j in range(8):
                    if c_board[i][j] == c_board[row + k][col + k] + 4:
                        if who(c_board[i][col + k]) != player and CODE_TO_INIT[c_board[i][col + k]].lower() == 'c':
                            c_board[i][col + k] = 0
                        if who(c_board[row + k][j]) != player and CODE_TO_INIT[c_board[row + k][j]].lower() == 'c':
                            c_board[row + k][j] = 0
            c_move_desc = move_desc_helper(row, col, row + k, col + k)
            child_boards.append([c_move_desc, c_board])
        else:
            break
        k = k + 1
    if row + k < 7 and col + k < 7 and board[row + k + 1][col + k + 1] == 0:
        if who(board[row + k][col + k]) != player and board[row + k][col + k] != 0:
            new_board = copy_board(board)
            new_board[row + k + 1][col + k + 1] = piece
            new_board[row + k][col + k] = 0
            new_board[row][col] = 0
            move_desc = move_desc_helper(row, col, row + k + 1, col + k + 1)
            child_boards.append([move_desc, new_board])
    # no.6
    k = 1
    while row - k > -1 and col + k < 8:
        if board[row - k][col + k] == 0:
            new_board = copy_board(board)
            new_board[row - k][col + k] = piece
            new_board[row][col] = 0
            move_desc = move_desc_helper(row, col, row - k, col + k)
            child_boards.append([move_desc, new_board])

            w_board = copy_board(new_board)
            if row < 7 and col > 0 and who(board[row + 1][col - 1]) != player and \
                    CODE_TO_INIT[board[row + 1][col - 1]].lower() == 'w':
                w_board[row + 1][col - 1] = 0
            w_move_desc = move_desc_helper(row, col, row - k, col + k)
            child_boards.append([w_move_desc, w_board])

            p_board = copy_board(new_board)
            imitate_pincer(row - k, col + k, p_board, player)
            p_move_desc = move_desc_helper(row, col, row - k, col + k)
            child_boards.append([p_move_desc, p_board])

            c_board = copy_board(new_board)
            for i in range(8):
                for j in range(8):
                    if c_board[i][j] == c_board[row - k][col + k] + 4:
                        if who(c_board[i][col + k]) != player and CODE_TO_INIT[c_board[i][col + k]].lower() == 'c':
                            c_board[i][col + k] = 0
                        if who(c_board[row - k][j]) != player and CODE_TO_INIT[c_board[row - k][j]].lower() == 'c':
                            c_board[row - k][j] = 0
            c_move_desc = move_desc_helper(row, col, row - k, col + k)
            child_boards.append([c_move_desc, c_board])
        else:
            break
        k = k + 1
    if row - k > 0 and col + k < 7 and board[row - k - 1][col + k + 1] == 0:
        if who(board[row - k][col + k]) != player and board[row - k][col + k] != 0:
            new_board = copy_board(board)
            new_board[row - k - 1][col + k + 1] = piece
            new_board[row - k][col + k] = 0
            new_board[row][col] = 0
            move_desc = move_desc_helper(row, col, row - k - 1, col + k + 1)
            child_boards.append([move_desc, new_board])
    # no.7
    k = 1
    while k + row < 8 and col - k > -1:
        if board[row + k][col - k] == 0:
            new_board = copy_board(board)
            new_board[row + k][col - k] = piece
            new_board[row][col] = 0
            move_desc = move_desc_helper(row, col, row + k, col - k)
            child_boards.append([move_desc, new_board])

            w_board = copy_board(new_board)
            if row > 0 and col < 7 and who(board[row - 1][col + 1]) != player and \
                    CODE_TO_INIT[board[row - 1][col + 1]].lower() == 'w':
                w_board[row - 1][col + 1] = 0
            w_move_desc = move_desc_helper(row, col, row + k, col - k)
            child_boards.append([w_move_desc, w_board])

            p_board = copy_board(new_board)
            imitate_pincer(row + k, col - k, p_board, player)
            p_move_desc = move_desc_helper(row, col, row + k, col - k)
            child_boards.append([p_move_desc, p_board])

            c_board = copy_board(new_board)
            for i in range(8):
                for j in range(8):
                    if c_board[i][j] == c_board[row + k][col - k] + 4:
                        if who(c_board[i][col - k]) != player and CODE_TO_INIT[c_board[i][col - k]].lower() == 'c':
                            c_board[i][col - k] = 0
                        if who(c_board[row + k][j]) != player and CODE_TO_INIT[c_board[row + k][j]].lower() == 'c':
                            c_board[row + k][j] = 0
            c_move_desc = move_desc_helper(row, col, row + k, col - k)
            child_boards.append([c_move_desc, c_board])
        else:
            break
        k = k + 1
    if row + k < 7 and col - k > 0 and board[row + k + 1][col - k - 1] == 0:
        if who(board[row + k][col - k]) != player and board[row + k][col - k] != 0:
            new_board = copy_board(board)
            new_board[row + k + 1][col - k - 1] = piece
            new_board[row + k][col - k] = 0
            new_board[row][col] = 0
            move_desc = move_desc_helper(row, col, row + k + 1, col - k - 1)
            child_boards.append([move_desc, new_board])
    # no.8
    k = 1
    while row - k > -1 and col - k > -1:
        if board[row - k][col - k] == 0:
            new_board = copy_board(board)
            new_board[row - k][col - k] = piece
            new_board[row][col] = 0
            move_desc = move_desc_helper(row, col, row - k, col - k)
            child_boards.append([move_desc, new_board])

            w_board = copy_board(new_board)
            if row < 7 and col < 7 and who(board[row + 1][col + 1]) != player and \
                    CODE_TO_INIT[board[row + 1][col + 1]].lower() == 'w':
                w_board[row + 1][col + 1] = 0
            w_move_desc = move_desc_helper(row, col, row - k, col - k)
            child_boards.append([w_move_desc, w_board])

            p_board = copy_board(new_board)
            imitate_pincer(row - k, col - k, p_board, player)
            p_move_desc = move_desc_helper(row, col, row - k, col - k)
            child_boards.append([p_move_desc, p_board])

            c_board = copy_board(new_board)
            for i in range(8):
                for j in range(8):
                    if c_board[i][j] == c_board[row - k][col - k] + 4:
                        if who(c_board[i][col - k]) != player and CODE_TO_INIT[c_board[i][col - k]].lower() == 'c':
                            c_board[i][col - k] = 0
                        if who(c_board[row - k][j]) != player and CODE_TO_INIT[c_board[row - k][j]].lower() == 'c':
                            c_board[row - k][j] = 0
            c_move_desc = move_desc_helper(row, col, row - k, col - k)
            child_boards.append([c_move_desc, c_board])
        else:
            break
        k = k + 1
    if row - k > 0 and col - k > 0 and board[row - k - 1][col - k - 1] == 0:
        if who(board[row - k][col - k]) != player and board[row - k][col - k] != 0:
            new_board = copy_board(board)
            new_board[row - k - 1][col - k - 1] = piece
            new_board[row - k][col - k] = 0
            new_board[row][col] = 0
            move_desc = move_desc_helper(row, col, row - k - 1, col - k - 1)
            child_boards.append([move_desc, new_board])

    neighbors = itertools.product([-1, 0, 1], [-1, 0, 1])
    for neighbor in neighbors:
        temp_r = row + neighbor[0]
        temp_c = col + neighbor[1]
        if 0 <= temp_r < 8 and 0 <= temp_c < 8:
            if board[temp_r][temp_c] == 0 or who(board[temp_r][temp_c]) != player:
                temp = copy_board(board)
                temp[temp_r][temp_c] = piece
                temp[row][col] = 0
                move_desc = move_desc_helper(row, col, temp_r, temp_c)
                child_boards.append([move_desc, temp])

    return child_boards


def imitate_pincer(row, col, board, player):
    for i in [-2, 0, 2]:
        for j in [-2, 0, 2]:
            temp_r = row + i
            temp_c = col + j
            if 0 <= temp_r < 8 and 0 <= temp_c < 8:
                be_captured_r = row + int(i / 2)
                be_captured_c = col + int(j / 2)
                if board[temp_r][temp_c] != 0 and CODE_TO_INIT[board[be_captured_r][be_captured_c]].lower() == 'p' and \
                        who(board[temp_r][temp_c]) == player and who(board[be_captured_r][be_captured_c]) != player:
                    board[be_captured_r][be_captured_c] = 0
                    return
