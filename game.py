import copy
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
        self.is_pushable = False

class Trap:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.id = 't'
        self.is_solid = False # la piece n'est pas solide et peut être traversée
        self.is_gravity_affected = False
        self.is_pushable = False

class Coin:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.id = 'c'
        self.is_solid = False # la piece n'est pas solide et peut être traversée
        self.is_gravity_affected = True
        self.is_pushable = True

class Brick:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.id = 'b'
        self.is_solid = False  # la brique est solide et ne peut pas être traversée
        self.is_gravity_affected = False  # la brique n'est pas affectée par la gravité
        self.is_pushable = False

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.id = '@'
        self.is_solid = True  # le joueur est solide et ne peut pas être traversé
        self.is_gravity_affected = False  # le joueur est affecté par la gravité
        self.coins = 0  # le joueur commence avec 0 diamants
        self.is_pushable = False

    def update_position(self, new_x, new_y):
        '''Permet de déplacer le joueur'''
        self.x = new_x
        self.y = new_y

    def get_coin(self):
        '''Permet d'augmenter le score de 1 lorsqu'une pièce est ramassée'''
        self.coins += 1


class Stone:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.id = 's'
        self.is_solid = True  # la pierre est solide et ne peut pas être traversée
        self.is_gravity_affected = True  # la pierre est affectée par la gravité
        self.is_pushable = True  # la pierre peut être poussée par le joueur ou d'autres objets


class Empty:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.id = ' '
        self.is_solid = False  # l'espace vide n'est pas solide et peut être traversé
        self.is_gravity_affected = False  # l'espace vide n'est pas affecté par la gravité
        self.is_pushable = False


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
            't': Trap,
            ' ': Empty
        }
        self.grid = self.create_grid()
        self.player = Player(self.get_icone_coord('@')[0], self.get_icone_coord('@')[1])  # initialiser le joueur en haut à gauche


    #def apply_gravity(self, grid):
    #    '''Applique la gravité à la grille courante'''
    #    new_grid = [row[:] for row in grid]  # Créer une copie de la grille originale
#
    #    def gravity_helper(y):
    #        if y >= len(new_grid) - 1:
    #            return
#
    #        for x in range(len(new_grid[0])):
    #            # Si la case contient une pierre
    #            if new_grid[y][x].is_gravity_affected:
    #                # Si la case en dessous est vide
    #                if new_grid[y + 1][x].id == " ":
    #                    # La pierre tombe d'une case
    #                    icone = new_grid[y][x].id
    #                    class_corres = self.class_correspondings[icone]
    #                    new_grid[y + 1][x] = class_corres(x, y + 1)
    #                    new_grid[y][x] = Empty(x, y)
#
    #        gravity_helper(y + 1)
#
    #    gravity_helper(0)
    #    return new_grid

    def apply_gravity(self, grid):
        new_grid = [row[:] for row in grid]  # Créer une copie de la grille originale

        for y in range(len(new_grid) - 1, -1, -1):
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
                        # Si la pierre est tombée, on vérifie si elle peut encore tomber
                        self.apply_gravity(new_grid)  # Réappliquer la gravité à la nouvelle grille
        return new_grid


    def moved_icone(self, old_grid, grid):
        '''Renvoie une liste des icônes à supprimer, qui se trouvaient dans l'ancienne grille mais ne le sont plus dans la nouvelle'''
        to_erase = []
        for y in range(len(old_grid)):
            for x in range(len(old_grid[0])):
                if old_grid[y][x] != grid[y][x]:
                    to_erase.append([x, y])  # Ajouter les coordonnées de l'icône à supprimer
        return to_erase


    def create_grid(self):
        '''Charge un niveau et le stocke dans une grille (liste de listes)'''
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
        '''Permet l'affichage de la grille avec les icônes à la place des objets (améliore la lisibilité). Utile seulement pour le développement'''
        nb_lignes = len(grid)
        nb_colonnes = len(grid[0])
        new_grid = np.empty((nb_lignes, nb_colonnes), dtype=object)

        for y in range(nb_lignes):
            for x in range(nb_colonnes):
                new_grid[y][x] = grid[y][x].id
        print(new_grid)
        return new_grid.tolist()

    def get_icone_coord(self, icone_symb):
        '''Permet d'accéder aux coordonnées du joueur'''
        for y, row in enumerate(self.grid):
            for x, icone in enumerate(row):
                if icone.id == icone_symb:
                    return icone.x, icone.y
        return 0, 0

    def is_valid_position(self, x, y):
        '''Vérifie la conformité des coordonnées'''
        # Vérifier si les coordonnées sont dans les limites du plateau
        if x < 0 or x >= len(self.grid[0]) or y < 0 or y >= len(self.grid):
            return False
        # Vérifier si la case est un mur
        if isinstance(self.grid[y][x], Wall):
            return False

        return True


    def push_stone(self, dx, dy):
        '''Permet au joueur de pousser une pierre'''
        # Vérifier si le mouvement est valide
        new_x, new_y = self.player.x + dx, self.player.y + dy
        if not self.is_valid_position(new_x, new_y):
            return False  # le mouvement n'est pas valide, retourner False

        # Vérifier si la case suivante contient une pierre poussable
        if not isinstance(self.grid[new_y][new_x], Stone) or not self.grid[new_y][new_x].is_pushable:
            return False  # la case suivante ne contient pas de pierre poussable, retourner False

        # Vérifier la direction du mouvement
        if dy < 0:
            return False  # le mouvement vers le haut n'est pas autorisé

        # Vérifier si la case suivante après la pierre est valide
        new_stone_x = new_x + dx
        new_stone_y = new_y + dy
        if not self.is_valid_position(new_stone_x, new_stone_y) or isinstance(self.grid[new_stone_y][new_stone_x], Stone):
            return False  # la case suivante après la pierre n'est pas valide, retourner False

        # Pousser la pierre
        self.grid[new_stone_y][new_stone_x] = Stone(new_stone_x, new_stone_y)
        self.grid[new_y][new_x] = Empty(new_x, new_y)

        return True  # le mouvement est valide, retourner True


    def center_view(self, view_width, view_height):
        # Calculer les coordonnées pour centrer la vue sur le joueur
        pass


class TestBoard(unittest.TestCase):
    def setUp(self):
        self.board = Board(5, 5, level_path)
        self.board.grid[1][1] = Coin(1, 1)
        self.board.grid[3][3] = Coin(3, 3)

    def test_piece_positions(self):
        self.assertEqual(self.board.grid[1][1].x, 1)
        self.assertEqual(self.board.grid[1][1].y, 1)
        self.assertEqual(self.board.grid[3][3].x, 3)
        self.assertEqual(self.board.grid[3][3].y, 3)

    def test_push_stone_valid_movement(self):
        self.board.player.x = 2
        self.board.player.y = 2
        self.assertTrue(self.board.push_stone(1, 0))
        self.assertIsInstance(self.board.grid[2][3], Stone)
        self.assertIsInstance(self.board.grid[2][2], Empty)

    def test_push_stone_invalid_movement(self):
        self.board.player.x = 2
        self.board.player.y = 2
        self.assertFalse(self.board.push_stone(-1, 0))  # Invalid direction
        self.assertFalse(self.board.push_stone(0, 1))   # Not a pushable stone
        self.assertFalse(self.board.push_stone(1, 1))   # Stone movement blocked


if __name__ == '__main__':
    unittest.main()