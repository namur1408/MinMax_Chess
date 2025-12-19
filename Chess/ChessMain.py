import pygame as p
from Chess import ChessEngine
import ChessAI
import random

p.init()
WIDTH = HEIGTH = 512
DIMENSION = 8
SQ_SIZE = HEIGTH // DIMENSION
MAX_FPS = 45
IMAGES = {}


def load_images():
    pieces = ['wp', 'wR', 'wN', 'wB', 'wK', 'wQ',
              'bp', 'bR', 'bN', 'bB', 'bK', 'bQ']
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(
            p.image.load('images/' + piece + '.png'),
            (SQ_SIZE, SQ_SIZE)
        )


def drawText(screen, text):
    font = p.font.SysFont("Helvetica", 32, True, False)
    textObject = font.render(text, 0, p.Color('Black'), p.Color('White'))  # Added background for readability
    textLocation = p.Rect(0, 0, WIDTH, HEIGTH)
    screen.blit(textObject, textObject.get_rect(center=textLocation.center))


def main():
    screen = p.display.set_mode((WIDTH, HEIGTH))
    clock = p.time.Clock()
    gs = ChessEngine.GameState()
    validMoves = gs.getValidMoves()
    moveMade = False
    load_images()
    running = True
    sqSelected = ()
    playerClicks = []
    animate = False
    lastMove = None
    gameOver = False

    # Player settings: True for Human, False for AI
    playerOne = True  # White
    playerTwo = False  # Black (AI)

    while running:
        isHumanTurn = (gs.white_to_move and playerOne) or (not gs.white_to_move and playerTwo)

        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            elif e.type == p.MOUSEBUTTONDOWN:
                if not gameOver and isHumanTurn:
                    location = p.mouse.get_pos()
                    col = location[0] // SQ_SIZE
                    row = location[1] // SQ_SIZE
                    if sqSelected == (row, col):
                        sqSelected = ()
                        playerClicks = []
                    else:
                        sqSelected = (row, col)
                        playerClicks.append(sqSelected)
                    if len(playerClicks) == 2:
                        move = ChessEngine.Move(playerClicks[0], playerClicks[1], gs.board)
                        for validMove in validMoves:
                            if move == validMove:
                                gs.makeMove(validMove)
                                moveMade = True
                                lastMove = validMove
                                animate = True
                                break
                        sqSelected = ()
                        playerClicks = []
            elif e.type == p.KEYDOWN:
                if e.key == p.K_c:  # Undo
                    gs.undoMove()
                    moveMade = True
                    animate = False
                    gameOver = False
                elif e.key == p.K_r:  # Reset
                    gs = ChessEngine.GameState()
                    validMoves = gs.getValidMoves()
                    sqSelected = ()
                    playerClicks = []
                    moveMade = False
                    animate = False
                    lastMove = None
                    gameOver = False

        # --- AI MOVE LOGIC ---
        if not gameOver and not isHumanTurn:
            # We pass the engine state to the recursive Minimax
            aiMove = ChessAI.findBestMove(gs, validMoves)

            if aiMove is None:
                gameOver = True
            else:
                gs.makeMove(aiMove)
                moveMade = True
                lastMove = aiMove
                animate = True

        if moveMade:
            if animate:
                drawGameState(screen, gs, validMoves, sqSelected, lastMove)
                animateMove(lastMove, screen, gs.board, clock)
                animate = False

            validMoves = gs.getValidMoves()
            if len(validMoves) == 0:
                gameOver = True
            moveMade = False

        drawGameState(screen, gs, validMoves, sqSelected, lastMove)

        if gameOver:
            if gs.checkMate:
                text = "Black wins by Checkmate" if gs.white_to_move else "White wins by Checkmate"
            else:
                text = "Stalemate"
            drawText(screen, text)

        clock.tick(MAX_FPS)
        p.display.flip()

def drawGameState(screen, gs, validMoves, sqSelected, lastMove):
    drawBoard(screen)
    highlightSquares(screen, gs, validMoves, sqSelected, lastMove)
    drawPieces(screen, gs.board)


def highlightSquares(screen, gs, validMoves, sqSelected, lastMove):
    if lastMove:
        s = p.Surface((SQ_SIZE, SQ_SIZE))
        s.set_alpha(100)
        s.fill(p.Color('yellow'))
        screen.blit(s, (lastMove.startCol * SQ_SIZE, lastMove.startRow * SQ_SIZE))
        screen.blit(s, (lastMove.endCol * SQ_SIZE, lastMove.endRow * SQ_SIZE))

    if sqSelected != ():
        r, c = sqSelected
        if gs.board[r][c][0] == ('w' if gs.white_to_move else 'b'):
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(150)
            s.fill(p.Color('blue'))
            screen.blit(s, (c * SQ_SIZE, r * SQ_SIZE))
            s.fill(p.Color('teal'))
            for move in validMoves:
                if move.startRow == r and move.startCol == c:
                    screen.blit(s, (move.endCol * SQ_SIZE, move.endRow * SQ_SIZE))


def drawBoard(screen):
    colors = [p.Color("beige"), (184, 138, 92)]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[((r + c) % 2)]
            p.draw.rect(screen, color, p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))


def drawPieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--":
                screen.blit(IMAGES[piece], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))


def animateMove(move, screen, board, clock):
    dR = move.endRow - move.startRow
    dC = move.endCol - move.startCol
    framesPerSquare = 3
    frameCount = (abs(dR) + abs(dC)) * framesPerSquare

    for frame in range(frameCount + 1):
        r, c = (move.startRow + dR * frame / frameCount,
                move.startCol + dC * frame / frameCount)
        drawBoard(screen)
        color = p.Color("beige") if (move.startRow + move.startCol) % 2 == 0 else p.Color((184, 138, 92))
        p.draw.rect(screen, color, p.Rect(move.startCol * SQ_SIZE, move.startRow * SQ_SIZE, SQ_SIZE, SQ_SIZE))
        temp_board = [row[:] for row in board]
        temp_board[move.endRow][move.endCol] = move.pieceCaptured
        temp_board[move.startRow][move.startCol] = "--"
        drawPieces(screen, temp_board)
        screen.blit(IMAGES[move.pieceMoved], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))
        p.display.flip()
        clock.tick(MAX_FPS)


if __name__ == "__main__":
    main()