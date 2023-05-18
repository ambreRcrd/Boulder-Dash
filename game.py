import numpy as np
import unittest

# Import d'un niveau
level_path = "level_test.txt"

class Wall:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.id = 'w'
        self.is_solid = True
        self.is_gravity_affected = False

class Coin:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.id = 'c'
        self.is_solid = False # la piece n'est pas solide et peut être traversée
        self.is_gravity_affected = True

class Brick:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.id = 'b'
        self.is_solid = False  # la brique est solide et ne peut pas être traversée
        self.is_gravity_affected = False  # la brique n'est pas affectée par la gravité

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.id = '@'
        self.is_solid = True  # le joueur est solide et ne peut pas être traversé
        self.is_gravity_affected = False  # le joueur est affecté par la gravité
        self.coins = 0  # le joueur commence avec 0 diamants

    def update_position(self, new_x, new_y):
        self.x = new_x
        self.y = new_y

    def get_coin(self):
        self.coins += 1


class Diamond:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.id = 'd'
        self.is_solid = False  # le diamant n'est pas solide et peut être traversé
        self.is_gravity_affected = True  # le diamant est affecté par la gravité

    def gravity_effect(self): # unused
        self.y -= 1


class Stone:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.id = 's'
        self.is_solid = True  # la pierre est solide et ne peut pas être traversée
        self.is_gravity_affected = True  # la pierre est affectée par la gravité
        self.is_pushable = True  # la pierre peut être poussée par le joueur ou d'autres objets

    def gravity_effect(self):
        self.y -= 1


class Empty:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.id = ' '
        self.is_solid = False  # l'espace vide n'est pas solide et peut être traversé
        self.is_gravity_affected = False  # l'espace vide n'est pas affecté par la gravité


class Board:
    def __init__(self, width, height, level_path):
        self.width = width
        self.height = height
        self.level_path = level_path
        self.class_correspondings = {
            '@': Player,
            'b': Brick,
            'w': Wall,
            's': Stone,
            'c': Coin,
            ' ': Empty
        }
        self.grid = self.create_grid()
        self.player = Player(self.get_icone_coord('@')[0], self.get_icone_coord('@')[1])  # initialiser le joueur en haut à gauche

    #def update(self):
    #    # Mettre à jour la position des pièces soumises à la gravité
    #    for y in range(self.height - 1, -1, -1):  # parcourir les colonnes de bas en haut
    #        for x in range(self.width):
    #            if isinstance(self.grid[y][x], Falling):
    #                self.move_falling_piece(x, y)

    def apply_gravity(self, grid):
        new_grid = [row[:] for row in grid]  # Créer une copie de la grille originale

        for y in range(len(new_grid) - 2, -1, -1):  # Commencer à l'index y = len(new_grid) - 2
            for x in range(len(new_grid[0])):
                # Si la case contient une pierre
                if new_grid[y][x].is_gravity_affected:
                    # Si la case en dessous est vide
                    if new_grid[y + 1][x].id == " ":
                        # La pierre tombe d'une case
                        icone = new_grid[y][x].id
                        class_corres = self.class_correspondings[icone]
                        new_grid[y + 1][x] = class_corres(x, y + 1)
                        new_grid[y][x] = Empty(x, y)

        # Vérifier si d'autres éléments peuvent tomber après le premier passage
        has_fallen = True
        while has_fallen:
            has_fallen = False
            for y in range(len(new_grid) - 2, -1, -1):  # Commencer à l'index y = len(new_grid) - 2
                for x in range(len(new_grid[0])):
                    # Si la case contient une pierre
                    if new_grid[y][x].is_gravity_affected:
                        # Si la case en dessous est vide
                        if new_grid[y + 1][x].id == " ":
                            # La pierre tombe d'une case
                            icone = new_grid[y][x].id
                            class_corres = self.class_correspondings[icone]
                            new_grid[y + 1][x] = class_corres(x, y + 1)
                            new_grid[y][x] = Empty(x, y)
                            has_fallen = True
                            break
                if has_fallen:
                    break

        return new_grid

    def moved_icone(self, old_grid, grid):
        to_erase = []
        for y in range(1, len(old_grid)):
            for x in range(1, len(old_grid[0])):
                if (
                        old_grid[y][x] != grid[y][x]
                        and grid[y][x].is_gravity_affected
                        and grid[y - 1][x].id == ' '
                ):
                    to_erase.append([x, y - 1])
        return to_erase

    def create_grid(self):
        with open(self.level_path, "r") as f:
            lines = f.readlines()

        nb_lignes = len(lines)
        nb_colonnes = len(lines[0].strip())

        grid = [[None] * nb_colonnes for _ in range(nb_lignes)]

        for y, line in enumerate(lines):
            line = line.strip()
            for x, icone in enumerate(line):
                corres_class = self.class_correspondings[icone]
                grid[y][x] = corres_class(x, y)

        return grid

    def to_list_grid(self, grid):
        nb_lignes = len(grid)
        nb_colonnes = len(grid[0])
        new_grid = np.empty((nb_lignes, nb_colonnes), dtype=object)

        for y in range(nb_lignes):
            for x in range(nb_colonnes):
                new_grid[y][x] = grid[y][x].id

        print(new_grid)
        return new_grid.tolist()

    def get_icone_coord(self, icone_symb):
        for y, row in enumerate(self.grid):
            for x, icone in enumerate(row):
                if icone.id == icone_symb:
                    return icone.x, icone.y
        return 0, 0

    #def move_falling_piece(self, x, y):
    #    # Vérifier si la pièce peut tomber d'un cran
    #    if not self.is_valid_position(x, y + 1):
    #        return  # la pièce ne peut pas tomber, ne rien faire
