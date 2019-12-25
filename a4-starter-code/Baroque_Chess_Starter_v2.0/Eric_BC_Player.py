'''PlayerSkeletonA.py
The beginnings of an agent that might someday play Baroque Chess.
'''

import BC_state_etc as BC
import random
import time
from datetime import datetime, timedelta
import math
import heapq


BEST_STATE = None
TIME_LIMIT_OFFSET = 0.1
LAST_MOVE = [-1, -1, -1] # Piece, col, row
CUTOFFS = 0
COUNT = 0
CURRENT_STATE_STATIC_VAL = 0
N_STATIC_EVALS = 0
OPP_NAME = None

BLACK = 0
WHITE = 1
NORTH = 0; SOUTH = 1; WEST = 2; EAST = 3; NW = 4; NE = 5; SW = 6; SE = 7

# Used in parsing the initial state and in testing:

INIT_TO_CODE = {'p':2, 'P':3, 'c':4, 'C':5, 'l':6, 'L':7, 'i':8, 'I':9,
  'w':10, 'W':11, 'k':12, 'K':13, 'f':14, 'F':15, '-':0}

# Used in printing out states:

CODE_TO_INIT = {0:'-',2:'p',3:'P',4:'c',5:'C',6:'l',7:'L',8:'i',9:'I',
  10:'w',11:'W',12:'k',13:'K',14:'f',15:'F'}

# Global variables representing the various types of pieces on the board:

BLACK_PINCER      = 2
BLACK_COORDINATOR = 4
BLACK_LEAPER      = 6
BLACK_IMITATOR    = 8
BLACK_WITHDRAWER  = 10
BLACK_KING        = 12
BLACK_FREEZER     = 14

WHITE_PINCER      = 3
WHITE_COORDINATOR = 5
WHITE_LEAPER      = 7
WHITE_IMITATOR    = 9
WHITE_WITHDRAWER  = 11
WHITE_KING        = 13
WHITE_FREEZER     = 15

# Initialize zobrist hasing table
ZOBRIST_N = []
ZOBRIST_M = {}
random.seed(0)
for x in range(64):
  ZOBRIST_N.append([])
  for y in range(16):
    ZOBRIST_N[x].append(random.randint(0, 2**64))

def who(piece): return piece % 2  # BLACK's pieces are even; WHITE's are odd.

def parse(bs): # bs is board string
  '''Translate a board string into the list of lists representation.'''
  b = [[0,0,0,0,0,0,0,0] for r in range(8)]
  rs9 = bs.split("\n")
  rs8 = rs9[1:] # eliminate the empty first item.
  for iy in range(8):
    rss = rs8[iy].split(' ');
    for jx in range(8):
      b[iy][jx] = INIT_TO_CODE[rss[jx]]
  return b

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

INITIAL_2 = parse('''
c l i w k i l f 
p - - p - p p p 
- - I - - - - P 
P - P - - - - C 
- - - - - L - - 
F - - - - - P - 
- P - P P P - - 
- L I W K - - -
''')

INITIAL_3 = parse('''
c l p p - i - k 
p i - P - p - p 
- - - - - - f - 
- p P - - P w P 
- - - - - - - - 
- P - - - - - P 
- - P - K P - C 
F L I W - I - - 
''')

INITIAL_4 = parse('''
c l - - k i - - 
p i - p - p - p 
- p p P - - f - 
- - P - - P w P 
- - - - - - - - 
- P - - - - - P 
- - P - K P - C 
F L I W - I - -
''')


