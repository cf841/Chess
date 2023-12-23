import pygame
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

        self.pinned = False
        self.moved = False

    def load_image(self, piece):
        image_file = ("white_"+piece+".png") if self.player == "white" else ("black_"+piece+".png")
        return pygame.image.load(images+image_file)

class Pawn(Piece):
    def __init__(self, pos, player, game):
        super().__init__(pos, player, "Pa", game)
         # Is pinned for checkmate
        self.points = 1
        self.image = self.load_image("pawn")

    def potential_moves(self):
        direction = 1 if self.player == "black" else -1
        self.potential_pos = []
        self.blocked = []
        pot_moves = 0
        pot_capture = 0

        # Check forward moves
        forward_moves = [list((self.pos[0] + direction * i, self.pos[1])) for i in range(1, 3 if not self.moved else 2)]
        for move in forward_moves:
            if self.game.is_empty(move):
                self.potential_pos.append(move)
                pot_moves += 1
            else:
                break

        if self.game.enpassant is not None:
            # Check if the pawn is next to the last moved pawn
            passant_pos = self.game.enpassant.pos
            if (self.pos[0] == passant_pos[0]) and ((self.pos[1] + 1 == self.game.enpassant.pos[1]) or (self.pos[1] - 1 == self.game.enpassant.pos[1])):
                self.potential_pos.append([self.pos[0] + direction, self.game.enpassant.pos[1]])

        # Check diagonal captures
        diagonal_moves = [list((self.pos[0] + direction, self.pos[1] + i)) for i in [-1, 1]]
        for move in diagonal_moves:
            if self.game.is_enemy(self, move):
                self.potential_pos.append(move)
                pot_moves += 1
                pot_capture += 1
            elif self.game.is_friendly(self, move):
                pass

        return pot_moves, pot_capture
    
class Knight(Piece):

    def __init__(self, pos, player, game):
        super().__init__(pos, player, "Kn", game)
        self.points = 3
        self.image = self.load_image("knight")
        self.moves = [(2, 1), (1, 2), (-1, 2), (-2, 1), (-2, -1), (-1, -2), (1, -2), (2, -1)]
    
    def potential_moves(self):
        pot_moves = 0
        pot_capture = 0
        self.potential_pos = []
        self.blocked = []
        for move in self.moves:
            new_pos = [self.pos[0] + move[0], self.pos[1] + move[1]]
            if self.game.is_empty(new_pos):
                pot_moves += 1
                self.potential_pos.append(new_pos)
            elif self.game.is_enemy(self, new_pos):
                pot_moves +=1
                pot_capture += 1
                self.potential_pos.append(new_pos)
            elif self.game.is_friendly(self, new_pos):
                pass
        return pot_moves, pot_capture

class Bishop(Piece):

    def __init__(self, pos, player, game):
        super().__init__(pos, player, "Bi", game)
        self.points = 3
        self.image = self.load_image("bishop")
        self.moves = [(1, 1), (-1, -1), (1, -1), (-1, 1)]

    def potential_moves(self):
        pot_moves = 0
        pot_capture = 0
        self.potential_pos = []
        self.blocked = []
        for move in self.moves:
            for i in range(1, 8): # Bishop can move up to 7 squares in each direction
                new_pos = [self.pos[0] + i * move[0], self.pos[1] + i * move[1]]
                if not (0 <= new_pos[0] < 8 and 0 <= new_pos[1] < 8):
                    break
                if self.game.is_empty(new_pos):
                    pot_moves += 1
                    self.potential_pos.append(new_pos)
                elif self.game.is_enemy(self, new_pos):
                    pot_moves += 1
                    pot_capture += 1
                    self.potential_pos.append(new_pos)
                    break # Bishop can't move past an enemy piece
                elif self.game.is_friendly(self, new_pos):
                    break # Bishop can't move past a friendly piece
        return pot_moves, pot_capture     

class Rook(Piece):

    def __init__(self, pos, player, game):
        super().__init__(pos, player, "Ro", game)
        self.points = 5
        self.image = self.load_image("rook")
        self.moves = [(1, 0), (-1, 0), (0, 1), (0, -1)] # All possible directions for a rook

    def potential_moves(self):
        pot_moves = 0
        pot_capture = 0
        self.potential_pos = []
        self.blocked = []
        for move in self.moves:
            for i in range(1, 8): # Rook can move up to 7 squares in each direction
                new_pos = [self.pos[0] + i * move[0], self.pos[1] + i * move[1]]
                if not (0 <= new_pos[0] < 8 and 0 <= new_pos[1] < 8):
                    break
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
        return pot_moves, pot_capture
    
