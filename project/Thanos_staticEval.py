importance = {'living_reward':5, 'freezing_reward':1, 'killing_reward':4, 'king_guard':4}
moves = [(1,-1), (1,1), (-1,1), (-1,-1),(0,1), (1,0), (-1,0), (0,-1)]
advanced_static_value = {0:0, 1:1, 2:5, 3:5, 4:5, 5:2, 6:100, 7:8}

def static_eval(state):
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
            
    if enemy_king_down:
        return 100000

    return ally_points + enemy_points

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