class State:
    def __init__(self, old_board=INITIAL, whose_move=WHITE, kingPos=[], frozen=[]):
        self.whose_move = whose_move;
        self.board = [r[:] for r in old_board]
        if len(kingPos) == 0: self.kingPos = king_search(old_board)
        else: self.kingPos = [(k[0], k[1]) for k in kingPos]
        if len(frozen) == 0: self.frozen = freezer_search(old_board, whose_move)
        else: self.frozen = [[(f[0], f[1]) for f in i] for i in frozen]
        self.eval = None
        self.move_start_sq = None
        self.move_end_sq = None

    def __repr__(self):
        s = ''
        for r in range(8):
            for c in range(8):
                s += CODE_TO_INIT[self.board[r][c]] + " "
            s += "\n"
        if self.whose_move==WHITE: s += "WHITE's move"
        else: s += "BLACK's move"
        s += "\n"
        return s

    def __copy__(self):
        new_state = State(self.board, self.whose_move,
            self.kingPos, self.frozen)
        new_state.move_start_sq = self.move_start_sq
        new_state.move_end_sq = self.move_end_sq
        return new_state

    def __eq__(self, other):
        if isinstance(other, State):
            for i in range(0, len(self.board)):
                if self.board[i] != other.board[i]: return False
            return True
        return False

    def __lt__(self, other):
        if self.whose_move == WHITE:
           lt = staticEval(self) > staticEval(other)
        else:
            lt = staticEval(self) < staticEval(other)
        return lt

    def self_static_eval(self):
        if self.eval == None:
            self.eval = staticEval(self)
        return self.eval

class minimax_tree_node:
  def __init__(self, state):
    self.state = state
    self.children = []

# def saveLastMove(parent, child):
#   p_board = parent.board
#   c_board = child.board
#   for x in range(0, len(p_board)):
#     for y in range(0, len(p_board)):
#       if c_board[x][y] != p_board[x][y] and c_board == 0 and who(p_board[x][y]) == parent.whose_move:
#         LAST_MOVE[0] = p_board[x][y]
#         LAST_MOVE[1] = x
#         LAST_MOVE[2] = y

def parameterized_minimax(currentState, ply=3, alphaBeta=True,\
    useBasicStaticEval=True, useZobristHashing=True):
  '''Implement this testing function for your agent's basic
  capabilities here.'''
  global N_STATIC_EVALS
  global COUNT
  global CURRENT_STATE_STATIC_VAL
  
  CURRENT_STATE_STATIC_VAL = basicStaticEval(currentState)
  now = datetime.now()
  depth = 0
  best = None
  endTime = now + timedelta(0, 1)
  min_or_max = -1 if currentState.whose_move == BLACK else 1
  while datetime.now() < endTime or depth <= ply:
    depth += 1
    best_state = minimax(currentState, depth, min_or_max, endTime, alphaBeta, useZobristHashing)
    if best_state != None:
      best = best_state
    else:
      break
  N_STATIC_EVALS = best.self_static_eval()
  return {'CURRENT_STATE_STATIC_VAL':CURRENT_STATE_STATIC_VAL, 'N_STATES_EXPANDED':COUNT, 'N_STATIC_EVALS':N_STATIC_EVALS, 'N_CUTOFFS':CUTOFFS}


def makeMove(currentState, currentRemark, timelimit=10):
    global OPP_NAME
    global COUNT
    # Compute the new state for a move.
    # You should implement an anytime algorithm based on IDDFS.
    now = datetime.now()
    global BEST_STATE
    global CUTOFFS

    # The following is a placeholder that just copies the current state.
    newState = State(currentState.board, currentState.whose_move)
    resultState = iter_deep_search(newState, now + timedelta(0, timelimit))
    move = (resultState.move_start_sq, resultState.move_end_sq)
    value = resultState.eval
    REMARK = ["My turn, I choose my move here", "I'll think harder in some future game. Here's my move", "I think it will be a interesting move",\
  "It is easy for me to do that", "I think I'm getting closer to win", "Hi "+str(OPP_NAME)+", I think we will have a great game", "I WILL NEVER SURRENDER",\
    "My precise evaluation function value of "+str(value)+" is impeccable", "It is interesting to choose the best one from "+str(COUNT)+" choices",\
      "It is easy for me to make choice by making "+str(CUTOFFS)+" times alpha-beta pruning"]

    # Make up a new remark
    newRemark = random.choice(REMARK)

    return [[move, resultState], newRemark]

def iter_deep_search(currentState, endTime):
  depth = 0
  best = None
  min_or_max = -1 if currentState.whose_move == BLACK else 1
  while datetime.now() < endTime:
    depth += 1
    best_state = minimax(currentState, depth, min_or_max, endTime)
    if best_state != None:
      best = best_state
    else:
      break
  return best

def is_over_time(endTime):
  global TIME_LIMIT_OFFSET
  now = datetime.now()
  return (now + timedelta(0, TIME_LIMIT_OFFSET)) >= endTime

