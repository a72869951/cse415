'''PlayerSkeletonA.py
The beginnings of an agent that might someday play Baroque Chess.

'''

import BC_state_etc as BC
import BC_checker as BC_c
import winTester as WIN
import time
from random import randint

Piece_VAL_Basic  = [0, 0, -1, 1, -2, 2, -2, 2, -2, 2, -2, 2, -100, 100, -2, 2]
Piece_VAL_Custom = [0, 0, -1, 1, -2, 2, -3, 3, -5, 5, -8, 8, -100, 100, -10, 10]
#Piece_VAL_Custom = [0, 0, -10, 10, -20, 20, -20, 20, -30, 30, -80, 80, -1000, 1000, -20, 20]

time_start = 0
time_cost = 0
time_limit = 0
N_STATES_EXPANDED = 0

# Zobrish hashing
S = 64
P = 16
zobristnum = [[0]*P for i in range(S)]

def myinit():
  global zobristnum
  for i in range(S):
    for j in range(P):
      zobristnum[i][j] = randint(0, 9999999999)

myinit()

def zhash(currentstate):
  global zobristnum
  val = 0
  k = 0
  for i in range(8):
    for j in range(8):
      piece = currentstate.board[i][j]
      val ^= zobristnum[k][piece]
  return val
val = 0
ZobrishHash = {}
ZobrishHash[val] = []

def parameterized_minimax(currentState, alphaBeta=False, ply=3,\
    useBasicStaticEval=True, useZobristHashing=False):
  '''Implement this testing function for your agent's basic
  capabilities here.'''
  global CURRENT_STATE_STATIC_VAL, N_STATES_EXPANDED
  #print(alphaBeta)
  if alphaBeta == True:
    N_STATES_EXPANDED = 1
    output_ab = alpha_Beta(currentState, ply, -float('inf'), float('inf'), currentState.whose_move, useBasicStaticEval)
    dist = {'CURRENT_STATE_STATIC_VAL':output_ab[0],'N_STATES_EXPANDED':N_STATES_EXPANDED,'N_STATIC_EVALS':output_ab[3],'N_CUTOFFS':output_ab[4],'NextState':output_ab[1],'NextMove':output_ab[2]}
    return(dist)
  else:
    output_mm = minmax(currentState, ply, currentState.whose_move, useBasicStaticEval)
    dist = {'CURRENT_STATE_STATIC_VAL':output_mm[0],'N_STATES_EXPANDED':output_mm[3],'N_STATIC_EVALS':output_mm[3],'N_CUTOFFS':output_mm[4],'NextState':output_mm[1],'NextMove':output_mm[2]}
    return(dist)

