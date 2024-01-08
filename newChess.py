import chess
import pygame
from pygame.locals import *

pygame.init()

BOARD_WIDTH = BOARD_HEIGHT = 640  # 60px * 8 squares
SQUARE_SIZE = BOARD_WIDTH // 8



# Load images
images = {}
for color in ["white", "black"]:
    for piece in ["pawn", "knight", "bishop", "rook", "queen", "king"]:
        images[f"{color}_{piece}"] = pygame.image.load(f"images/{color}_{piece}.png")
# Create the display
screen = pygame.display.set_mode((BOARD_WIDTH, BOARD_HEIGHT))

def draw_board(board):
    # Draw the board
    for row in range(8):
        for col in range(8):
            color = (233, 236, 239) if (row + col) % 2 == 0 else (125, 135, 150)
            pygame.draw.rect(screen, color, pygame.Rect(col*SQUARE_SIZE, row*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
            
            piece = board.piece_at(chess.square(col, 7-row))  # Change here
            if piece:
                color = "white" if piece.color == chess.WHITE else "black"
                piece_name = ["pawn", "knight", "bishop", "rook", "queen", "king"][piece.piece_type - 1]
                image = images[f"{color}_{piece_name}"]
                image_rect = image.get_rect()
                image_rect.center = ((col * SQUARE_SIZE) + SQUARE_SIZE // 2, (row * SQUARE_SIZE) + SQUARE_SIZE // 2)
                screen.blit(image, image_rect)
            for move in legal_moves:
                square =  (move.to_square % 8, 7 - move.to_square // 8)
                pygame.draw.circle(screen, (110, 80, 180), ((square[0] * SQUARE_SIZE) + SQUARE_SIZE // 2, (square[1] * SQUARE_SIZE) + SQUARE_SIZE // 2), 10)

    pygame.display.flip()



transposition_table = {}
piece_square_tables = {
    "P": [
    [0, 0, 0, 0, 0, 0, 0, 0],
    [50, 50, 50, 50, 50, 50, 50, 50],
    [10, 10, 20, 30, 30, 20, 10, 10],
    [5, 5, 10, 30, 30, 10, 5, 5],
    [0, 0, 0, 25, 25, 0, 0, 0],
    [5, -5, -10, 0, 0, -10, -5, 5],
    [5, 10, 10, -20, -20, 10, 10, 5],
    [0, 0, 0, 0, 0, 0, 0, 0]
],  # Fill in with actual values
    "N": [
        [-50, -40, -30, -30, -30, -30, -40, -50],
        [-40, -20, 0, 0, 0, 0, -20, -40],
        [-30, 0, 10, 15, 15, 10, 0, -30],
        [-30, 5, 15, 20, 20, 15, 5, -30],
        [-30, 0, 15, 20, 20, 15, 0, -30],
        [-30, 5, 10, 15, 15, 10, 5, -30],
        [-40, -20, 0, 5, 5, 0, -20, -40],
        [-50, -40, -30, -30, -30, -30, -40, -50]
        ],
    "B": [
        [-20, -10, -10, -10, -10, -10, -10, -20],
        [-10, 0, 0, 0, 0, 0, 0, -10],
        [-10, 0, 5, 10, 10, 5, 0, -10],
        [-10, 5, 5, 10, 10, 5, 5, -10],
        [-10, 0, 10, 10, 10, 10, 0, -10],
        [-10, 10, 10, 10, 10, 10, 10, -10],
        [-10, 5, 0, 0, 0, 0, 5, -10],
        [-20, -10, -10, -10, -10, -10, -10, -20]
],
    "R": [
    [0, 0, 0, 0, 0, 0, 0, 0],
    [5, 10, 10, 10, 10, 10, 10, 5],
    [-5, 0, 0, 0, 0, 0, 0, -5],
    [-5, 0, 0, 0, 0, 0, 0, -5],
    [-5, 0, 0, 0, 0, 0, 0, -5],
    [-5, 0, 0, 0, 0, 0, 0, -5],
    [-5, 0, 0, 0, 0, 0, 0, -5],
    [0, -5, 0, 5, 5, 0, -5, 0]
],
    "Q": [
    [-20, -10, -10, -5, -5, -10, -10, -20],
    [-10, 0, 0, 0, 0, 0, 0, -10],
    [-10, 0, 5, 5, 5, 5, 0, -10],
    [-5, 0, 5, 5, 5, 5, 0, -5],
    [0, 0, 5, 5, 5, 5, 0, -5],
    [-10, 5, 5, 5, 5, 5, 0, -10],
    [-10, 0, 5, 0, 0, 0, 0, -10],
    [-20, -10, -10, -5, -5, -10, -10, -20]
],
    "K": [
    [-30, -40, -40, -50, -50, -40, -40, -30],
    [-30, -40, -40, -50, -50, -40, -40, -30],
    [-30, -40, -40, -50, -50, -40, -40, -30],
    [-30, -40, -40, -50, -50, -40, -40, -30],
    [-20, -30, -30, -40, -40, -30, -30, -20],
    [-10, -20, -20, -20, -20, -20, -20, -10],
    [20, 20, -10, -10, -10, -10, 20, 20],
    [20, 50, 10, -5, -5, 10, 50, 20]
],
}

def is_passed_pawn(board, square):
    pawn = board.piece_at(square)
    if pawn is None or pawn.piece_type != chess.PAWN:
        return False

    pawn_square = chess.square_rank(square)
    file = chess.square_file(square)

    if pawn.color == chess.WHITE:
        for rank in range(pawn_square + 1, 8):
            for p_file in [file - 1, file, file + 1]:
                if p_file >= 0 and p_file <= 7:
                    if board.piece_at(chess.square(p_file, rank)) == chess.PAWN:
                        return False
    else:
        for rank in range(pawn_square - 1, -1, -1):
            for p_file in [file - 1, file, file + 1]:
                if p_file >= 0 and p_file <= 7:
                    if board.piece_at(chess.square(p_file, rank)) == chess.PAWN:
                        return False

    return True

def is_doubled_pawn(board, square):
    pawn = board.piece_at(square)
    if pawn is None or pawn.piece_type != chess.PAWN:
        return False

    pawn_square = chess.square_rank(square)
    file = chess.square_file(square)

    if pawn.color == chess.WHITE and pawn_square < 7:
        return board.piece_at(chess.square(file, pawn_square + 1)) == chess.PAWN
    elif pawn.color == chess.BLACK and pawn_square > 0:
        return board.piece_at(chess.square(file, pawn_square - 1)) == chess.PAWN

    return False

def evaluation(board):
    piece_values = {"P": 100, "N": 300, "B": 300, "R": 500, "Q": 900, "K": 0}
    moveability = {"P": 1, "N": 3, "B": 5, "R": 5, "Q": 9, "K": -10}
    white_material = 0
    black_material = 0 
    white_position = 0
    black_position = 0
    white_movement = 0
    black_movement = 0
    total = 0

    # Additional pawn structure variables
    white_passed_pawns = 0
    black_passed_pawns = 0
    white_doubled_pawns = 0
    black_doubled_pawns = 0

    for square in chess.SQUARES:
        piece = board.piece_at(square)
        row = square// 8
        col = square % 8
        if piece is not None:
            value = piece_values[piece.symbol().upper()]
            if piece.symbol().islower():
                table = piece_square_tables[piece.symbol().upper()]
                position_value = table[row][col]
            else:
                position_value = piece_square_tables[piece.symbol().upper()][7-row][col]
            if piece.color == chess.WHITE:
                white_material += value
                white_movement += moveability[piece.symbol().upper()]
                white_position += position_value

                # Additional pawn structure logic for white
                if piece.symbol().upper() == 'P':
                    if is_passed_pawn(board, square):
                        white_passed_pawns += 1
                    if is_doubled_pawn(board, square):
                        white_doubled_pawns += 1
            else:
                black_material += value
                black_movement += moveability[piece.symbol().upper()]
                black_position += position_value

                # Additional pawn structure logic for black
                if piece.symbol().upper() == 'P':
                    if is_passed_pawn(board, square):
                        black_passed_pawns += 1
                    if is_doubled_pawn(board, square):
                        black_doubled_pawns += 1

    total += white_material - black_material
    total += white_position - black_position

    # Add pawn structure to total
    total += (white_passed_pawns - black_passed_pawns) * 10
    total -= (white_doubled_pawns - black_doubled_pawns) * 5

    if board.is_checkmate():
        if board.turn == chess.WHITE:
            return float('-inf')  # Black wins
        else:
            return float('inf')  # White wins
    elif board.is_check():
        if board.turn == chess.WHITE:
            total -= 50  # Black has given check
        else:
            total += 50  # White has given check

    return total


board = chess.Board()

# Function still doesnt recognise other player taking it's pieces in future moves
transposition_table = {}

def Search(board, depth, alpha = float('-inf'), beta = float('inf')):
    fen = board.fen()

    if depth == 0 or board.is_checkmate() or board.is_stalemate():
        return SearchAllCaptures(board, alpha, beta)
    
    bestEval = float('-inf')
    moves = board.legal_moves
    for move in moves:
        board.push(move)
        eval = -Search(board, depth-1, -beta, -alpha)
        board.pop()
        bestEval = max(eval, bestEval)
        alpha = max(alpha, eval)
        if alpha >= beta:
            break
    
    return bestEval

def SearchAllCaptures(board, alpha, beta):
    eval = evaluation(board)
    if eval >= beta:
        return beta
    alpha = max(alpha, eval)
    moves = board.legal_moves
    for move in moves:
        if board.is_capture(move):
            board.push(move)
            eval = -SearchAllCaptures(board, -beta, -alpha)
            board.pop()
        
        if eval >= beta:
            return beta
        alpha = max(alpha, eval)
    return alpha




opening_moves = {
    'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1': 'e2e4',  # Example opening move
    'rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 2': 'g1f3',
    'rnbqkbnr/ppp1pppp/8/3p4/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 2': 'e4d5',
    'rnbqkb1r/pppppppp/5n2/8/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 1 2': 'e4e5',
    'rnb1kbnr/ppp1pppp/8/3q4/8/8/PPPP1PPP/RNBQKBNR w KQkq - 0 3' : 'b1c3'
}

def bot(board : chess.Board):

    board_fen = board.fen()
    print(board_fen)
    if board_fen in opening_moves:
        return chess.Move.from_uci(opening_moves[board_fen])

    high_val = float('-inf')
    best = None
    for move in board.legal_moves:
        board.push(move)
        score =  Search(board, 2)
        print(f"{board.piece_at(move.to_square)} : {move} for a score of {score}")
        board.pop()
        if score > high_val:
            high_val = score
            best = move
    return best

def sort_moves(board):
    capture = []
    non_captures = []
    for move in board.legal_moves:
        if board.is_capture(move):
            capture.append(move)
        else:
            non_captures.append(move)
    return capture + non_captures

dragging = False
drag_piece = None
drag_pos = None
legal_moves = []

BOT = chess.WHITE

while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
        elif event.type == MOUSEBUTTONDOWN:
            if board.turn != BOT:  # Only allow the player to move when it's their turn
                mouse_pos = pygame.mouse.get_pos()
                square = (mouse_pos[0] // SQUARE_SIZE, 7 - mouse_pos[1] // SQUARE_SIZE)  # Change here
                piece = board.piece_at(chess.square(*square))
                if piece and piece.color != BOT:  # Only allow the player to pick up their own pieces
                    dragging = True
                    drag_piece = piece
                    drag_pos = square
                    legal_moves = [move for move in board.legal_moves if move.from_square == chess.square(*square)]
        elif event.type == MOUSEBUTTONUP:
            if dragging:
                mouse_pos = pygame.mouse.get_pos()
                square = (mouse_pos[0] // SQUARE_SIZE, 7 - mouse_pos[1] // SQUARE_SIZE)  # Change here
                if square != drag_pos:  # Add this line
                    # Check if the move is a pawn promotion
                    if drag_piece.piece_type == chess.PAWN and square[1] in [0, 7]:
                        # Promote to a queen for now, you can add a selection later
                        move = chess.Move.from_uci(f"{chess.square_name(chess.square(*drag_pos))}{chess.square_name(chess.square(*square))}q")
                    else:
                        move = chess.Move.from_uci(f"{chess.square_name(chess.square(*drag_pos))}{chess.square_name(chess.square(*square))}")
                    if move in board.legal_moves:
                        board.push(move)
                dragging = False

    draw_board(board)
    pygame.display.update()

    if not dragging and board.turn == BOT:  # Let the bot make a move when it's their turn
        legal_moves = []
        move = bot(board)
        if move is None:
            print("checkmate")
            inp = input()
        board.push(move)
        print("")