def minimax_helper(ori_state, state, depth, min_or_max, endTime, alpha, beta, alphaBeta=True, useZobristHashing=True):
  global ZOBRIST_M
  global CUTOFFS 
  global COUNT
  ori_state = ori_state

  if is_over_time(endTime):
    return None

  if depth == 0:
    state.self_static_eval()
    return state
  
  state.self_static_eval()
  board = state.board
  child_states = []
  s_hashcode = getHashCode(board)
  time.sleep(0.1)
  if useZobristHashing:
    s_node = ZOBRIST_M.get(s_hashcode, minimax_tree_node(state))
  else:
    s_node = minimax_tree_node(state)

  if len(s_node.children) == 0:
    child_states = getChildStates(state, s_hashcode)
    for c in child_states:
      # if c.whose_move == (1-ori_state.whose_move) and c.board != ori_state.board:
      c_hashcode = getHashCode(c.board)
      s_node.children.append(c_hashcode)
      ZOBRIST_M[c_hashcode] = minimax_tree_node(c)
    ZOBRIST_M[s_hashcode] = s_node
  else:
    for c_hashcode in s_node.children:
      # if ZOBRIST_M[c_hashcode].state.whose_move == (1-ori_state.whose_move) and (ZOBRIST_M[c_hashcode].state.board!=ori_state.board):
      child_states.append(ZOBRIST_M[c_hashcode].state)
  
  heapq.heapify(child_states)

  best = None
  best_eval = 0

  while len(child_states) != 0:
    c_state = heapq.heappop(child_states)

    if is_over_time(endTime):
      break
    
    if alpha >= beta:
      CUTOFFS+=1
      break

    new_state = minimax_helper(ori_state, c_state, depth-1, -min_or_max, endTime, alpha, beta, alphaBeta)
    if new_state != None:
      new_eval = new_state.eval
      COUNT+=1
    else:
      new_eval = 0
    
    if best == None:
      best = new_state
      best_eval = new_eval
    elif min_or_max*new_eval >= min_or_max*best_eval:
      best = new_state
      best_eval = new_eval
    
    if min_or_max == 1 and alphaBeta:
      alpha = max(alpha, new_eval)
    elif alphaBeta:
      beta = min(beta, new_eval)

  # print('best_minimaxhelper_return')
  # print(best)
  return best

def minimax(state, depth, min_or_max, endTime, alphaBeta=True, useZobristHashing=True):
  global CUTOFFS, COUNT
  ori_state = state
  s_hashcode = getHashCode(state.board)
  child_states = []
  if useZobristHashing:
    s_node = ZOBRIST_M.get(s_hashcode, minimax_tree_node(state))
  else:
    s_node = minimax_tree_node(state)

  if len(s_node.children) == 0:
    child_states = getChildStates(state, s_hashcode)
    for c in child_states:
      if c.whose_move == (1-ori_state.whose_move) and c.board != ori_state.board:
        c_hashcode = getHashCode(c.board)
        s_node.children.append(c_hashcode)
        c.self_static_eval()
        ZOBRIST_M[c_hashcode] = minimax_tree_node(c)
    ZOBRIST_M[s_hashcode] = s_node
  else:
    for c_hashcode in s_node.children:
      if ZOBRIST_M[c_hashcode].state.whose_move == (1-ori_state.whose_move) and ZOBRIST_M[c_hashcode].state.board!=ori_state.board:
        child_states.append(ZOBRIST_M[c_hashcode].state)
  
  heapq.heapify(child_states)

  best = None
  best_eval = 0
  alpha = -math.inf
  beta = math.inf
  
  while len(child_states) != 0:
    c_state = heapq.heappop(child_states)
    # print('c_state in minimax loop')
    # print(c_state)

    if is_over_time(endTime):
      best10 = child_states[0:10]
      best = random.choice(best10)
      break
    
    if alpha >= beta:
      CUTOFFS+=1
      best10 = child_states[0:10]
      best = random.choice(best10)
      break
    
    new_state = minimax_helper(ori_state, c_state, depth-1, -min_or_max, endTime, alpha, beta, alphaBeta, useZobristHashing)
    
    if new_state != None:
      new_eval = new_state.eval
      COUNT+=1
    else:
      new_eval = 0
    
    if min_or_max == 1 and alphaBeta:
      alpha = max(alpha, new_eval)
    elif alphaBeta:
      beta = min(beta, new_eval)
    
    if best == None or min_or_max*new_eval >= min_or_max*best_eval:
      best = c_state
      best_eval = new_eval

  return best


