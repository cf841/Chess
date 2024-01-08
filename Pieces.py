import pygame
from copy import deepcopy
images = "./images/"


class Piece:

    def __init__ (self, pos, player, symbol, game):
        self.pos = pos
        self.player = player
        self.game = game
        self.symbol = "w" + symbol if player == "white" else "b" + symbol

        self.potential_pos = []
        self.protected = []
        self.targeted = []
        self.blocked = []

        self.pinned = False
        self.moved = False

    def copy(self):
        new_piece = Piece(self.pos.copy(), self.player, self.symbol[-1], self.game)
        new_piece.potential_pos = self.potential_pos.copy()
        new_piece.protected = self.protected.copy()
        new_piece.targeted = self.targeted.copy()
        new_piece.blocked = self.blocked.copy()
        new_piece.pinned = self.pinned
        new_piece.moved = self.moved
        return new_piece

    def load_image(self, piece):
        image_file = ("white_"+piece+".png") if self.player == "white" else ("black_"+piece+".png")
        return pygame.image.load(images+image_file)

class Pawn(Piece):
    def __init__(self, pos, player, game):
        super().__init__(pos, player, "Pa", game)
         # Is pinned for checkmate
        self.points = 1
        self.image = self.load_image("pawn")

    def see_king(self):
        direction = 1 if self.player == "black" else -1
        # Check diagonal captures
        diagonal_moves = [list((self.pos[0] + direction, self.pos[1] + i)) for i in [-1, 1]]
        for move in diagonal_moves:
            if 0 <= move[0] < 8 and 0 <= move[1] < 8:  # Check if the position is on the board
                if self.game.board[move[0]][move[1]] is not None:
                    if move == self.game.kings[("white" if self.player == "black" else "black")]:
                        return True
        return False

    def potential_moves(self):
        direction = 1 if self.player == "black" else -1
        self.potential_pos = []
        king = self.game.kings[self.player]
        pot_moves = 0
        pot_capture = 0
        
        # Check forward moves
        forward_moves = [list((self.pos[0] + direction * i, self.pos[1])) for i in range(1, 3 if not self.moved else 2)]
        for move in forward_moves:
            if not (0 <= move[0] < 8 and 0 <= move[1] < 8):
                continue
            if not self.game.board[king[0]][king[1]].check_after_move(self, move):
                if self.game.is_empty(move):
                    self.potential_pos.append(move)
                    pot_moves += 1
                elif self.game.is_friendly(self, move):
                    break
                else:
                    break

        if self.game.enpassant is not None:
            # Check if the pawn is next to the last moved pawn
            passant_pos = self.game.enpassant.pos
            if not self.game.board[king[0]][king[1]].check_after_move(self, [self.pos[0] + direction, self.game.enpassant.pos[1]]):
                if (self.pos[0] == passant_pos[0]) and ((self.pos[1] + 1 == self.game.enpassant.pos[1]) or (self.pos[1] - 1 == self.game.enpassant.pos[1])):
                    self.potential_pos.append([self.pos[0] + direction, self.game.enpassant.pos[1]])
                    self.game.board[passant_pos[0]][passant_pos[1]].targeted.append(self)
        # Check diagonal captures
        diagonal_moves = [list((self.pos[0] + direction, self.pos[1] + i)) for i in [-1, 1]]
        for move in diagonal_moves:
            if not (0 <= move[0] < 8 and 0 <= move[1] < 8) or self.game.board[king[0]][king[1]].check_after_move(self, move):
                continue
            if self.game.is_enemy(self, move):
                self.potential_pos.append(move)
                pot_moves += 1
                pot_capture += 1
            elif self.game.is_friendly(self, move):
                pass

        if not self.game.board[king[0]][king[1]].check:
            for enemy in self.targeted:
                for new_pos in self.potential_pos:
                    old = self.game.board[new_pos[0]][new_pos[1]]
                    self.game.board[new_pos[0]][new_pos[1]], self.game.board[self.pos[0]][self.pos[1]] = self, None

                    if enemy.see_king():
                        self.pinned = True
                        self.game.board[self.pos[0]][self.pos[1]], self.game.board[new_pos[0]][new_pos[1]] = self, old
                        self.potential_pos = self.calculate_potential_positions(enemy)
                        return 1, 1

                    self.game.board[self.pos[0]][self.pos[1]], self.game.board[new_pos[0]][new_pos[1]] = self, old

        return pot_moves, pot_capture

    def calculate_potential_positions(self, enemy):
        direction = 1 if self.player == "black" else -1
        king = self.game.kings[self.player]
        out = []

        # Check forward moves
        forward_moves = [list((self.pos[0] + direction * i, self.pos[1])) for i in range(1, 3 if not self.moved else 2)]
        for move in forward_moves:
            if 0 <= move[0] < 8 and 0 <= move[1] < 8:  # Check if the position is on the board
                if self.game.board[king[0]][king[1]].check_after_move(self, move):
                    out.append(move)

        # Check diagonal captures
        diagonal_moves = [list((self.pos[0] + direction, self.pos[1] + i)) for i in [-1, 1]]
        for move in diagonal_moves:
            if 0 <= move[0] < 8 and 0 <= move[1] < 8:  # Check if the position is on the board
                if self.game.board[king[0]][king[1]].check_after_move(self, move):
                    out.append(move)

        return out
    
