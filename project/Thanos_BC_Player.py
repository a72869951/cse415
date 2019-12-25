'''PlayerSkeletonA.py
The beginnings of an agent that might someday play Baroque Chess.

'''
from BC_state_etc import *
import random
import time
import itertools


def parameterized_minimax(currentState, alphaBeta=True, ply=3, useBasicStaticEval=False):
    '''Implement this testing function for your agent's basic
    capabilities here.'''
    global N_STATES_EXPANDED
    global N_STATIC_EVALS
    global N_CUTOFFS
    initTime = time.clock()
    timeLimit = 20
    result_state = minimax_search(currentState, currentState, "", 1, initTime, timeLimit, ply, alphaBeta, useBasicStaticEval)
    if useBasicStaticEval:
      CURRENT_STATE_STATIC_VAL = basicStaticEval(currentState)
    else:
      CURRENT_STATE_STATIC_VAL = staticEval(currentState)
    return {'CURRENT_STATE_STATIC_VAL': CURRENT_STATE_STATIC_VAL, 'N_STATES_EXPANDED': N_STATES_EXPANDED,
          'N_STATIC_EVALS': N_STATIC_EVALS, 'N_CUTOFFS': N_CUTOFFS}

def minimax(state,initTime, timeLimit,plyLeft):
    global N_STATES_EXPANDED
    global N_STATIC_EVALS
    global N_CUTOFFS
    N_STATES_EXPANDED=0
    N_STATIC_EVALS=0
    N_CUTOFFS=0
    return minimax_search(state, state, "", 1, initTime, timeLimit, plyLeft, True, False)

# minmax search and alpha beta pruning
def minimax_search(state, first, desc, level, initTime, timeLimit, plyLeft,alphaBeta=True,
                   useBasicStaticEval=False,alpha=-99999 ,beta=99999):

    # state is the current state, desc record the first move, level is the current depth, plyLeft is rest of ply,
    global TimeOut
    global N_STATES_EXPANDED
    global N_STATIC_EVALS
    global N_CUTOFFS
    global zhash_table
    if plyLeft == 0:
        global N_STATIC_EVALS
        N_STATIC_EVALS=N_STATIC_EVALS+1
        if not useBasicStaticEval:
            eval=zhash_table.get(hash_state(state))
            if eval is None:
                eval=staticEval(state)
                h=hash_state(state)
                zhash_table[h]=eval

            # eval=zhash_table.get(hash_state(state), staticEval(state))
            # eval=staticEval(state)

        else:
            eval = zhash_table.get(hash_state(state))
            if eval is None:
                eval = basicStaticEval(state)
                h = hash_state(state)
                zhash_table[h] = eval
            # eval = zhash_table.get(hash_state(state), basicStaticEval(state))
            # eval=basicStaticEval(state)
        return [eval, state, first, desc, level, TimeOut]
    if state.whose_move == WHITE:
        temp = [-99999, state, first, desc, level, TimeOut]
    else:
        temp = [99999, state, first, desc, level, TimeOut]
    for s in successors_generate(state):  # s is one of the legal successors for 'state'
        if level == 1:
            desc = s[0]  # set decision to be s[0]
            first = BC_state(s[1], other_side(state.whose_move))  # set this "s" state to be supposed state to return
        currTime = time.clock()
        if (currTime - initTime) > (timeLimit * 0.9):
            TimeOut = True
            temp[-1] = True
            break  # if time reach the limit, break
        newVal = minimax_search(BC_state(s[1], other_side(state.whose_move)), first, desc, level+1,
                            initTime, timeLimit, plyLeft-1, alphaBeta, useBasicStaticEval, alpha, beta)
        if state.whose_move == WHITE:
            if newVal[0] > temp[0]:
                temp = newVal
            if newVal[0] == temp[0]:
                randomint = random.randint(0, 1)
                if randomint == 0:
                    temp = newVal
            if alphaBeta:
                alpha = max(alpha, temp[0])
                if beta <= alpha:
                    N_CUTOFFS += 1
                    break
        if state.whose_move == BLACK:
            if newVal[0] < temp[0]:
                temp = newVal
            if newVal[0] == temp[0]:
                randomint = random.randint(0, 1)
                if randomint == 0:
                    temp = newVal
            if alphaBeta:
                beta = min(beta,  temp[0])
                if beta <= alpha:
                    N_CUTOFFS += 1
                    break
    return temp

def makeMove(currentState, currentRemark, timelimit=10):
    global TimeOut
    TimeOut = False
    initTime = time.clock()
    for ply in range(1, 16):#using IDDFS for depth 1 to 16
        newState = minimax(currentState, initTime, timelimit, ply)
        if newState[-1] == True:
            break
        else:
            tempBestState = newState
    # print for debugging
    # print our for debugging
    print(" the three value:")
    print(N_STATES_EXPANDED)
    print(N_STATIC_EVALS)
    print(N_CUTOFFS)
    print("ply：")
    print(ply)
    return [[tempBestState[3], BC_state(tempBestState[2].board, tempBestState[2].whose_move)], random_remark()]