def getHashCode(board):
  val = 0
  for x in range(8):
    for y in range(8):
      piece = board[x][y]
      if piece != 0:
        val ^= ZOBRIST_N[8*x+y][piece]
  return val

def getChildStates(state, hashCode):
  board = state.board
  child_states = []
  for x in range(0, len(board)):
    for y in range(0, len(board)):
      # Get current piece number
      piece = board[x][y]
      # if current player is the same color as the piece get all child states
      if piece != 0 and who(piece) == state.whose_move:
        child_states += move(state, hashCode, x, y)

  return child_states

vec = [(0,1), (0,-1), (1,0), (-1,0), (1,1), (-1,-1), (1,-1), (-1,1)]

def king_search(board):
  wKingPiece = None
  bKingPiece = None
  for i in range(0, len(board)):
    for j in range(0, len(board[i])):
      if board[i][j] == INIT_TO_CODE['K']:
        wKingPiece = (i, j)
      elif board[i][j] == INIT_TO_CODE['k']:
        bKingPiece = (i, j)
  return [wKingPiece, bKingPiece]

def freezer_search(board, whose_move):
  frozen = [[],[]]
  for x in range(0, len(board)):
    for y in range(0, len(board[x])):
      if board[x][y] - who(board[x][y]) == INIT_TO_CODE['f']:
        for i, j in vec:
          if x+i >= 0 and y+j >= 0 and x+i <= 7 and y+j <= 7:
            frozen[who(board[x][y])].append((x+i, y+j))
  return frozen

def move(state, z_hash, xPos, yPos):
  # Check if piece is frozen by opponent's freezer
  if (xPos, yPos) in state.frozen[1-state.whose_move]:
    return []
  
  child_states = []
  piece = state.board[xPos][yPos]
  piece_t = piece - who(piece)

  directions = vec[0:4] if piece_t == INIT_TO_CODE['p'] else vec
  for i, j in directions:
    x = xPos
    y = yPos
    # Don't move pieces off the board or into another piece
    while x+i >= 0 and y+j >= 0 and x+i <= 7 and y+j <= 7 and (state.board[x+i][y+j] == 0 or piece_t == INIT_TO_CODE['k']):

      if piece_t != INIT_TO_CODE['k']:
        x += i
        y += j 
      
      if piece == LAST_MOVE[0] and x == LAST_MOVE[1] and y == LAST_MOVE[2] and piece_t != INIT_TO_CODE['k']:
        continue
      
      # copy old state move
      c_state = state.__copy__()
      c_state.whose_move = 1 - c_state.whose_move
      # c_state.move_start_sq = (xPos, yPos)
      # print(c_state.whose_move)
      # print(c_state)

      # pick up piece for move
      c_state.board[xPos][yPos] = 0 # Clear old position
      c_state.board[x][y] = piece # Move to new position
      c_state.move_start_sq = (xPos, yPos)
      c_state.move_end_sq = (x, y)
      z_h = z_hash
      z_h ^= ZOBRIST_N[8*xPos+yPos][c_state.board[xPos][yPos]]
      z_h ^= ZOBRIST_N[8*x+y][c_state.board[x][y]]
      if piece_t == INIT_TO_CODE['p']: # if piece is pincer
        child_states.append(pincer_capture(c_state, x, y, z_h))
      elif piece_t == INIT_TO_CODE['c']: # if piece is coordinator
        child_states.append(coordinator_capture(c_state, x, y, z_h))
      elif piece_t == INIT_TO_CODE['f']: # if piece is freezer
        child_states.append(freezer_capture(c_state, x, y, z_h))
      elif piece_t == INIT_TO_CODE['l']: # if piece is leaper
        child_states.append(leaper_capture(c_state, x, y, i, j, z_h))
      elif piece_t == INIT_TO_CODE['i']: # if piece is imitator
        child_states.extend(imitator_capture(c_state,x,y,xPos,yPos,i,j,z_h))
      elif piece_t == INIT_TO_CODE['w']: # if piece is withdrawer
        child_states.append(withdrawer_capture(c_state, xPos-i, yPos-j, x, y, z_h))
      elif piece_t == INIT_TO_CODE['k']: # if piece is king
        child_states.append(king_capture(c_state, x, y, x+i, y+j, z_h))
      if piece_t == INIT_TO_CODE['k']:
        break
  
  return child_states