def alpha_Beta(currentState, ply, alpha, beta, maximizing, useBasicStaticEval=True):
  global time_cost, time_start, time_limit, N_STATES_EXPANDED
  if (useBasicStaticEval == True):
    current_val = basicStaticEval(currentState)
  else:
    current_val = staticEval(currentState)
  state = currentState
  moves = ((0,0),(0,0))
  if (ply == 0)or(who_win(currentState) != "No Win"):
    #print('\n1\n')
    #print([current_val,currentState,moves])
    #print(current_val)
    return([current_val,currentState,moves,1,0])
  time_cost = time.time()-time_start
  if time_cost > 0.9*time_limit:
    return([current_val,currentState,moves,1,0])
  else:
    States_moves = move(currentState)
    expanded = 1
    cutoff = 0
    N_STATES_EXPANDED += len(States_moves)
    #print('\n1\n')
    #print(States_moves)
    #print(len(States_moves))
    #time_cost = time.time()-time_start
    if (maximizing == 1):
      value = -float('inf')
      count = 0
      for State_move in States_moves:
          count += 1
          #value = max(value, alpha_Beta(child, ply - 1, alpha, beta, False, useBasicStaticEval))
          #alpha = max(alpha, value)
          child = State_move[0]
          move_next = ((State_move[1][0] ,State_move[1][1]),(State_move[2][0] ,State_move[2][1]))
          output = alpha_Beta(child, ply - 1, alpha, beta, 0, useBasicStaticEval)
          value_child = output[0]
          state_child = output[1]
          move_child = output[2]
          expanded = expanded + output[3]
          cutoff = cutoff + output[4]
          if (value < value_child)or((value == value_child)and(randint(0,1) == 0)):
            value = value_child
            state = child
            moves = move_next

          alpha = max(alpha, value)
          #if count == 100:
          #  print([alpha,beta])
          if alpha >= beta:
            cutoff = cutoff + len(States_moves) - count
            #print([alpha,beta])
            #print(value)
            #print(value_child)
            break
      return([beta,state,moves,expanded,cutoff])
    else:
        value = float('inf')
        count = 0
        for State_move in States_moves:
            count += 1
            #value = min(value, alpha_Beta(child, ply - 1, alpha, beta, True, useBasicStaticEval))
            #beta = min(beta, value)
            child = State_move[0]
            move_next = ((State_move[1][0] ,State_move[1][1]),(State_move[2][0] ,State_move[2][1]))
            output = alpha_Beta(child, ply - 1, alpha, beta, 1, useBasicStaticEval)
            value_child = output[0]
            state_child = output[1]
            move_child = output[2]
            expanded = expanded + output[3]
            cutoff = cutoff + output[4]
            if (value > value_child)or((value == value_child)and(randint(0,1) == 0)):
              value = value_child
              state = child
              moves = move_next
            beta = min(beta, value)
            if alpha >= beta:
              cutoff = cutoff + len(States_moves) - count
              break
        return([alpha,state,moves,expanded,cutoff])

def minmax(currentState, ply, maximizing = False, useBasicStaticEval=True):
  global time_cost, time_start, time_limit
  if (useBasicStaticEval == True):
    CURRENT_STATE_STATIC_VAL = basicStaticEval(currentState)
  else:
    CURRENT_STATE_STATIC_VAL = staticEval(currentState)
  state = currentState
  moves = ((0,0),(0,0))
  if (ply == 0)or(who_win(currentState) != "No Win"):
    return([CURRENT_STATE_STATIC_VAL,currentState,moves,1,0])
  time_cost = time.time()-time_start
  if time_cost > 0.85*time_limit:
    return([CURRENT_STATE_STATIC_VAL,currentState,moves,1,0])
  else:
    States_moves = move(currentState)
    expanded = 1
    if maximizing:
      value = -float('inf')
      count = 0
      for State_move in States_moves:
          count += 1
          child = State_move[0]
          move_next = ((State_move[1][0] ,State_move[1][1]),(State_move[2][0] ,State_move[2][1]))
          output = minmax(child, ply - 1, False, useBasicStaticEval)
          value_child = output[0]
          state_child = output[1]
          move_child = output[2]
          expanded = expanded + output[3]
          if (value < value_child)or((value == value_child)and(randint(0,1) == 0)):
            value = value_child
            state = child
            moves = move_next
      return([value,state,moves,expanded,0])
    else:
        value = float('inf')
        count = 0
        for State_move in States_moves:
            count += 1
            child = State_move[0]
            move_next = ((State_move[1][0] ,State_move[1][1]),(State_move[2][0] ,State_move[2][1]))
            output = minmax(child, ply - 1, True, useBasicStaticEval)
            value_child = output[0]
            state_child = output[1]
            move_child = output[2]
            expanded = expanded + output[3]
            if (value > value_child)or((value == value_child)and(randint(0,1) == 0)):
              value = value_child
              state = child
              moves = move_next
        return([value,state,moves,expanded,0])