def random_remark():
    global opponent_name
    remark = ["Smash!",
             "You are weak.",
             "I am the best.",
             "I am inevitable.",
             "You are not the only one cursed with knowledge," + str(opponent_name) + ".",
             "You will lose",
             "that's the best you can do?",
             "No matter what you try, there will only one result.",
             "No one can match me in the universe.",
             "You have my respect.",
             "All that much time for this move?"
             "let it be fear"]
    return random.choice(remark)

def nickname():
    return "Thanos"

def introduce():
    return "My name is Thanos, my designer is Jingqiang Wang and Junhao Zeng "


def prepare(player2Nickname):
    ''' Here the game master will give your agent the nickname of
    the opponent agent, in case your agent can use it in some of
    the dialog responses.  Other than that, this function can be
    used for initializing data structures, if needed.'''
    global opponent_name
    opponent_name = player2Nickname
    init_table()



basic_piece_vals = [0, 0, -1, 1, -2, 2, -2, 2, -2, 2, -2, 2, -100, 100, -2, 2]
importance = {'living_reward': 5, 'freezing_reward': 1, 'killing_reward': 4, 'king_guard': 4}
moves = [(1, -1), (1, 1), (-1, 1), (-1, -1), (0, 1), (1, 0), (-1, 0), (0, -1)]
advanced_static_value = {0: 0, 1: 1, 2: 5, 3: 5, 4: 5, 5: 2, 6: 100, 7: 8}

def basicStaticEval(state):
    '''Use the simple method for state evaluation described in the spec.
    This is typically used in parameterized_minimax calls to verify
    that minimax and alpha-beta pruning work correctly.'''
    return sum([sum([basic_piece_vals[x] for x in y]) for y in state.board])