class King(Piece):

    def is_path_clear(self, start, end):
        direction = 1 if start < end else -1
        for i in range(start + direction, end, direction):
            if self.game.board[self.pos[0]][i] is not None:
                return False
        return True

    def is_in_check(self, new_pos):
        for i in range(8):
            for j in range(8):
                piece = self.game.board[i][j]
                if piece is not None and piece.player!= self.player:
                    if new_pos in piece.potential_pos:
                        return True
        return False

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
        self.blocked = []
        for move in self.moves:
            new_pos = [self.pos[0] + move[0], self.pos[1] + move[1]]
            if not (0 <= new_pos[0] < 8 and 0 <= new_pos[1] < 8):
                continue
            if self.game.is_empty(new_pos):
                pot_moves += 1
                self.potential_pos.append(new_pos)
            elif self.game.is_enemy(self, new_pos):
                pot_moves += 1
                pot_capture += 1
                self.potential_pos.append(new_pos)
            elif self.game.is_friendly(self, new_pos):
                self.blocked.append(new_pos)

        if self.player == "white":
            if 'K' in self.game.gamestate:
                piece = self.game.board[7][7]
                if self.is_path_clear(self.pos[1], piece.pos[1]):
                    new_pos = [self.pos[0], self.pos[1] + 2 * (1 if piece.pos[1] > self.pos[1] else -1)]
                    if self.is_in_check(new_pos):
                        pass
                    else:
                        self.potential_pos.append(new_pos)
                        pot_moves += 1
            if 'Q' in self.game.gamestate:
                piece = self.game.board[7][0]
                if self.is_path_clear(self.pos[1], piece.pos[1]):
                    new_pos = [self.pos[0], self.pos[1] + 2 * (1 if piece.pos[1] > self.pos[1] else -1)]
                    if self.is_in_check(new_pos):
                        pass
                    else:
                        self.potential_pos.append(new_pos)
                        pot_moves += 1
        
        if self.player == "black":
            if 'k' in self.game.gamestate:
                piece = self.game.board[0][7]
                if self.is_path_clear(self.pos[1], piece.pos[1]):
                    new_pos = [self.pos[0], self.pos[1] + 2 * (1 if piece.pos[1] > self.pos[1] else -1)]
                    if self.is_in_check(new_pos):
                        pass
                    else:
                        self.potential_pos.append(new_pos)
                        pot_moves += 1
            if 'q' in self.game.gamestate:
                piece = self.game.board[0][0]
                if self.is_path_clear(self.pos[1], piece.pos[1]):
                    new_pos = [self.pos[0], self.pos[1] + 2 * (1 if piece.pos[1] > self.pos[1] else -1)]
                    if self.is_in_check(new_pos):
                        pass
                    else:
                        self.potential_pos.append(new_pos)
                        pot_moves += 1

        return pot_moves, pot_capture

class Queen(Piece):

    def __init__(self, pos, player, game):
        super().__init__(pos, player, "Qu", game)
        self.points = 9
        self.image = images + ("white_queen.png" if player == "white" else "black_queen.png")
        self.image = pygame.image.load(self.image)
        self.moves = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1)] # All possible directions for a queen
        
    def potential_moves(self):
        pot_moves = 0
        pot_capture = 0
        self.potential_pos = []
        self.blocked = []
        for move in self.moves:
            for i in range(1, 8): # Queen can move up to 7 squares in each direction
                new_pos = [self.pos[0] + i * move[0], self.pos[1] + i * move[1]]
                if not (0 <= new_pos[0] < 8 and 0 <= new_pos[1] < 8):
                    break
                if self.game.is_empty(new_pos):
                    self.potential_pos.append(new_pos)
                    pot_moves += 1
                    self.potential_pos.append(new_pos)
                elif self.game.is_enemy(self, new_pos):
                    self.potential_pos.append(new_pos)
                    pot_moves += 1
                    pot_capture += 1
                    self.potential_pos.append(new_pos)
                    break # Queen can't move past an enemy piece
                elif self.game.is_friendly(self, new_pos):
                    break # Queen can't move past a friendly piece
        return pot_moves, pot_capture