def makeMove(currentState, currentRemark, timelimit=10):
    global time_start, time_cost, time_limit
    # Compute the new state for a move.
    # You should implement an anytime algorithm based on IDDFS.

    # The following is a placeholder that just copies the current state.
    newState = BC.BC_state(currentState.board)

    # Fix up whose turn it will be.
    newState.whose_move = 1 - currentState.whose_move
    
    # Construct a representation of the move that goes from the
    # currentState to the newState.
    # Here is a placeholder in the right format but with made-up
    # numbers:
    time_start = time.time()
    time_cost = time.time()-time_start
    time_limit = timelimit
    alphabeta = False
    depth = 0
    basicStatic = False
    ZobristH = False
    output = parameterized_minimax(currentState,alphabeta,depth,basicStatic,ZobristH)
    depth = 1
    while time_cost < timelimit*0.85:
      output_last = output
      output = parameterized_minimax(currentState,alphabeta,depth,basicStatic,ZobristH)
      depth += 1
      #time_cost = time.time()-time_start
    print('Depth = '+str(depth))
    #value = output[0]
    state = output_last['NextState']
    moves = output_last['NextMove']
    #print(state)
    #print(moves)
    print('CURRENT_STATE_STATIC_VAL = '+str(output_last['CURRENT_STATE_STATIC_VAL']))
    print('N_STATES_EXPANDED = '+str(output_last['N_STATES_EXPANDED']))
    print('N_STATIC_EVALS = '+str(output_last['N_STATIC_EVALS']))
    print('N_CUTOFFS = '+str(output_last['N_CUTOFFS']))
    #newState = BC.BC_state(state.board)
    newState = state
    

    #move = ((5,1), (6,1))

    # Make up a new remark
    newRemark = "I am ruthless and talk less,人狠话不多。"

    return [[moves, newState], newRemark]

def nickname():
    return "PrinceStephen"

def introduce():
    return "I'm PrinceStephen, a newbie Baroque Chess agent. I am created by Ye Jin and Ziyuan Wang. UW NETID yjin2 and wangzi. I am a character to play Baroque Chess."

def prepare(player2Nickname):
    ''' Here the game master will give your agent the nickname of
    the opponent agent, in case your agent can use it in some of
    the dialog responses.  Other than that, this function can be
    used for initializing data structures, if needed.'''
    return "Hello %s. Let's begin." %player2Nickname

def basicStaticEval(state):
    '''Use the simple method for state evaluation described in the spec.
    This is typically used in parameterized_minimax calls to verify
    that minimax and alpha-beta pruning work correctly.'''
    sum_val = 0
    for i in (state.board):
      for j in i:
        sum_val = sum_val + Piece_VAL_Basic[j]
    return(sum_val)

def staticEval(state):
    '''Compute a more thorough static evaluation of the given state.
    This is intended for normal competitive play.  How you design this
    function could have a significant impact on your player's ability
    to win games.'''
    sum_val = 0
    for i in (state.board):
      for j in i:
        sum_val = sum_val + Piece_VAL_Custom[j]
    return(sum_val)

def move(currentState):
  State = []
  for i in range(8):
    for j in range(8):
      if (currentState.board[i][j] % 2 == currentState.whose_move) and (currentState.board[i][j]!=0):
        if (currentState.board[i][j] == 2)or(currentState.board[i][j] == 3):
          State.extend(pawn_move(currentState,i,j))
        if (currentState.board[i][j] == 4)or(currentState.board[i][j] == 5):
          State.extend(coord_move(currentState,i,j))
        if (currentState.board[i][j] == 6)or(currentState.board[i][j] == 7):
          State.extend(leap_move(currentState,i,j))
        if (currentState.board[i][j] == 10)or(currentState.board[i][j] == 11):
          State.extend(withd_move(currentState,i,j))
        if (currentState.board[i][j] == 12)or(currentState.board[i][j] == 13):
          State.extend(king_move(currentState,i,j))
        if (currentState.board[i][j] == 14)or(currentState.board[i][j] == 15):
          State.extend(freez_move(currentState,i,j))
        if (currentState.board[i][j] == 8)or(currentState.board[i][j] == 9):
          State.extend(imit_move(currentState,i,j))
  #print(State)
  #print(len(State))
  return(State)