class Knight(Piece):

    def __init__(self, pos, player, game):
        super().__init__(pos, player, "Kn", game)
        self.points = 3
        self.image = self.load_image("knight")
        self.moves = [(2, 1), (1, 2), (-1, 2), (-2, 1), (-2, -1), (-1, -2), (1, -2), (2, -1)]

    def see_king(self):
        for move in self.moves:
            new_pos = [self.pos[0] + move[0], self.pos[1] + move[1]]
            if 0 <= new_pos[0] < 8 and 0 <= new_pos[1] < 8:  # Check if the position is on the board
                if self.game.board[new_pos[0]][new_pos[1]] is not None:
                    if new_pos == self.game.kings[("white" if self.player == "black" else "black")]:
                        return True
        return False
    
    def potential_moves(self):
        pot_moves = 0
        pot_capture = 0
        self.potential_pos = []
        king = self.game.kings[self.player]

        for move in self.moves:
            new_pos = [self.pos[0] + move[0], self.pos[1] + move[1]]
            if not (0 <= new_pos[0] < 8 and 0 <= new_pos[1] < 8):
                continue
            if not self.game.board[king[0]][king[1]].check_after_move(self, new_pos):
                if self.game.is_empty(new_pos):
                    pot_moves += 1
                    self.potential_pos.append(new_pos)
                elif self.game.is_enemy(self, new_pos):
                    pot_moves +=1
                    pot_capture += 1
                    self.potential_pos.append(new_pos)
                elif self.game.is_friendly(self, new_pos):
                    continue

        if not self.game.board[king[0]][king[1]].check:
            for enemy in self.targeted:
                for new_pos in self.potential_pos:
                    old = self.game.board[new_pos[0]][new_pos[1]]
                    self.game.board[new_pos[0]][new_pos[1]], self.game.board[self.pos[0]][self.pos[1]] = self, None

                    if enemy.see_king():
                        self.pinned = True
                        self.game.board[self.pos[0]][self.pos[1]], self.game.board[new_pos[0]][new_pos[1]] = self, old
                        self.potential_pos = self.calculate_potential_positions(enemy)
                        return 1, 1

                    self.game.board[self.pos[0]][self.pos[1]], self.game.board[new_pos[0]][new_pos[1]] = self, old

        return pot_moves, pot_capture
    
    def calculate_potential_positions(self, enemy):
        x, y = self.pos
        king = self.game.kings[self.player]
        out = []

        for move in self.moves:
            new_pos = [x + move[0], y + move[1]]
            if 0 <= new_pos[0] < 8 and 0 <= new_pos[1] < 8:  # Check if the position is on the board
                if self.game.board[king[0]][king[1]].check_after_move(self, new_pos):
                    out.append(new_pos)
        return out

