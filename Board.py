import pygame
import sys
from Pieces import *

class Game:

    def __init__(self):
        self.board = [[None for _ in range(8)] for _ in range(8)]
        self.kings = []
        self.gamestate = "KQkq" # can castle both sides, - for en passant
        self.enpassant = None
        self.held = None
        self.setup_pieces()

    def castle(self, king_pos, new_pos):
        # Determine castling direction
        direction = 1 if new_pos[1] > king_pos[1] else -1

       # Determine rook's initial and final positions
        rook_initial_pos = [king_pos[0], 7 if direction == 1 else 0]
        rook_final_pos = [king_pos[0], king_pos[1] + direction]

        rook = self.board[rook_initial_pos[0]][rook_initial_pos[1]]
        self.board[rook_final_pos[0]][rook_final_pos[1]] = rook
        self.board[rook_initial_pos[0]][rook_initial_pos[1]] = None
        rook.pos = rook_final_pos

        # Remove castling rights
        self.remove_castling(rook)
    
    def remove_castling(self, piece):
        if piece.player == "white":
            self.gamestate= self.gamestate.replace("KQ", "")
        elif piece.player == "black":
            self.gamestate = self.gamestate.replace("kq", "")

    def movePiece(self, pos1, pos2):

        piece = self.board[pos1[0]][pos1[1]]
        if piece.moved == False:
            if isinstance(piece, King): 
                if abs(pos2[1] - pos1[1]) == 2:
                    self.castle(pos1, pos2)
                    if piece.player == "white":
                        self.game.kings[0] = pos2
                    else: self.game.kings[1] = pos2
                else:
                    self.remove_castling(piece)
            if isinstance(piece, Rook):
                if pos1 == [0, 0]:
                    self.gamestate = self.gamestate.replace("q", "")
                elif pos1 == [0, 7]:
                    self.gamestate = self.gamestate.replace("k", "")
                elif pos1 == [7, 0]:
                    self.gamestate = self.gamestate.replace("Q", "")
                elif pos1 == [7, 7]:
                    self.gamestate = self.gamestate.replace("K", "")

            if isinstance(piece, Pawn):
                if abs(pos1[0]-pos2[0]) == 2:
                    self.enpassant = piece
                else:
                    self.enpassant = None
            else:
                self.enpassant = None

        if isinstance(piece, Pawn):
            if pos1[1] != pos2[1] and self.board[pos2[0]][pos2[1]] is None: # Check for en passant capture
                x, y = self.enpassant.pos
                self.board[y][x] = None # Have to switch cause how indexing
                self.enpassant = None
        
        if isinstance(piece, King):
            if piece.player == "white":
                self.game.kings[0] = pos2
            else: self.game.kings[1] = pos2
        if piece.moved == False:
            self.board[pos1[0]][pos1[1]].moved = True
        self.board[pos2[0]][pos2[1]] = piece
        piece.pos = pos2
        self.board[pos1[0]][pos1[1]] = None
        self.update_possible_moves()
        

    def is_valid_index(self, i, j):
        return 0 <= i < 8 and 0 <= j < 8

    def update_possible_moves(self):
        for row in self.board:
            for piece in row:
                if piece is not None:
                    piece.potential_moves()

    def draw(self, screen):
        screen.fill((0, 0, 0))

        for x in range(8):
            for y in range(8):
                color = (210, 180, 140) if (x + y) % 2 == 0 else (129, 96, 73)  # Change the color based on the position
                pygame.draw.rect(screen, color, (x*80, y*80, 80, 80))
        
        if self.held is not None:
            for pos in self.held.potential_pos:
                pygame.draw.rect(screen, (173, 216, 230), (pos[1]*80, pos[0]*80, 80, 80))

        for i in range(8):
            for j in range(8):
                piece = self.board[i][j]
                if piece is not None:
                    image_width, image_height = piece.image.get_size()
                    square_size = 80  # or whatever size your squares are
                    offset_x = (square_size - image_width) / 2
                    offset_y = (square_size - image_height) / 2
                    screen.blit(piece.image, (piece.pos[1]*80 + offset_x, piece.pos[0]*80 + offset_y))

    @staticmethod
    def is_valid(pos):
        return 0 <= pos[0] < 8 and 0 <= pos[1] < 8
    
    def is_empty(self, pos):
        if self.is_valid(pos):
            return self.board[pos[0]][pos[1]] is None
        return False
    
    def is_enemy(self, piece, pos):
        if self.is_valid(pos):
            square = self.board[pos[0]][pos[1]]
            if square is not None and square.player != piece.player:
                square.targeted.append(piece)
                if isinstance(square, King):
                    square.check = True
                return True
        return False
    
    def is_friendly(self, piece, pos):
        if self.is_valid(pos):
            square = self.board[pos[0]][pos[1]]
            if square is not None and square.player == piece.player:
                square.protected.append(piece)
                return True
        return False

    def setup_pieces(self):
        for i in range(8):
            self.board[1][i] = Pawn([1, i], "black", self)
            self.board[6][i] = Pawn([6, i], "white", self)

        # Setup the rooks
        self.board[0][0] = Rook([0, 0], "black", self)
        self.board[0][7] = Rook([0, 7], "black", self)
        self.board[7][0] = Rook([7, 0], "white", self)
        self.board[7][7] = Rook([7, 7], "white", self)

        # Setup the knights
        self.board[0][1] = Knight([0, 1], "black", self)
        self.board[0][6] = Knight([0, 6], "black", self)
        self.board[7][1] = Knight([7, 1], "white", self)
        self.board[7][6] = Knight([7, 6], "white", self)

        # Setup the bishops
        self.board[0][2] = Bishop([0, 2], "black", self)
        self.board[0][5] = Bishop([0, 5], "black", self)
        self.board[7][2] = Bishop([7, 2], "white", self)
        self.board[7][5] = Bishop([7, 5], "white", self)

        # Setup the queens
        self.board[0][3] = Queen([0, 3], "black", self)
        self.board[7][3] = Queen([7, 3], "white", self)

        # Setup the kings
        self.board[0][4] = King([0, 4], "black", self)
        self.kings.append([0, 4])
        self.board[7][4] = King([7, 4], "white", self)
        self.kings.append([7, 4])

        for i in range(8):
            for j in range(8):
                if self.board[i][j] is not None:
                    self.board[i][j].potential_moves()

    def display(self):
        board_str = '    ' + ' '.join(str(i).center(5) for i in range(8)) + '\n'  # Print column indexes
        board_str += '    ' + '-' * (len(board_str) - 1) + '\n'  # Print top border
        for i, row in enumerate(self.board):
            row_str = str(i) + ' |'  # Print row index
            for piece in row:
                if piece is None:
                    row_str += '.'.center(5) + '|'
                else:
                    row_str += piece.symbol.center(5) + '|'
            board_str += row_str + '\n' + ' ' * 4 + '-' * len(row_str) + '\n'  # Print row with bottom border
        print(board_str)

    def print_all_potential_moves(self):
        for i in range(8):
            for j in range(8):
                piece = self.board[i][j]
                if piece is not None:
                    print(f"Potential moves for piece at ({i}, {j}): {piece.potential_moves(self.board)}")

    def handle_mouse_down(self, pos):
        x, y = pos[0] // 80, pos[1] // 80
        self.held = self.board[y][x]
    
    def handle_mouse_up(self, pos):
        if self.held is not None:
            x, y = pos[0] // 80, pos[1] // 80
            if [y, x] in self.held.potential_pos:
                for king in self.kings:
                    self.board[king[0]][king[1]].check = False
                self.movePiece(self.held.pos, [y,x])
            self.held = None
    
    def print_protected(self):
        for row in self.board:
            for piece in row:
                if piece is not None and len(piece.protected) > 1:
                    print(f"{piece.pos}", end="")
                    for item in piece.protected:
                        print(item.symbol, end=", ")
                    print("")