def pawn_move(currentState,posx,posy):
  State = []
  side = currentState.whose_move
  direction_x = [-1, 0, 1, 0]
  direction_y = [0, -1, 0, 1]
  if non_freezer(currentState,posx,posy):
    for i in range(4):
      for length in range(1,8):
        posx_new = posx + direction_x[i] * length
        posy_new = posy + direction_y[i] * length
        if outofrange(posx_new,posy_new)or(currentState.board[posx_new][posy_new] != 0):
          break
        else:
          newState = BC.BC_state(currentState.board)
          newState.whose_move = 1 - currentState.whose_move
          newState.board[posx_new][posy_new] = newState.board[posx][posy]
          newState.board[posx][posy] = 0
          for j in range(4):
            if not(outofrange(posx_new + 2*direction_x[j],posy_new + 2*direction_y[j])):
              if pawn_capture(newState,posx_new,posy_new, posx_new + direction_x[j],posy_new + direction_y[j]):
                newState.board[posx_new + direction_x[j]][posy_new + direction_y[j]] = 0
          State.append([newState, [posx, posy], [posx_new, posy_new]])
  return(State)

def coord_move(currentState,posx,posy):
  State = []
  side = currentState.whose_move
  direction_x = [-1, -1, 0, 1, 1, 1, 0, -1]
  direction_y = [0, 1, 1, 1, 0, -1, -1, -1]
  if non_freezer(currentState,posx,posy):
    for i in range(8):
      for length in range(1,8):
        posx_new = posx + direction_x[i] * length
        posy_new = posy + direction_y[i] * length
        if outofrange(posx_new,posy_new)or(currentState.board[posx_new][posy_new] != 0):
          break
        else:
          newState = BC.BC_state(currentState.board)
          newState.whose_move = 1 - currentState.whose_move
          newState.board[posx_new][posy_new] = newState.board[posx][posy]
          newState.board[posx][posy] = 0
          #Search king
          j = [j for j in newState.board if (12+side) in j][0]
          king_pos_x = newState.board.index(j)
          king_pos_y = j.index(12+side)
          if (newState.board[posx_new][king_pos_y]!=0)and(newState.board[posx_new][king_pos_y] % 2) != side:
            newState.board[posx_new][king_pos_y] = 0
          if (newState.board[posx_new][king_pos_y]!=0)and(newState.board[king_pos_x][posy_new] % 2) != side:
            newState.board[king_pos_x][posy_new] = 0
          State.append([newState, [posx, posy], [posx_new, posy_new]])
  return(State)

def leap_move(currentState,posx,posy):
  State = []
  side = currentState.whose_move
  direction_x = [-1, -1, 0, 1, 1, 1, 0, -1]
  direction_y = [0, 1, 1, 1, 0, -1, -1, -1]
  if non_freezer(currentState,posx,posy):
    for i in range(8):
      for length in range(1,8):
        posx_new = posx + direction_x[i] * length
        posy_new = posy + direction_y[i] * length
        if outofrange(posx_new,posy_new)or(sameside(currentState.board[posx_new][posy_new],currentState.board[posx][posy])):
          break
        else:
          if currentState.board[posx_new][posy_new] == 0:
            newState = BC.BC_state(currentState.board)
            newState.whose_move = 1 - currentState.whose_move
            newState.board[posx_new][posy_new] = newState.board[posx][posy]
            newState.board[posx][posy] = 0
            State.append([newState, [posx, posy], [posx_new, posy_new]])
          elif notsameside(currentState.board[posx_new][posy_new],currentState.board[posx][posy]):
            if (not(outofrange(posx_new+direction_x[i],posy_new+direction_y[i])))and(currentState.board[posx_new+direction_x[i]][posy_new+direction_y[i]]==0):
              newState = BC.BC_state(currentState.board)
              newState.whose_move = 1 - currentState.whose_move
              newState.board[posx_new+direction_x[i]][posy_new+direction_y[i]] = newState.board[posx][posy]
              newState.board[posx][posy] = 0
              newState.board[posx_new][posy_new] = 0
              posx_new = posx_new+direction_x[i]
              posy_new = posy_new+direction_y[i]
              State.append([newState, [posx, posy], [posx_new, posy_new]])
            break
  return(State)

