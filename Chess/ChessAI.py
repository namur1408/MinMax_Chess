import random

pieceScore = {"K": 0, "Q": 10, "R": 5, "B": 3, "N": 3, "p": 1, "--": 0}
CHECKMATE = 1000
STALEMATE = 0
DEPTH = 2


def findBestMove(gs, validMoves):
    global nextMove
    nextMove = None
    alpha = -CHECKMATE * 10
    beta = CHECKMATE * 10

    if gs.white_to_move:
        findMoveMinimax(gs, validMoves, DEPTH, alpha, beta, 1)
    else:
        findMoveMinimax(gs, validMoves, DEPTH, alpha, beta, -1)

    return nextMove


def findMoveMinimax(gs, validMoves, depth, alpha, beta, turnMultiplier):
    global nextMove
    if depth == 0:
        return turnMultiplier * scoreBoard(gs)
    random.shuffle(validMoves)
    maxScore = -CHECKMATE * 10
    for move in validMoves:
        gs.makeMove(move)
        nextMoves = gs.getValidMoves()
        score = -findMoveMinimax(gs, nextMoves, depth - 1, -beta, -alpha, -turnMultiplier)
        if score > maxScore:
            maxScore = score
            if depth == DEPTH:
                nextMove = move
        gs.undoMove()
        alpha = max(alpha, maxScore)
        if alpha >= beta:
            break
    return maxScore

def scoreBoard(gs):
    if gs.checkMate:
        return -CHECKMATE if gs.white_to_move else CHECKMATE
    elif gs.staleMate:
        return STALEMATE
    score = 0
    for row in gs.board:
        for square in row:
            if square[0] == 'w':
                score += pieceScore[square[1]]
            elif square[0] == 'b':
                score -= pieceScore[square[1]]
    return score