class Bishop(Piece):

    def __init__(self, pos, player, game):
        super().__init__(pos, player, "Bi", game)
        self.points = 3
        self.image = self.load_image("bishop")
        self.moves = [(1, 1), (-1, -1), (1, -1), (-1, 1)]

    def see_king(self):
        for move in self.moves:
            for i in range(1, 8):  # Bishop can move up to 7 squares in each direction
                new_pos = [self.pos[0] + i * move[0], self.pos[1] + i * move[1]]
                if not (0 <= new_pos[0] < 8 and 0 <= new_pos[1] < 8):  # Check if the position is on the board
                    break
                if self.game.board[new_pos[0]][new_pos[1]] is not None:
                    if new_pos == self.game.kings[("white" if self.player == "black" else "black")]:
                        return True
                    break  # Bishop can't "see" past another piece
        return False

    def potential_moves(self):
        self.potential_pos = []
        captures = 0
        king = self.game.kings[self.player]

        for move in self.moves:
            for i in range(1, 8):  # Bishop can move up to 7 squares in each direction
                new_pos = [self.pos[0] + i * move[0], self.pos[1] + i * move[1]]
                if not (0 <= new_pos[0] < 8 and 0 <= new_pos[1] < 8):
                    break

                if not self.game.board[king[0]][king[1]].check_after_move(self, new_pos):

                    if self.game.is_empty(new_pos):
                        self.potential_pos.append(new_pos)
                    elif self.game.is_enemy(self, new_pos):
                        captures += 1
                        self.potential_pos.append(new_pos)
                        break #
                    elif self.game.is_friendly(self, new_pos):
                        break 

        if not self.game.board[king[0]][king[1]].check:
            for enemy in self.targeted:
                for new_pos in self.potential_pos:
                    old = self.game.board[new_pos[0]][new_pos[1]]
                    self.game.board[new_pos[0]][new_pos[1]], self.game.board[self.pos[0]][self.pos[1]] = self, None

                    if enemy.see_king():
                        self.pinned = True
                        self.game.board[self.pos[0]][self.pos[1]], self.game.board[new_pos[0]][new_pos[1]] = self, old
                        self.potential_pos = self.calculate_potential_positions(enemy)
                        return 1, 1

                    self.game.board[self.pos[0]][self.pos[1]], self.game.board[new_pos[0]][new_pos[1]] = self, old

        return len(self.potential_pos), captures

    def calculate_potential_positions(self, enemy):
        x1, y1 = self.pos
        x2, y2 = enemy.pos
        out = []
        move = (-1 if x1 > x2 else 1, -1 if y1 > y2 else 1)
        if abs(x1 - x2) == abs(y1 - y2):
            for i in range(1, 8):
                new_pos = [x1 + i * move[0], y1 + i * move[1]]
                out.append(new_pos)
                if enemy.pos == new_pos:
                    break
        return out