def withd_move(currentState,posx,posy):
  State = []
  side = currentState.whose_move
  direction_x = [-1, -1, 0, 1, 1, 1, 0, -1]
  direction_y = [0, 1, 1, 1, 0, -1, -1, -1]
  if non_freezer(currentState,posx,posy):
    for i in range(8):
      for length in range(1,8):
        posx_new = posx + direction_x[i] * length
        posy_new = posy + direction_y[i] * length
        if outofrange(posx_new,posy_new)or(currentState.board[posx_new][posy_new] != 0):
          break
        else:
          newState = BC.BC_state(currentState.board)
          newState.whose_move = 1 - currentState.whose_move
          newState.board[posx_new][posy_new] = newState.board[posx][posy]
          newState.board[posx][posy] = 0
          if not(outofrange(posx+direction_x[(i+4)%8],posy+direction_y[(i+4)%8])):
            if notsameside(newState.board[posx+direction_x[(i+4)%8]][posy+direction_y[(i+4)%8]],currentState.board[posx][posy]):
              newState.board[posx+direction_x[(i+4)%8]][posy+direction_y[(i+4)%8]] = 0
          State.append([newState, [posx, posy], [posx_new, posy_new]])
  return(State)

def king_move(currentState,posx,posy):
  State = []
  side = currentState.whose_move
  direction_x = [-1, -1, 0, 1, 1, 1, 0, -1]
  direction_y = [0, 1, 1, 1, 0, -1, -1, -1]
  if non_freezer(currentState,posx,posy):
    for i in range(8):
      for length in range(1,2):
        posx_new = posx + direction_x[i] * length
        posy_new = posy + direction_y[i] * length
        if outofrange(posx_new,posy_new)or(sameside(currentState.board[posx_new][posy_new],currentState.board[posx][posy])):
          break
        else:
          newState = BC.BC_state(currentState.board)
          newState.whose_move = 1 - currentState.whose_move
          newState.board[posx_new][posy_new] = newState.board[posx][posy]
          newState.board[posx][posy] = 0
          State.append([newState, [posx, posy], [posx_new, posy_new]])
  return(State)

def freez_move(currentState,posx,posy):
  State = []
  side = currentState.whose_move
  direction_x = [-1, -1, 0, 1, 1, 1, 0, -1]
  direction_y = [0, 1, 1, 1, 0, -1, -1, -1]
  if (non_freezer(currentState,posx,posy))and(non_imitator(currentState,posx,posy)):
    for i in range(8):
      for length in range(1,8):
        posx_new = posx + direction_x[i] * length
        posy_new = posy + direction_y[i] * length
        if outofrange(posx_new,posy_new)or(currentState.board[posx_new][posy_new] != 0):
          break
        else:
          newState = BC.BC_state(currentState.board)
          newState.whose_move = 1 - currentState.whose_move
          newState.board[posx_new][posy_new] = newState.board[posx][posy]
          newState.board[posx][posy] = 0
          State.append([newState, [posx, posy], [posx_new, posy_new]])
  return(State)

