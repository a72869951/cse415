'''PlayerSkeletonA.py
The beginnings of an agent that might someday play Baroque Chess.

'''
from BC_state_etc import *
import itertools
import random
import time


def parameterized_minimax(currentState, alphaBeta=False, ply=3,\
    useBasicStaticEval=True, useZobristHashing=False):
  '''Implement this testing function for your agent's basic
  capabilities here.'''
  global N_STATES_EXPANDED
  global N_STATIC_EVALS
  global N_CUTOFFS
  initTime = time.clock()
  timeLimit = 20
  result_state = minimax_search(currentState, currentState, "", 1, initTime, timeLimit, ply, False, True)
  if useBasicStaticEval:
      CURRENT_STATE_STATIC_VAL = basic_staticEval(currentState)
  else:
      CURRENT_STATE_STATIC_VAL = basic_staticEval(currentState)

  return {'CURRENT_STATE_STATIC_VAL': CURRENT_STATE_STATIC_VAL, 'N_STATES_EXPANDED': N_STATIC_EVALS,
          'N_STATIC_EVALS': 1, 'N_CUTOFFS': N_CUTOFFS}

def minimax(state,initTime, timeLimit,plyLeft):
    global N_STATES_EXPANDED
    global N_STATIC_EVALS
    global N_CUTOFFS
    N_STATES_EXPANDED=0
    N_STATIC_EVALS=0
    N_CUTOFFS=0
    return minimax_search(state, state, "", 1, initTime, timeLimit, plyLeft,False, False)

def minimax_search(state, first, desc, level, initTime, timeLimit, plyLeft,alphaBeta=False, useBasicStaticEval=True):
    # state is the current state, desc record the first move, level is the current depth, plyLeft is rest of ply,
    global TimeOut
    global N_STATES_EXPANDED
    global N_STATIC_EVALS
    global N_CUTOFFS

    if plyLeft == 0:
        global N_STATIC_EVALS
        N_STATIC_EVALS=N_STATIC_EVALS+1
        if not useBasicStaticEval:
            return [staticEval(state), state, first, desc, level, TimeOut]
        else:return [basic_staticEval(state), state, first, desc, level, TimeOut]

    if state.whose_move == WHITE:
        provisional = [-100000, state, first, desc, level, TimeOut]
    else:
        provisional = [100000, state, first, desc, level, TimeOut]
    for s in look_for_child_in(state):  # s is one of the legal successors for 'state'
        N_STATES_EXPANDED=N_STATES_EXPANDED+1
        if level == 1:
            desc = s[0]  # set decision to be s[0]
            first = BC_state(s[1], opponent(state.whose_move))  # set this "s" state to be supposed state to return
        currTime = time.clock()
        if (currTime - initTime) > (timeLimit * 0.9):
            TimeOut = True
            provisional[-1] = True
            break  # if time reach the limit, break
        newVal = minimax_search(BC_state(s[1], opponent(state.whose_move)), first, desc, level+1,
                            initTime, timeLimit, plyLeft-1,False,False)

        if (state.whose_move == BLACK and newVal[0] == provisional[0]) or (state.whose_move == WHITE and newVal[0] == provisional[0]):
            randomint = random.randint(0, 1)
            if randomint == 0:
                provisional = newVal
        if (state.whose_move == BLACK and newVal[0] < provisional[0]) or (state.whose_move == WHITE and newVal[0] > provisional[0]):
            provisional = newVal
    return provisional

piece_vals = [0, 0, -10, 10, -20, 20, -20, 20, -30, 30, -80, 80, -1000, 1000, -20, 20]

def makeMove(currentState, currentRemark, timelimit=10):
    global TimeOut
    TimeOut = False
    initTime = time.clock()

    for ply in range(1, 16):#using IDDFS for depth 1 to 16
        newState = minimax(currentState, initTime, timelimit, ply)
        if newState[-1] == True:
            break
    # print(" the three value:")
    # print(N_STATES_EXPANDED)
    # print(N_STATIC_EVALS)
    # print(N_CUTOFFS)

    return [[newState[3], BC_state(newState[2].board, newState[2].whose_move)], random.choice(PUNTS)]


PUNTS = ["Smash!",
         "You are weak.",
         "I am the best.",
         "I am inevitable.",
         "You are not the only one cursed with knowledge.",
         "You will lose",
         "that's the best you can do?",
         "No matter what you try, there will only one result.",
         "No one can match me in the universe.",
         "You have my respect.",
         "All that much time for this move?"]

def nickname():
    return "Thanos"

def introduce():
    return "My name is Thanos, my designer is JingQiang Wang and Junhao Zeng "


def prepare(player2Nickname):
    ''' Here the game master will give your agent the nickname of
    the opponent agent, in case your agent can use it in some of
    the dialog responses.  Other than that, this function can be
    used for initializing data structures, if needed.'''
    pass

def basicStaticEval(state):
    '''Use the simple method for state evaluation described in the spec.
    This is typically used in parameterized_minimax calls to verify
    that minimax and alpha-beta pruning work correctly.'''
    return sum([sum([piece_vals[j] for j in i]) for i in state.board])

def staticEval(state):
    '''Compute a more thorough static evaluation of the given state.
    This is intended for normal competitive play.  How you design this
    function could have a significant impact on your player's ability
    to win games.'''
    return sum([sum([piece_vals[j] for j in i]) for i in state.board])

def move_desc_helper(r1, c1, r2, c2):
    return [(r1, c1 ), (r2 , c2 )]

# return the opppnent
def opponent(player):
    if player == WHITE:
        return BLACK
    else:
        return WHITE

def look_for_child_in(state):
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

# return a copy of the board, when we need to add a successor
def copy_board(board):
    new_board = [[0, 0, 0, 0, 0, 0, 0, 0] for r in range(8)]
    for i in range(8):
        for j in range(8):
            new_board[i][j] = board[i][j]
    return new_board


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


# movement rule and capture rule for pincer
def pincer(piece, row, col, board, player):
    child_boards = []

    # move right
    k = 1
    while col + k <= 7:
        if board[row][col + k] == 0:
            new_board = copy_board(board)
            new_board[row][col + k] = piece
            new_board[row][col] = 0
            pincer_helper(row, col + k, new_board, player)

            # generate movement
            move_desc = move_desc_helper(row, col, row, col + k)
            child_boards.append([move_desc, new_board])
        else:
            break
        k = k + 1

    # move
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

    # move east
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

    # move west
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
    return child_boards

# check whether the pincer can capture some enemy
def pincer_helper(row, col, board, player):
    for i in [-2, 0, 2]:
        for j in [-2, 0, 2]:

            # make sure pincer only capture enemy vertically or horizontally
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

    # move south
    k = 1
    while col + k < 8:
        if board[row][col + k] == 0:
            new_board = copy_board(board)
            new_board[row][col + k] = piece
            new_board[row][col] = 0

            # check whether withdrawer can capture some enmey
            if col > 0 and who(board[row][col - 1]) != current_player and board[row][col - 1] != 0:
                new_board[row][col - 1] = 0
            move_desc = move_desc_helper(row, col, row, col + k)
            new_boards.append([move_desc, new_board])
        else:
            break
        k = k + 1

    # move north
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

    # move east
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

    # move west
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

    # move northeast
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

            # find the king first, then check the diagonal
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