def pincer_capture(state, x, y, z_h):
    global ZOBRIST_M
    piece = state.board[x][y]
    # search surrounding spaces to look for a capture
    for i, j in vec[0:4]:
        if is_on_board(x, y) and is_on_board(x+i, y+j) and is_on_board(x+2*i, y+2*j)\
                and who(state.board[x+i][y+j]) != who(piece) \
                and state.board[x+2*i][y+2*j] == piece:
            z_h ^= ZOBRIST_N[8*(x+i)+y+j][state.board[x+i][y+j]]
            state.board[x+i][y+j] = 0
    state.self_static_eval()
    state.move_end_sq = (x,y)
    ZOBRIST_M[z_h] = minimax_tree_node(state)
    # print("pincher hash", z_h)
    return state

def coordinator_capture(state, x, y, z_h):
    global ZOBRIST_M
    kx, ky = state.kingPos[state.whose_move]
    # try to coordinate with king to capture
    if is_on_board(x,y) and is_on_board(x, ky)\
            and who(state.board[x][y]) != who(state.board[x][ky]):
        z_h ^= ZOBRIST_N[8*x+ky][state.board[x][ky]]
        state.board[x][ky] = 0
    if is_on_board(x,y) and is_on_board(kx, y)\
            and who(state.board[x][y]) != who(state.board[kx][y]):
        z_h ^= ZOBRIST_N[8*kx+y][state.board[kx][y]]
        state.board[kx][y] = 0
    state.self_static_eval()
    state.move_end_sq = (x,y)
    ZOBRIST_M[z_h] = minimax_tree_node(state)
    return state

def freezer_capture(state, x, y, z_h):
    global ZOBRIST_M
    state.frozen[state.whose_move] = []
    for i, j in vec:
        if is_on_board(x+i, y+j):
            state.frozen[state.whose_move].append((x+i,y+j))
    state.self_static_eval()
    state.move_end_sq = (x,y)
    ZOBRIST_M[z_h] = minimax_tree_node(state)
    return state

def leaper_capture(state, x, y, i, j, z_h):
    global ZOBRIST_M
    state.move_end_sq = (x,y)
    if is_on_board(x,y) and is_on_board(x+i, y+j) and is_on_board(x+2*i,y+2*j)\
            and who(state.board[x+i][y+j]) != who(state.board[x][y]) \
            and state.board[x+i][y+j] != 0 and state.board[x+2*i][y+2*j] == 0:
        z_h ^= ZOBRIST_N[8*(x+2*i)+(y+2*j)][state.board[x][y]]
        z_h ^= ZOBRIST_N[8*x+y][state.board[x][y]]
        z_h ^= ZOBRIST_N[8*(x+i)+y+j][state.board[x+i][y+j]]
        state.board[x+2*i][y+2*j] = state.board[x][y]
        state.board[x][y] = 0
        state.board[x+i][y+j] = 0
        state.move_end_sq = (x+2*i,y+2*i)
    state.self_static_eval()
    ZOBRIST_M[z_h] = minimax_tree_node(state)
    return state