def imit_move(currentState,posx,posy):
  State = []
  side = currentState.whose_move
  direction_x = [-1, -1, 0, 1, 1, 1, 0, -1]
  direction_y = [0, 1, 1, 1, 0, -1, -1, -1]
  if non_freezer(currentState,posx,posy):
    for i in range(8):
      for length in range(1,8):
        posx_new = posx + direction_x[i] * length
        posy_new = posy + direction_y[i] * length
        if (outofrange(posx_new,posy_new))or(sameside(currentState.board[posx_new][posy_new],currentState.board[posx][posy])):
          #print('\n'+str(i)+'\n')
          break
        else:
          if (currentState.board[posx_new][posy_new] == 0):
            eat = False
            if not(outofrange(posx+direction_x[(i+4)%8],posy+direction_y[(i+4)%8])):
              if (currentState.board[posx+direction_x[(i+4)%8]][posy+direction_y[(i+4)%8]] == BC.WHITE_WITHDRAWER - side):
                #eat the withdrawer
                newState = BC.BC_state(currentState.board)
                newState.whose_move = 1 - currentState.whose_move
                newState.board[posx_new][posy_new] = newState.board[posx][posy]
                newState.board[posx][posy] = 0
                newState.board[posx+direction_x[(i+4)%8]][posy+direction_y[(i+4)%8]] = 0
                State.append([newState, [posx, posy], [posx_new, posy_new]])
                eat = True
            if ((direction_x[i] == 0)or(direction_y[i] == 0)):
              eat_pincer = False
              for j in range(8):
                if ((direction_x[j] == 0)or(direction_y[j] == 0)):
                  cap_x = posx_new + direction_x[j]
                  cap_y = posy_new + direction_y[j]
                  coop_x = posx_new + 2*direction_x[j]
                  coop_y = posy_new + 2*direction_y[j]
                  if (not(outofrange(coop_x,coop_y)))and(currentState.board[cap_x][cap_y] == BC.WHITE_PINCER - side)and(sameside(currentState.board[coop_x][coop_y],currentState.board[posx][posy])):
                    #eat the pawn
                    if eat_pincer == False:
                      newState = BC.BC_state(currentState.board)
                      newState.whose_move = 1 - currentState.whose_move
                      newState.board[posx_new][posy_new] = newState.board[posx][posy]
                      newState.board[posx][posy] = 0
                    newState.board[cap_x][cap_y] = 0
                    eat_pincer = True
                    eat = True
              if eat_pincer == True:
                State.append([newState, [posx, posy], [posx_new, posy_new]])
            j = [j for j in currentState.board if (12+side) in j][0]
            king_pos_x = currentState.board.index(j)
            king_pos_y = j.index(12+side)
            if (currentState.board[posx_new][king_pos_y] == BC.WHITE_COORDINATOR - side)or(currentState.board[king_pos_x][posy_new] == BC.WHITE_COORDINATOR - side):
              #eat the coordinator
              newState = BC.BC_state(currentState.board)
              newState.whose_move = 1 - currentState.whose_move
              newState.board[posx_new][posy_new] = newState.board[posx][posy]
              newState.board[posx][posy] = 0
              if newState.board[posx_new][king_pos_y] == BC.WHITE_COORDINATOR - side:
                newState.board[posx_new][king_pos_y] = 0
              if newState.board[king_pos_x][posy_new] == BC.WHITE_COORDINATOR - side:
                newState.board[king_pos_x][posy_new] = 0
              eat = True
              State.append([newState, [posx, posy], [posx_new, posy_new]])
            if eat == False:
              newState = BC.BC_state(currentState.board)
              newState.whose_move = 1 - currentState.whose_move
              newState.board[posx_new][posy_new] = newState.board[posx][posy]
              newState.board[posx][posy] = 0
              State.append([newState, [posx, posy], [posx_new, posy_new]])
          elif (currentState.board[posx_new][posy_new] == BC.WHITE_KING - side)and(length == 1):
              #eat the king
              newState = BC.BC_state(currentState.board)
              newState.whose_move = 1 - currentState.whose_move
              newState.board[posx_new][posy_new] = newState.board[posx][posy]
              newState.board[posx][posy] = 0
              State.append([newState, [posx, posy], [posx_new, posy_new]])
              eat = True
              break
          elif (currentState.board[posx_new][posy_new] == BC.WHITE_LEAPER-side)and(not(outofrange(posx_new + direction_x[i],posy_new + direction_y[i]))):
            if currentState.board[posx_new + direction_x[i]][posy_new + direction_y[i]] == 0:
              #eat the leaper
              newState = BC.BC_state(currentState.board)
              newState.whose_move = 1 - currentState.whose_move
              newState.board[posx_new + direction_x[i]][posy_new + direction_y[i]] = newState.board[posx][posy]
              newState.board[posx][posy] = 0
              newState.board[posx_new][posy_new] = 0
              State.append([newState, [posx, posy], [posx_new + direction_x[i], posy_new + direction_y[i]]])
            else:
              break
          else:
            break
  #print(State)
  return(State)          