#
    #    # Faire tomber la pièce d'un cran
    #    self.grid[x][y + 1] = self.grid[x][y]
    #    self.grid[x][y] = Empty(x, y)
#
    #    # Si la pièce est une pierre et qu'elle est tombée sur un diamant, le collecter
    #    if isinstance(self.grid[x][y + 1], Diamond):
    #        self.player.has_diamonds += 1
    #        self.grid[x][y + 1] = Empty(x, y + 1)
#
    #    # Si la pièce est une pierre et qu'elle est tombée sur le joueur, le tuer
    #    if isinstance(self.grid[x][y + 1], Player):
    #        self.player.is_alive = False

    #def is_valid_position(self, x, y):
    #    # Vérifier si la position est à l'intérieur du plateau
    #    if x < 0 or x >= self.width or y < 0 or y >= self.height:
    #        return False
#
    #    # Vérifier si la case est traversable
    #    return not self.grid[x][y].is_solid

    #def move_player(self, dx, dy):
    #    # Vérifier si le mouvement est valide
    #    new_x = self.player.x + dx
    #    new_y = self.player.y + dy
    #    if not self.is_valid_position(new_x, new_y):
    #        return False  # le mouvement n'est pas valide, retourner False
#
    #    # Déplacer le joueur
    #    self.grid[self.player.x][self.player.y] = Empty(self.player.x, self.player.y)  # effacer la case précédente du joueur
    #    self.player.x = new_x
    #    self.player.y = new_y
    #    self.grid[self.player.x][self.player.y] = self.player  # placer le joueur sur la nouvelle case
#
    #    # Si le joueur a collecté un diamant, l'ajouter à son inventaire
    #    if isinstance(self.grid[self.player.x][self.player.y], Diamond):
    #        self.player.has_diamonds += 1
    #        self.grid[self.player.x][self.player.y] = Empty(self.player.x, self.player.y)  # effacer le diamant de la case
#
    #    return True  # le mouvement est valide, retourner True
#
    #def push_stone(self, dx, dy):
    #    # Vérifier si le mouvement est valide
    #    new_x = self.player.x + dx
    #    new_y = self.player.y + dy
    #    if not self.is_valid_position(new_x, new_y):
    #        return False  # le mouvement n'est pas valide, retourner False
#
    #    # Vérifier si la case suivante contient une pierre poussable
    #    if not isinstance(self.grid[new_x][new_y], Stone) or not self.grid[new_x][new_y].is_pushable:
    #        return False  # la case suivante ne contient pas de pierre poussable, retourner False
#
    #    # Vérifier si la case suivante après la pierre est valide
    #    new_stone_x = new_x + dx
    #    new_stone_y = new_y + dy
    #    if not self.is_valid_position(new_stone_x, new_stone_y):
    #        return False  # la case suivante après la pierre n'est pas valide, retourner False
#
    #    # Pousser la pierre
    #    self.grid[new_stone_x][new_stone_y] = self.grid[new_x][new_y]
    #    self.grid[new_x][new_y] = Empty(new_x, new_y)
#
    #    # Déplacer le joueur
    #    self.grid[self.player.x][self.player.y] = Empty(self.player.x, self.player.y)  # effacer la case précédente du joueur
    #    self.player.x = new_x
    #    self.player.y = new_y
    #    self.grid[self.player.x][self.player.y] = self.player  # placer le joueur sur la nouvelle case
#
    #    # Si le joueur a collecté un diamant, l'ajouter à son inventaire
    #    if isinstance(self.grid[self.player.x][self.player.y], Diamond):
    #        self.player.has_diamonds += 1
    #        self.grid[self.player.x][self.player.y] = Empty(self.player.x, self.player.y)  # effacer le diamant de la case
#
    #    return True  # le mouvement est valide, retourner True

    def center_view(self, view_width, view_height):
        # Calculer les coordonnées pour centrer la vue sur le joueur
        pass

class TestBoard(unittest.TestCase):
    def setUp(self):
        self.board = Board(5, 5, level_path)
        self.board.grid[1][1] = Coin(1, 1) #Coin(1, 1, 1)
        self.board.grid[3][3] = Coin(3, 3) #Coin(3, 3, 2)

    def test_piece_positions(self):
        self.assertEqual(self.board.grid[1][1].x, 1)
        self.assertEqual(self.board.grid[1][1].y, 1)
        self.assertEqual(self.board.grid[3][3].x, 3)
        self.assertEqual(self.board.grid[3][3].y, 3)

    #def test_piece_ids(self):
    #    self.assertEqual(self.board.grid[1][1].id, 1)
    #    self.assertEqual(self.board.grid[3][3].id, 2)