class Rook(Piece):

    def __init__(self, pos, player, game):
        super().__init__(pos, player, "Ro", game)
        self.points = 5
        self.image = self.load_image("rook")
        self.moves = [(1, 0), (-1, 0), (0, 1), (0, -1)] # All possible directions for a rook
    
    def see_king(self):
        for move in self.moves:
            for i in range(1, 8):
                new_pos = [self.pos[0] + i * move[0], self.pos[1] + i * move[1]]
                if not (0 <= new_pos[0] < 8 and 0 <= new_pos[1] < 8):
                    break
                if self.game.board[new_pos[0]][new_pos[1]] is not None:
                    if self.game.kings[("white" if self.player == "black" else "black")] == new_pos:
                        return True
                    break
        return False

    # THIS APPARNETLY WORK DO NOT BREAK
    def potential_moves(self):
        pot_moves = 0
        pot_capture = 0
        self.potential_pos = []
        king = self.game.kings[self.player]

        for move in self.moves:
            for i in range(1, 8): # Rook can move up to 7 squares in each direction
                new_pos = [self.pos[0] + i * move[0], self.pos[1] + i * move[1]]
                if not (0 <= new_pos[0] < 8 and 0 <= new_pos[1] < 8):
                    break

                # Will making this move, put the king into check ie ILLEGAL
                if not self.game.board[king[0]][king[1]].check_after_move(self, new_pos):

                    if self.game.is_empty(new_pos):
                        pot_moves += 1
                        self.potential_pos.append(new_pos)
                    elif self.game.is_enemy(self, new_pos):
                        pot_moves += 1
                        pot_capture += 1
                        self.potential_pos.append(new_pos)
                        break # Rook can't move past an enemy piece
                    elif self.game.is_friendly(self, new_pos):
                        break # Rook can't move past a friendly piece

        if not self.game.board[king[0]][king[1]].check:
            for enemy in self.targeted:
                for new_pos in self.potential_pos:
                    old = self.game.board[new_pos[0]][new_pos[1]]
                    self.game.board[new_pos[0]][new_pos[1]], self.game.board[self.pos[0]][self.pos[1]] = self, None

                    if enemy.see_king():
                        self.pinned = True
                        self.game.board[self.pos[0]][self.pos[1]], self.game.board[new_pos[0]][new_pos[1]] = self, old
                        self.potential_pos = self.calculate_potential_positions(enemy)
                        return 1, 1

                    self.game.board[self.pos[0]][self.pos[1]], self.game.board[new_pos[0]][new_pos[1]] = self, old

            return pot_moves, pot_capture

    def calculate_potential_positions(self, enemy):
        if self.pos[0] == enemy.pos[0]:  # The pieces are in the same row
            min_col, max_col = sorted([self.pos[1], enemy.pos[1]])
            return [[self.pos[0], col] for col in range(min_col, max_col + 1) if col != self.pos[1]]
        elif self.pos[1] == enemy.pos[1]:  # The pieces are in the same column
            min_row, max_row = sorted([self.pos[0], enemy.pos[0]])
            return [[row, self.pos[1]] for row in range(min_row, max_row + 1) if row != self.pos[0]]
        else:
            return []
 
class Queen(Piece):

    def __init__(self, pos, player, game):
        super().__init__(pos, player, "Qu", game)
        self.points = 9
        self.image = images + ("white_queen.png" if player == "white" else "black_queen.png")
        self.image = pygame.image.load(self.image)
        self.moves = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1)] # All possible directions for a queen

    def see_king(self):
        for move in self.moves:
            for i in range(1, 8):  # Queen can move up to 7 squares in each direction
                new_pos = [self.pos[0] + i * move[0], self.pos[1] + i * move[1]]
                if not (0 <= new_pos[0] < 8 and 0 <= new_pos[1] < 8):  # Check if the position is on the board
                    break
                if self.game.board[new_pos[0]][new_pos[1]] is not None:
                    if new_pos == self.game.kings[("white" if self.player == "black" else "black")]:
                        return True
                    break  # Queen can't "see" past another piece
        return False

    def potential_moves(self):
        self.potential_pos = []
        captures = 0
        king = self.game.kings[self.player]

        for move in self.moves:
            for i in range(1, 8):  # Queen can move up to 7 squares in each direction
                new_pos = [self.pos[0] + i * move[0], self.pos[1] + i * move[1]]

                if not (0 <= new_pos[0] < 8 and 0 <= new_pos[1] < 8):
                    break
                if not self.game.board[king[0]][king[1]].check_after_move(self, new_pos):
                    piece_at_new_pos = self.game.board[new_pos[0]][new_pos[1]]
                    if piece_at_new_pos is None:
                        self.potential_pos.append(new_pos)
                    if self.game.is_enemy(self, new_pos):
                        self.potential_pos.append(new_pos)
                        captures += 1
                        break  # Queen can't move past an enemy piece
                    elif self.game.is_friendly(self, new_pos):  # The piece is a friend
                        break  # Queen can't move past a friendly piece
    
        if not self.game.board[king[0]][king[1]].check:
            for enemy in self.targeted:
                for new_pos in self.potential_pos:
                    old = self.game.board[new_pos[0]][new_pos[1]]
                    self.game.board[self.pos[0]][self.pos[1]], self.game.board[new_pos[0]][new_pos[1]] = None, self
                    if enemy.see_king():
                        self.pinned = True
                        self.game.board[self.pos[0]][self.pos[1]], self.game.board[new_pos[0]][new_pos[1]] = self, old
                        self.potential_pos = self.calculate_potential_positions(enemy)
                        return 1, 1
                    self.game.board[self.pos[0]][self.pos[1]], self.game.board[new_pos[0]][new_pos[1]] = self, old

        return len(self.potential_pos), captures

    
    def calculate_potential_positions(self, enemy):
        king = self.game.kings[self.player]
        out = []

        for dx, dy in self.moves:
            for i in range(1, 8):  # Queen can move up to 7 squares in any direction
                new_pos = [self.pos[0] + dx * i, self.pos[1] + dy * i]
                if 0 <= new_pos[0] < 8 and 0 <= new_pos[1] < 8:  # Check if the position is on the board
                    if self.game.board[king[0]][king[1]].check_after_move(self, new_pos):
                        out.append(new_pos)
                    if self.game.board[new_pos[0]][new_pos[1]] is not None:
                        break  # Queen can't move past any piece
                else:
                    break  # Break if the position is off the board
        return out