def D2toD1(l):
  new_l = []
  for l1 in l:
    for l2 in l1:
      new_l.append(l2)
  return new_l

def non_freezer(currentState, posx, posy):
  direction_x = [-1, -1, -1, 0, 1, 1, 1, 0]
  direction_y = [-1, 0, 1, 1, 1, 0, -1, -1]
  side = currentState.whose_move
  for i in range(8):
    if not(outofrange(posx+direction_x[i], posy+direction_y[i])):
      if currentState.board[posx+direction_x[i]][posy+direction_y[i]] == (15 - side):
        return(False)
  return(True)

def non_imitator(currentState,posx,posy):
  direction_x = [-1, -1, -1, 0, 1, 1, 1, 0]
  direction_y = [-1, 0, 1, 1, 1, 0, -1, -1]
  side = currentState.whose_move
  for i in range(8):
    if not(outofrange(posx+direction_x[i], posy+direction_y[i])):
      if currentState.board[posx+direction_x[i]][posy+direction_y[i]] == (9 - side):
        return(False)
  return(True)

def nearby(currentState,posx,posy,piece):
  direction_x = [-1, -1, -1, 0, 1, 1, 1, 0]
  direction_y = [-1, 0, 1, 1, 1, 0, -1, -1]
  side = currentState.whose_move
  for i in range(8):
    if not(outofrange(posx+direction_x[i], posy+direction_y[i])):
      if currentState.board[posx+direction_x[i]][posy+direction_y[i]] == (piece - side):
        return(True)
  return(False)

def pawn_capture(currentState, posx, posy, pos_cap_x, pos_cap_y):
  side = 1 - currentState.whose_move
  cap = currentState.board[pos_cap_x][pos_cap_y]
  coop = currentState.board[pos_cap_x*2 - posx][pos_cap_y*2 - posy]
  if sameside(currentState.board[posx][posy], coop)and(notsameside(currentState.board[posx][posy], cap)):
    return(True)
  else:
    return(False)
  
def outofrange(posx,posy):
  if (posx > 7)or(posx < 0)or(posy > 7)or(posy < 0):
    return True
  else:
    return False

def sameside(a,b):
  if (a != 0)and(b != 0):
    if (a % 2) == (b % 2):
      return(True)
    else:
      return(False)
  else:
    return(False)

def notsameside(a,b):
  if (a != 0)and(b != 0):
    if (a % 2) != (b % 2):
      return(True)
    else:
      return(False)
  else:
    return(False)

def who_win(currentState):
  possibleWin = "No Win"
  black_king_detected = False
  white_king_detected = False
  for i in range(8):
    for j in range(8):
      if currentState.board[i][j] == BC.BLACK_KING: black_king_detected = True
      if currentState.board[i][j] == BC.WHITE_KING: white_king_detected = True
  if white_king_detected and not black_king_detected: possibleWin = "Win for WHITE"
  if black_king_detected and not white_king_detected: possibleWin = "Win for BLACK"
  return possibleWin