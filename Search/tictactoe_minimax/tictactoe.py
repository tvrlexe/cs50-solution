"""
Tic Tac Toe Player
"""


import copy

X = "X"
O = "O"
EMPTY = None


def initial_state():
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    count_x=0
    count_o=0
    for i in range(len(board)):
        for j in range(len(board[0])):
            if board[i][j] == X:
                count_x+=1
            elif board[i][j] == O:
                count_o+=1
    if count_x>count_o:
        return O
    else:
        return X


def actions(board):
    action = []
    for i in range(len(board)):
        for j in range(len(board[0])):
            if board[i][j] == EMPTY:
                action.append((i,j))
    return action



def result(board, action):
    i,j=action
    if board[i][j] is not EMPTY:
        raise ValueError("Invalid move")
    new_board = copy.deepcopy(board)
    new_board[i][j] = player(board)
    return new_board




def winner(board):
    for row in board:
        if row[0] == row[1] == row[2] and row[0] is not None:
            return row[0]
    for i in range(3):
        if board[0][i] == board[1][i] == board[2][i] and board[0][i] is not None:
            return board[0][i]
    if board[0][0] == board[1][1] == board[2][2] and board[0][0] is not None:
        return board[0][0]
    if board[0][2] == board[1][1] == board[2][0] and board[0][2] is not None:
        return board[0][2]
    return None


def terminal(board):
    if winner(board):
        return True
    for row in board:
        for i in range(3):
            if row[i] == EMPTY:
                return False
    return True

def utility(board):
    if winner(board) == X:
        return 1
    elif winner(board) == O:
        return -1
    elif terminal(board):
        return 0



def minimax(board):
    if terminal(board):
        return None

    best_move = None
    if player(board) == X:
        best_score = float('-inf')
        for action in actions(board):
            score = min_value(result(board, action))
            if score > best_score:
                best_score = score
                best_move = action
    else:
        best_score = float('inf')
        for action in actions(board):
            score = max_value(result(board, action))
            if score < best_score:
                best_score = score
                best_move = action

    return best_move




def max_value(board):
    if terminal(board):
        return utility(board)

    v = float('-inf')
    for action in actions(board):
        v = max(v, min_value(result(board, action)))
    return v


def min_value(board):
    if terminal(board):
        return utility(board)

    v = float('inf')
    for action in actions(board):
        v = min(v, max_value(result(board, action)))
    return v