def staticEval(state: object) -> object:
    '''Compute a more thorough static evaluation of the given state.
    This is intended for normal competitive play.  How you design this
    function could have a significant impact on your player's ability
    to win games.'''
    ally_points = 0
    enemy_points = 0
    enemy_king_down = True
    for yditection, row in enumerate(state.board):
        for xdirection, piece in enumerate(row):

            # do not need to do any calculations for empty square
            if piece == 0:
                continue

            # store nearby pieces
            neighbors = surrounding(state, yditection, xdirection, moves)

            # find piece score: you get a better score if you have more pieces
            if piece % 2 == 0:
                enemy_points -= importance['living_reward'] * advanced_static_value[piece // 2]
            else:
                ally_points += importance['living_reward'] * advanced_static_value[piece // 2]

            # the more enemies it can freeze, the higher the points
            if piece == 14 or (piece == 8 and 15 in neighbors):
                enemy_points -= importance['freezing_reward'] \
                                * sum([advanced_static_value[x // 2] for x in neighbors if x % 2 == 1])

            elif piece == 15 or (piece == 9 and 14 in neighbors):
                ally_points += importance['freezing_reward'] \
                               * sum([advanced_static_value[x // 2] for x in neighbors if x % 2 == 0])

            # the more a pincer can kill in one move, the higher the points
            elif piece == 2:
                enemy_points -= importance['killing_reward'] * pincer_kill(state, yditection, xdirection)

            elif piece == 3:
                ally_points += importance['killing_reward'] * pincer_kill(state, yditection, xdirection)

            # check how many allies there are near king
            elif piece == 12:
                enemy_king_down = False
                enemy_points -= importance['king_guard'] * sum([1 for x in neighbors if x % 2 == 0])
                enemy_points += importance['king_guard'] * sum([1 for x in neighbors if x % 2 == 1])

            elif piece == 13:
                ally_points += importance['king_guard'] * sum([1 for x in neighbors if x % 2 == 1])
                ally_points -= importance['king_guard'] * sum([1 for x in neighbors if x % 2 == 0])

    total_points = ally_points + enemy_points
    if enemy_king_down:
        return 100000
    return total_points

def movement_generator(r1, c1, r2, c2):
    return [(r1, c1), (r2, c2)]

# return the opppnent
def other_side(player):
    if player == WHITE:
        return BLACK
    else:
        return WHITE

def successors_generate(state):
    global N_STATES_EXPANDED
    N_STATES_EXPANDED = N_STATES_EXPANDED + 1
    board = state.board
    player = state.whose_move
    children = []
    for y in range(8):
        for x in range(8):
            p = board[y][x]
            if who(p) == player and p != 0:
                nextAllB = successors_generate_helper(board, player, p, y, x)
                children.extend(nextAllB)
    return children

# return a copy of the board, when we need to add a successor
def replication(board):
    nextB = [[0, 0, 0, 0, 0, 0, 0, 0] for _ in range(8)]
    for y in range(8):
        for x in range(8):
            nextB[y][x] = board[y][x]
    return nextB


def successors_generate_helper(board, player, p, yDirection, xDirection):
    succeossors = []
    if is_frozen(yDirection, xDirection, board, player):
        return succeossors
    elif CODE_TO_INIT[p].lower() == 'p':
        succeossors.extend(p_move(board, player, p, yDirection, xDirection))
    elif CODE_TO_INIT[p].lower() == 'k':
        succeossors.extend(k_move(board, player, p, yDirection, xDirection))
    elif CODE_TO_INIT[p].lower() == 'w':
        succeossors.extend(w_move(board, player, p, yDirection, xDirection))
    elif CODE_TO_INIT[p].lower() == 'l':
        succeossors.extend(l_move(board, player, p, yDirection, xDirection))
    elif CODE_TO_INIT[p].lower() == 'c':
        succeossors.extend(c_move(board, player, p, yDirection, xDirection))
    elif CODE_TO_INIT[p].lower() == 'f' or CODE_TO_INIT[p].lower() == 'i':
        succeossors.extend(freezer_or_imitator(p, yDirection, xDirection, board))
    return succeossors


# movement rule and capture rule for p_move
def p_move(board, player, p, yDirection, xDirection):
    succeossors = []

    # move E
    step = 1
    while xDirection + step <= 7:
        if board[yDirection][xDirection + step] == 0:
            nextB = replication(board)
            nextB[yDirection][xDirection + step] = p
            nextB[yDirection][xDirection] = 0
            p_capture(yDirection, xDirection + step, nextB, player)

            # generate standard movement
            form_move = movement_generator(yDirection, xDirection, yDirection, xDirection + step)
            succeossors.append([form_move, nextB])
        else:
            break
        step = step + 1

    # move W
    step = 1
    while xDirection - step >= 0:
        if board[yDirection][xDirection - step] == 0:
            nextB = replication(board)
            nextB[yDirection][xDirection - step] = p
            nextB[yDirection][xDirection] = 0
            p_capture(yDirection, xDirection - step, nextB, player)
            form_move = movement_generator(yDirection, xDirection, yDirection, xDirection - step)
            succeossors.append([form_move, nextB])
        else:
            break
        step = step + 1

    # move N
    step = 1
    while yDirection + step <= 7:
        if board[yDirection + step][xDirection] == 0:
            nextB = replication(board)
            nextB[yDirection + step][xDirection] = p
            nextB[yDirection][xDirection] = 0
            p_capture(yDirection + step, xDirection, nextB, player)
            form_move = movement_generator(yDirection, xDirection, yDirection + step, xDirection)
            succeossors.append([form_move, nextB])
        else:
            break
        step = step + 1

    # move S
    step = 1
    while yDirection - step >= 0:
        if board[yDirection - step][xDirection] == 0:
            nextB = replication(board)
            nextB[yDirection - step][xDirection] = p
            nextB[yDirection][xDirection] = 0
            p_capture(yDirection - step, xDirection, nextB, player)
            form_move = movement_generator(yDirection, xDirection, yDirection - step, xDirection)
            succeossors.append([form_move, nextB])
        else:
            break
        step = step + 1
    return succeossors

# check whether the p_move can capture some enemy
def p_capture(yDirection, xDirection, board, player):
    for y in [-2, 0, 2]:
        for x in [-2, 0, 2]:

            # make sure p_move only capture enemy vertically or horizontally
            if y * x == 0:
                potential_enemy_r = yDirection + y
                potential_enemy_c = xDirection + x
                if 0 <= potential_enemy_r <= 7 and 0 <= potential_enemy_c <= 7:
                    cap_y = yDirection + int(y / 2)
                    cap_x = xDirection + int(x / 2)
                    if board[potential_enemy_r][potential_enemy_c] != 0 \
                            and board[cap_y][cap_x] != 0 \
                            and who(board[potential_enemy_r][potential_enemy_c]) == player \
                            and who(board[cap_y][cap_x]) != player:
                            board[cap_y][cap_x] = 0
                            return


def w_move(board, player, p, yDirection, xDirection):
    nextAllB = []

    # move E
    step = 1
    while xDirection + step <= 7:
        if board[yDirection][xDirection + step] == 0:
            nextB = replication(board)
            nextB[yDirection][xDirection + step] = p
            nextB[yDirection][xDirection] = 0

            # check whether w_move can capture some enmey
            if xDirection > 0 \
                    and who(board[yDirection][xDirection - 1]) != player \
                    and board[yDirection][xDirection - 1] != 0:
                nextB[yDirection][xDirection - 1] = 0
            form_move = movement_generator(yDirection, xDirection, yDirection, xDirection + step)
            nextAllB.append([form_move, nextB])
        else:
            break
        step = step + 1

    # move W
    step = 1
    while xDirection - step >= 0:
        if board[yDirection][xDirection - step] == 0:
            nextB = replication(board)
            nextB[yDirection][xDirection - step] = p
            nextB[yDirection][xDirection] = 0
            if xDirection < 7 \
                    and who(board[yDirection][xDirection + 1]) != player \
                    and board[yDirection][xDirection + 1] != 0:
                nextB[yDirection][xDirection + 1] = 0
            form_move = movement_generator(yDirection, xDirection, yDirection, xDirection - step)
            nextAllB.append([form_move, nextB])
        else:
            break
        step = step + 1

    # move N
    step = 1
    while yDirection + step <= 7:
        if board[yDirection + step][xDirection] == 0:
            nextB = replication(board)
            nextB[yDirection + step][xDirection] = p
            nextB[yDirection][xDirection] = 0
            if yDirection > 0 \
                    and who(board[yDirection - 1][xDirection]) != player \
                    and board[yDirection - 1][xDirection] != 0:
                nextB[yDirection - 1][xDirection] = 0
            form_move = movement_generator(yDirection, xDirection, yDirection + step, xDirection)
            nextAllB.append([form_move, nextB])
        else:
            break
        step = step + 1

    # move S
    step = 1
    while yDirection - step >= 0:
        if board[yDirection - step][xDirection] == 0:
            nextB = replication(board)
            nextB[yDirection - step][xDirection] = p
            nextB[yDirection][xDirection] = 0
            if yDirection < 7 \
                    and who(board[yDirection + 1][xDirection]) != player \
                    and board[yDirection + 1][xDirection] != 0:
                nextB[yDirection + 1][xDirection] = 0
            form_move = movement_generator(yDirection, xDirection, yDirection - step, xDirection)
            nextAllB.append([form_move, nextB])
        else:
            break
        step = step + 1

    # move SE
    step = 1
    while step + yDirection <= 7 and step + xDirection <= 7:
        if board[yDirection + step][xDirection + step] == 0:
            nextB = replication(board)
            nextB[yDirection + step][xDirection + step] = p
            nextB[yDirection][xDirection] = 0
            if yDirection > 0 \
                    and xDirection > 0 \
                    and who(board[yDirection - 1][xDirection - 1]) != player \
                    and board[yDirection - 1][xDirection - 1] != 0:
                nextB[yDirection - 1][xDirection - 1] = 0
            form_move = movement_generator(yDirection, xDirection, yDirection + step, xDirection + step)
            nextAllB.append([form_move, nextB])
        else:
            break
        step = step + 1

    # move NE
    step = 1
    while yDirection - step >= 0 and xDirection + step <= 7:
        if board[yDirection - step][xDirection + step] == 0:
            nextB = replication(board)
            nextB[yDirection - step][xDirection + step] = p
            nextB[yDirection][xDirection] = 0
            if yDirection < 7 \
                    and xDirection > 0 \
                    and who(board[yDirection + 1][xDirection - 1]) != player \
                    and board[yDirection + 1][xDirection - 1] != 0:
                nextB[yDirection + 1][xDirection - 1] = 0
            form_move = movement_generator(yDirection, xDirection, yDirection - step, xDirection + step)
            nextAllB.append([form_move, nextB])
        else:
            break
        step = step + 1

    # move SW
    step = 1
    while step + yDirection <= 7 and xDirection - step >= 0:
        if board[yDirection + step][xDirection - step] == 0:
            nextB = replication(board)
            nextB[yDirection + step][xDirection - step] = p
            nextB[yDirection][xDirection] = 0
            if yDirection > 0 \
                    and xDirection < 7 \
                    and who(board[yDirection - 1][xDirection + 1]) != player \
                    and board[yDirection - 1][xDirection + 1] != 0:
                nextB[yDirection - 1][xDirection + 1] = 0
            form_move = movement_generator(yDirection, xDirection, yDirection + step, xDirection - step)
            nextAllB.append([form_move, nextB])
        else:
            break
        step = step + 1

    # move NW
    step = 1
    while yDirection - step >= 0 and xDirection - step >= 0:
        if board[yDirection - step][xDirection - step] == 0:
            nextB = replication(board)
            nextB[yDirection - step][xDirection - step] = p
            nextB[yDirection][xDirection] = 0
            if yDirection < 7 \
                    and xDirection < 7 \
                    and who(board[yDirection + 1][xDirection + 1]) != player \
                    and board[yDirection + 1][xDirection + 1] != 0:
                nextB[yDirection + 1][xDirection + 1] = 0
            form_move = movement_generator(yDirection, xDirection, yDirection - step, xDirection - step)
            nextAllB.append([form_move, nextB])
        else:
            break
        step = step + 1

    return nextAllB


def l_move(board, player, p, yDirection, xDirection):
    nextAllB = []

    # move E
    step = 1
    while xDirection + step <= 7:
        if board[yDirection][xDirection + step] == 0:
            nextB = replication(board)
            nextB[yDirection][xDirection + step] = p
            nextB[yDirection][xDirection] = 0
            form_move = movement_generator(yDirection, xDirection, yDirection, xDirection + step)
            nextAllB.append([form_move, nextB])
        else:
            break
        step = step + 1
    if xDirection + step < 7 and board[yDirection][xDirection + step + 1] == 0:
        if who(board[yDirection][xDirection + step]) != player \
                and board[yDirection][xDirection + step] != 0:
            nextB = replication(board)
            nextB[yDirection][xDirection + step + 1] = p
            nextB[yDirection][xDirection + step] = 0
            nextB[yDirection][xDirection] = 0
            form_move = movement_generator(yDirection, xDirection, yDirection, xDirection + step + 1)
            nextAllB.append([form_move, nextB])

    # move W
    step = 1
    while xDirection - step >= 0:
        if board[yDirection][xDirection - step] == 0:
            nextB = replication(board)
            nextB[yDirection][xDirection - step] = p
            nextB[yDirection][xDirection] = 0
            form_move = movement_generator(yDirection, xDirection, yDirection, xDirection - step)
            nextAllB.append([form_move, nextB])
        else:
            break
        step = step + 1
    if xDirection - step > 0 and board[yDirection][xDirection - step - 1] == 0:
        if who(board[yDirection][xDirection - step]) != player \
                and board[yDirection][xDirection - step] != 0:
            nextB = replication(board)
            nextB[yDirection][xDirection - step - 1] = p
            nextB[yDirection][xDirection - step] = 0
            nextB[yDirection][xDirection] = 0
            form_move = movement_generator(yDirection, xDirection, yDirection, xDirection - step - 1)
            nextAllB.append([form_move, nextB])

    # move N
    step = 1
    while yDirection + step <= 7:
        if board[yDirection + step][xDirection] == 0:
            nextB = replication(board)
            nextB[yDirection + step][xDirection] = p
            nextB[yDirection][xDirection] = 0
            form_move = movement_generator(yDirection, xDirection, yDirection + step, xDirection)
            nextAllB.append([form_move, nextB])
        else:
            break
        step = step + 1
    if yDirection + step < 7 and board[yDirection + step + 1][xDirection] == 0:
        if who(board[yDirection + step][xDirection]) != player \
                and board[yDirection + step][xDirection] != 0:
            nextB = replication(board)
            nextB[yDirection + step + 1][xDirection] = p
            nextB[yDirection + step][xDirection] = 0
            nextB[yDirection][xDirection] = 0
            form_move = movement_generator(yDirection, xDirection, yDirection + step + 1, xDirection)
            nextAllB.append([form_move, nextB])

    # move S
    step = 1
    while yDirection - step >= 0:
        if board[yDirection - step][xDirection] == 0:
            nextB = replication(board)
            nextB[yDirection - step][xDirection] = p
            nextB[yDirection][xDirection] = 0
            form_move = movement_generator(yDirection, xDirection, yDirection - step, xDirection)
            nextAllB.append([form_move, nextB])
        else:
            break
        step = step + 1
    if yDirection - step > 0 and board[yDirection - step - 1][xDirection] == 0:
        if who(board[yDirection - step][xDirection]) != player \
                and board[yDirection - step][xDirection] != 0:
            nextB = replication(board)
            nextB[yDirection - step - 1][xDirection] = p
            nextB[yDirection - step][xDirection] = 0
            nextB[yDirection][xDirection] = 0
            form_move = movement_generator(yDirection, xDirection, yDirection - step - 1, xDirection)
            nextAllB.append([form_move, nextB])

    # move SE
    step = 1
    while step + yDirection <= 7 and step + xDirection <= 7:
        if board[yDirection + step][xDirection + step] == 0:
            nextB = replication(board)
            nextB[yDirection + step][xDirection + step] = p
            nextB[yDirection][xDirection] = 0
            form_move = movement_generator(yDirection, xDirection, yDirection + step, xDirection + step)
            nextAllB.append([form_move, nextB])
        else:
            break
        step = step + 1
    if yDirection + step < 7 and xDirection + step < 7 and board[yDirection + step + 1][xDirection + step + 1] == 0:
        if who(board[yDirection + step][xDirection + step]) != player \
                and board[yDirection + step][xDirection + step] != 0:
            nextB = replication(board)
            nextB[yDirection + step + 1][xDirection + step + 1] = p
            nextB[yDirection + step][xDirection + step] = 0
            nextB[yDirection][xDirection] = 0
            form_move = movement_generator(yDirection, xDirection, yDirection + step + 1, xDirection + step + 1)
            nextAllB.append([form_move, nextB])

    # move NE
    step = 1
    while yDirection - step >= 0 and xDirection + step <= 7:
        if board[yDirection - step][xDirection + step] == 0:
            nextB = replication(board)
            nextB[yDirection - step][xDirection + step] = p
            nextB[yDirection][xDirection] = 0
            form_move = movement_generator(yDirection, xDirection, yDirection - step, xDirection + step)
            nextAllB.append([form_move, nextB])
        else:
            break
        step = step + 1
    if yDirection - step > 0 and xDirection + step < 7 and board[yDirection - step - 1][xDirection + step + 1] == 0:
        if who(board[yDirection - step][xDirection + step]) != player \
                and board[yDirection - step][xDirection + step] != 0:
            nextB = replication(board)
            nextB[yDirection - step - 1][xDirection + step + 1] = p
            nextB[yDirection - step][xDirection + step] = 0
            nextB[yDirection][xDirection] = 0
            form_move = movement_generator(yDirection, xDirection, yDirection - step - 1, xDirection + step + 1)
            nextAllB.append([form_move, nextB])

    # move SW
    step = 1
    while step + yDirection <= 7 and xDirection - step >= 0:
        if board[yDirection + step][xDirection - step] == 0:
            nextB = replication(board)
            nextB[yDirection + step][xDirection - step] = p
            nextB[yDirection][xDirection] = 0
            form_move = movement_generator(yDirection, xDirection, yDirection + step, xDirection - step)
            nextAllB.append([form_move, nextB])
        else:
            break
        step = step + 1
    if yDirection + step < 7 and xDirection - step > 0 and board[yDirection + step + 1][xDirection - step - 1] == 0:
        if who(board[yDirection + step][xDirection - step]) != player \
                and board[yDirection + step][xDirection - step] != 0:
            nextB = replication(board)
            nextB[yDirection + step + 1][xDirection - step - 1] = p
            nextB[yDirection + step][xDirection - step] = 0
            nextB[yDirection][xDirection] = 0
            form_move = movement_generator(yDirection, xDirection, yDirection + step + 1, xDirection - step - 1)
            nextAllB.append([form_move, nextB])

    # move NW
    step = 1
    while yDirection - step >= 0 and xDirection - step >= 0:
        if board[yDirection - step][xDirection - step] == 0:
            nextB = replication(board)
            nextB[yDirection - step][xDirection - step] = p
            nextB[yDirection][xDirection] = 0
            form_move = movement_generator(yDirection, xDirection, yDirection - step, xDirection - step)
            nextAllB.append([form_move, nextB])
        else:
            break
        step = step + 1
    if yDirection - step > 0 and xDirection - step > 0 and board[yDirection - step - 1][xDirection - step - 1] == 0:
        if who(board[yDirection - step][xDirection - step]) != player \
                and board[yDirection - step][xDirection - step] != 0:
            nextB = replication(board)
            nextB[yDirection - step - 1][xDirection - step - 1] = p
            nextB[yDirection - step][xDirection - step] = 0
            nextB[yDirection][xDirection] = 0
            form_move = movement_generator(yDirection, xDirection, yDirection - step - 1, xDirection - step - 1)
            nextAllB.append([form_move, nextB])

    return nextAllB


def c_move(board, player, p, yDirection, xDirection):
    nextAllB = []
    # move E
    step = 1
    while xDirection + step <= 7:
        if board[yDirection][xDirection + step] == 0:
            nextB = replication(board)
            nextB[yDirection][xDirection + step] = p
            nextB[yDirection][xDirection] = 0
            c_capture(yDirection, xDirection + step, nextB, player)
            form_move = movement_generator(yDirection, xDirection, yDirection, xDirection + step)
            nextAllB.append([form_move, nextB])
        else:
            break
        step = step + 1
    # move W
    step = 1
    while xDirection - step >= 0:
        if board[yDirection][xDirection - step] == 0:
            nextB = replication(board)
            nextB[yDirection][xDirection - step] = p
            nextB[yDirection][xDirection] = 0
            c_capture(yDirection, xDirection - step, nextB, player)
            form_move = movement_generator(yDirection, xDirection, yDirection, xDirection - step)
            nextAllB.append([form_move, nextB])
        else:
            break
        step = step + 1
    # move N
    step = 1
    while yDirection + step <= 7:
        if board[yDirection + step][xDirection] == 0:
            nextB = replication(board)
            nextB[yDirection + step][xDirection] = p
            nextB[yDirection][xDirection] = 0
            c_capture(yDirection + step, xDirection, nextB, player)
            form_move = movement_generator(yDirection, xDirection, yDirection + step, xDirection)
            nextAllB.append([form_move, nextB])
        else:
            break
        step = step + 1
    # move S
    step = 1
    while yDirection - step >= 0:
        if board[yDirection - step][xDirection] == 0:
            nextB = replication(board)
            nextB[yDirection - step][xDirection] = p
            nextB[yDirection][xDirection] = 0
            c_capture(yDirection - step, xDirection, nextB, player)
            form_move = movement_generator(yDirection, xDirection, yDirection - step, xDirection)
            nextAllB.append([form_move, nextB])
        else:
            break
        step = step + 1
    # move SE
    step = 1
    while step + yDirection <= 7 and step + xDirection <= 7:
        if board[yDirection + step][xDirection + step] == 0:
            nextB = replication(board)
            nextB[yDirection + step][xDirection + step] = p
            nextB[yDirection][xDirection] = 0
            c_capture(yDirection + step, xDirection + step, nextB, player)
            form_move = movement_generator(yDirection, xDirection, yDirection + step, xDirection + step)
            nextAllB.append([form_move, nextB])
        else:
            break
        step = step + 1
    # move NE
    step = 1
    while yDirection - step >= 0 and xDirection + step <= 7:
        if board[yDirection - step][xDirection + step] == 0:
            nextB = replication(board)
            nextB[yDirection - step][xDirection + step] = p
            nextB[yDirection][xDirection] = 0
            c_capture(yDirection - step, xDirection + step, nextB, player)
            form_move = movement_generator(yDirection, xDirection, yDirection - step, xDirection + step)
            nextAllB.append([form_move, nextB])
        else:
            break
        step = step + 1
    # move SW
    step = 1
    while step + yDirection <= 7 and xDirection - step >= 0:
        if board[yDirection + step][xDirection - step] == 0:
            nextB = replication(board)
            nextB[yDirection + step][xDirection - step] = p
            nextB[yDirection][xDirection] = 0
            c_capture(yDirection + step, xDirection - step, nextB, player)
            form_move = movement_generator(yDirection, xDirection, yDirection + step, xDirection - step)
            nextAllB.append([form_move, nextB])
        else:
            break
        step = step + 1
    # move NW
    step = 1
    while yDirection - step >= 0 and xDirection - step >= 0:
        if board[yDirection - step][xDirection - step] == 0:
            nextB = replication(board)
            nextB[yDirection - step][xDirection - step] = p
            nextB[yDirection][xDirection] = 0
            c_capture(yDirection - step, xDirection - step, nextB, player)
            form_move = movement_generator(yDirection, xDirection, yDirection - step, xDirection - step)
            nextAllB.append([form_move, nextB])
        else:
            break
        step = step + 1

    return nextAllB


def c_capture(yDirection, xDirection, board, player):
    for y in range(8):
        for x in range(8):
            current_piece = board[y][x]

            # find the k_move first, then check the diagonal
            if current_piece == player + 12:
                if who(board[yDirection][x]) != player:
                    board[yDirection][x] = 0
                if who(board[y][xDirection]) != player:
                    board[y][xDirection] = 0
    return

# freezer and imitaor move to eight direction
def freezer_or_imitator(p, yDirection, xDirection, board):
    nextAllB = []
    # move E
    step = 1
    while xDirection + step <= 7:
        if board[yDirection][xDirection + step] == 0:
            nextB = replication(board)
            nextB[yDirection][xDirection + step] = p
            nextB[yDirection][xDirection] = 0
            form_move = movement_generator(yDirection, xDirection, yDirection, xDirection + step)
            nextAllB.append([form_move, nextB])
        else:
            break
        step = step + 1
    # move W
    step = 1
    while xDirection - step >= 0:
        if board[yDirection][xDirection - step] == 0:
            nextB = replication(board)
            nextB[yDirection][xDirection - step] = p
            nextB[yDirection][xDirection] = 0
            form_move = movement_generator(yDirection, xDirection, yDirection, xDirection - step)
            nextAllB.append([form_move, nextB])
        else:
            break
        step = step + 1

    # move N
    step = 1
    while yDirection + step <= 7:
        if board[yDirection + step][xDirection] == 0:
            nextB = replication(board)
            nextB[yDirection + step][xDirection] = p
            nextB[yDirection][xDirection] = 0
            form_move = movement_generator(yDirection, xDirection, yDirection + step, xDirection)
            nextAllB.append([form_move, nextB])
        else:
            break
        step = step + 1

    # move S
    step = 1
    while yDirection - step >= 0:
        if board[yDirection - step][xDirection] == 0:
            nextB = replication(board)
            nextB[yDirection - step][xDirection] = p
            nextB[yDirection][xDirection] = 0
            form_move = movement_generator(yDirection, xDirection, yDirection - step, xDirection)
            nextAllB.append([form_move, nextB])
        else:
            break
        step = step + 1

    # move SE
    step = 1
    while step + yDirection <= 7 and step + xDirection <= 7:
        if board[yDirection + step][xDirection + step] == 0:
            nextB = replication(board)
            nextB[yDirection + step][xDirection + step] = p
            nextB[yDirection][xDirection] = 0
            form_move = movement_generator(yDirection, xDirection, yDirection + step, xDirection + step)
            nextAllB.append([form_move, nextB])
        else:
            break
        step = step + 1

    # move NE
    step = 1
    while yDirection - step >= 0 and xDirection + step <= 7:
        if board[yDirection - step][xDirection + step] == 0:
            nextB = replication(board)
            nextB[yDirection - step][xDirection + step] = p
            nextB[yDirection][xDirection] = 0
            form_move = movement_generator(yDirection, xDirection, yDirection - step, xDirection + step)
            nextAllB.append([form_move, nextB])
        else:
            break
        step = step + 1

    # move SW
    step = 1
    while step + yDirection <= 7 and xDirection - step >= 0:
        if board[yDirection + step][xDirection - step] == 0:
            nextB = replication(board)
            nextB[yDirection + step][xDirection - step] = p
            nextB[yDirection][xDirection] = 0
            form_move = movement_generator(yDirection, xDirection, yDirection + step, xDirection - step)
            nextAllB.append([form_move, nextB])
        else:
            break
        step = step + 1

    # move NW
    step = 1
    while yDirection - step >= 0 and xDirection - step >= 0:
        if board[yDirection - step][xDirection - step] == 0:
            nextB = replication(board)
            nextB[yDirection - step][xDirection - step] = p
            nextB[yDirection][xDirection] = 0
            form_move = movement_generator(yDirection, xDirection, yDirection - step, xDirection - step)
            nextAllB.append([form_move, nextB])
        else:
            break
        step = step + 1
    return nextAllB

# k_move is limited to moving exactly one square at a time
def k_move(board, player, p, yDirection, xDirection):
    succeossors = []
    neighbors = itertools.product([-1, 0, 1], [-1, 0, 1])
    for neighbor in neighbors:
        potential_enemy_r = yDirection + neighbor[0]
        potential_enemy_c = xDirection + neighbor[1]
        if 0 <= potential_enemy_r <= 7 and 0 <= potential_enemy_c <= 7:
            if board[potential_enemy_r][potential_enemy_c] == 0 \
                    or who(board[potential_enemy_r][potential_enemy_c]) != player:
                prov = replication(board)
                prov[potential_enemy_r][potential_enemy_c] = p
                prov[yDirection][xDirection] = 0
                form_move = movement_generator(yDirection, xDirection, potential_enemy_r, potential_enemy_c)
                succeossors.append([form_move, prov])
    return succeossors

# check the piece is frozen or not
def is_frozen(yDirection, xDirection, board, player):
    neighbors = itertools.product([-1, 0, 1], [-1, 0, 1])
    for neighbor in neighbors:
        potential_enemy_r = yDirection + neighbor[0]
        potential_enemy_c = xDirection + neighbor[1]
        if 0 <= potential_enemy_r <= 7 and 0 <= potential_enemy_c <= 7:
            if who(board[potential_enemy_r][potential_enemy_c]) != player \
                    and CODE_TO_INIT[board[potential_enemy_r][potential_enemy_c]].lower() == 'f':
                return True
    return False



# zobrist hash
P=2
table = []
zhash_table = {}
# assign a random number for every position in the table according to the
def init_table():
    global table
    table=[[0] * 8 for i in range(8)]
    for i in range(8):
        for j in range(8):
            piece_dic = {}
            for p in range(P):
                piece_dic[p] = random.getrandbits(64)
            table[i][j]=piece_dic

# Returns the hash value according to the a given state
def hash_state(state):
    global table
    h = 0
    board = state.board
    for i in range(8):
        for j in range(8):
            piece = board[i][j]
            if piece != 0:
                if (piece % 2) == 0:
                    h ^= table[i][j][1]
                else:
                    h ^= table[i][j][0]
    return h

# store neighbor in a list
def surrounding(state, yditection, xdirection, moves):
    neighbors = []
    for (update_r, update_c) in moves:
        n_row = yditection + update_r
        n_col = xdirection + update_c
        if n_row >= 0 and n_col >= 0 and n_row < 8 and n_col < 8:
            if state.board[n_row][n_col] != 0:
                neighbors.append(state.board[yditection + update_r][xdirection + update_c])
    return neighbors

# how many piece it can kill in one moves
def pincer_kill(state, yditection, xdirection):
    count_kill = 0
    for (update_r, update_c) in moves:

        # pincer can only move vertically and horizontally
        if update_r * update_c == 0:
            step = 1
            n_row = yditection + step*update_r
            n_col = xdirection + step*update_c
            while n_row > 0 and n_col > 0 and n_row < 7 and n_col < 7:

                # if pincer meets ally, then break
                if state.board[n_row][n_col] % 2 == state.board[yditection][xdirection] % 2:
                    break

                # meet enemy piece and behind the enemy is ally
                elif (state.board[n_row][n_col] % 2 != state.board[yditection][xdirection] % 2) \
                        & (state.board[n_row+update_r][n_col+update_c] % 2 == state.board[yditection][xdirection] % 2):
                    count_kill += 1
                    break
                step += 1
                n_row = yditection + step*update_r
                n_col = xdirection + step*update_c
    return count_kill