class King(Piece):

    def is_path_clear(self, start, end):
        direction = 1 if start < end else -1
        for i in range(start + direction, end, direction):
            if self.game.board[self.pos[0]][i] is not None:
                return False
        return True

    def see_king(self):
        return False

    def is_in_check(self, new_pos):
        for i in range(8):
            for j in range(8):
                piece = self.game.board[i][j]
                if piece is not None and piece.player!= self.player:
                    if new_pos in piece.potential_pos:
                        return True
        return False

    def check_after_move(self, piece, new_pos):
        old_pos = piece.pos # the old position of the piece to be moved
        old = self.game.board[new_pos[0]][new_pos[1]] # what was in the place the piece is attempting to move
        self.game.board[old_pos[0]][old_pos[1]] = None
        self.game.board[new_pos[0]][new_pos[1]] = piece
        old_king = self.game.kings[piece.player]
        if isinstance(piece, King):
            self.game.kings[piece.player] = new_pos
        for enemy in self.targeted:
            if enemy != old:
                if enemy.see_king():
                    self.game.board[old_pos[0]][old_pos[1]] = piece
                    self.game.board[new_pos[0]][new_pos[1]] = old
                    self.game.kings[piece.player] = old_king
                    return True # is still in check
        self.game.board[old_pos[0]][old_pos[1]] = piece
        self.game.board[new_pos[0]][new_pos[1]] = old
        self.game.kings[piece.player] = old_king
        return False # King no longer being checked


    def check_castling(self, pot_moves, king, queen, row):
        if king in self.game.gamestate:
            self.check_castling_side(pot_moves, row, 7)
        if queen in self.game.gamestate:
            self.check_castling_side(pot_moves, row, 0)

    def check_castling_side(self, pot_moves, row, col):
        piece = self.game.board[row][col]
        if self.is_path_clear(self.pos[1], piece.pos[1]):
            new_pos = [self.pos[0], self.pos[1] + 2 * (1 if piece.pos[1] > self.pos[1] else -1)]
            if not self.is_in_check(new_pos):
                self.potential_pos.append(new_pos)
                pot_moves += 1

    def __init__(self, pos, player, game):
        super().__init__(pos, player, "Ki", game)
        self.image = self.load_image("king")
        self.points = float('inf')
        self.check = False
        self.moves = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1)] # All possible directions for a king

    # Need to be careful around checkmates here, tho infinite points should do it.
    def potential_moves(self):
        pot_moves = 0
        pot_capture = 0
        self.potential_pos = []

        for move in self.moves:
            new_pos = [self.pos[0] + move[0], self.pos[1] + move[1]]
            if not (0 <= new_pos[0] < 8 and 0 <= new_pos[1] < 8):
                continue

            if self.game.is_empty(new_pos) and not self.check_after_move(self, new_pos):
                self.potential_pos.append(new_pos)
                pot_moves += 1
                self.check = False

            elif self.game.is_enemy(self, new_pos) and not any(self.game.board[new_pos[0]][new_pos[1]].protected) and not self.check_after_move(self, new_pos):
                self.potential_pos.append(new_pos)
                pot_moves += 1
                pot_capture += 1
                self.check = False

        if self.player == "white":
            self.check_castling(pot_moves, 'K', 'Q', 7)
        elif self.player == "black":
            self.check_castling(pot_moves, 'k', 'q', 0)

        return pot_moves, pot_capture