def imitator_capture(state, x, y, x0, y0, i, j, z_h):
    global ZOBRIST_M

    captures = []
    if is_on_board(x,y):
        # # imitate pincher
        p_cap = state.__copy__()
        for i, j in vec[0:4]:
            if is_on_board(x+i, y+j) and is_on_board(x+2*i, y+2*j)\
                    and state.board[x+i][y+j] - state.whose_move == INIT_TO_CODE['p'] \
                    and state.board[x+2*i][y+2*j] + state.whose_move == INIT_TO_CODE['P'] and ((x-x0, y-y0) in vec[0:4]):
                p_cap.board[x+i][y+j] = 0
                p_cap.move_end_sq = (x,y)
                captures.append(p_cap)

        # imitate coordinator
        kx, ky = state.kingPos[state.whose_move]
        k_cap = state.__copy__()
        k_bool = False
        if is_on_board(x, ky) \
                and who(state.board[x][y]) != who(state.board[x][ky]) \
                and state.board[x][ky] - state.whose_move == INIT_TO_CODE['c']:
            k_cap.board[x][ky] = 0
            k_cap.move_end_sq = (x,y)
            k_bool = True
        if is_on_board(kx, y)\
                and who(state.board[x][y]) != who(state.board[kx][y]) \
                and state.board[kx][y] - state.whose_move == INIT_TO_CODE['c']:
            k_cap.board[kx][y] = 0
            k_cap.move_end_sq = (x,y)
            k_bool = True

        if k_bool:
            captures.append(k_cap)

        # imitate freezer
        f_cap = state.__copy__()
        f_bool = False
        for i, j in vec:
            if is_on_board(x+i, y+j):
                if state.board[x+i][y+j] - state.whose_move == INIT_TO_CODE['f']:
                    f_bool = True
                f_cap.frozen[state.whose_move].append((x + i,y + j))
                f_cap.move_end_sq = (x,y)
        if f_bool:
            captures.append(f_cap)

        # imitate withdrawer
        w_cap = state.__copy__()
        if is_on_board(x0-i, y0-j)\
                and state.board[x0-i][y0-j] - state.whose_move == INIT_TO_CODE['w']:
            w_cap.board[x0-i][y0-j] = 0
            w_cap.move_end_sq = (x,y)
            captures.append(w_cap)         
    return captures

def withdrawer_capture(state, x, y, x1, y1, z_h):
    global ZOBRIST_M
    if is_on_board(x, y) and who(state.board[x][y])!= who(state.board[x1][y1]):
        z_h ^= ZOBRIST_N[8*x+y][state.board[x][y]]
        state.board[x][y] = 0
    state.self_static_eval()
    state.move_end_sq = (x1,y1)
    ZOBRIST_M[z_h] = minimax_tree_node(state)
    return state

def king_capture(state, x, y, x1, y1, z_h):
    global ZOBRIST_M
    if is_on_board(x,y) and is_on_board(x1, y1)\
            and (who(state.board[x1][y1]) != who(state.board[x][y]) \
            or state.board[x1][y1] == 0):
        if state.board[x1][y1] != 0:
            z_h ^= ZOBRIST_N[8*x1+y1][state.board[x1][y1]]
        z_h ^= ZOBRIST_N[8*x1+y1][state.board[x][y]]
        z_h ^= ZOBRIST_N[8*x+y][state.board[x][y]]
        state.board[x1][y1] = state.board[x][y]
        state.board[x][y] = 0
        state.kingPos[state.whose_move] = (x1, y1)
        state.self_static_eval()
        state.move_end_sq = (x1,y1)
        ZOBRIST_M[z_h] = minimax_tree_node(state)
    return state

def is_on_board(x,y):
    return x >= 0 and y >= 0 and x <= 7 and y <= 7

def nickname():
    return "Eric"

def introduce():
    return "I'm Eric, a Baroque Chess agent rookie."

def prepare(player2Nickname):
    ''' Here the game master will give your agent the nickname of
    the opponent agent, in case your agent can use it in some of
    the dialog responses.  Other than that, this function can be
    used for initializing data structures, if needed.'''
    global OPP_NAME
    OPP_NAME = player2Nickname
    pass


PIECE_VALS = [0,0,-1,1,-2,2,-5,5,-7,7,-8,8,-100,100,-3,3]


def basicStaticEval(state):
    '''Use the simple method for state evaluation described in the spec.
    This is typically used in parameterized_minimax calls to verify
    that minimax and alpha-beta pruning work correctly.'''
    return sum([sum([PIECE_VALS[j] for j in i]) for i in state.board])

def staticEval(state):
    '''Compute a more thorough static evaluation of the given state.
    This is intended for normal competitive play.  How you design this
    function could have a significant impact on your player's ability
    to win games.'''
    return sum([sum([PIECE_VALS[j] for j in i]) for i in state.board])

if __name__ == "__main__":
    state = State(old_board=INITIAL_2, whose_move=BLACK)

    print('start_state: \n')
    print(state)
    best_state=parameterized_minimax(state, 3, alphaBeta=True, useBasicStaticEval=True, useZobristHashing=True)
    print(best_state)

    # now = datetime.now()
    # new_state = iter_deep_search(state, now + timedelta(0, 10))

    # print(new_state)

