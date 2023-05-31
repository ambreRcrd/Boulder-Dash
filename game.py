import copy
import numpy as np
import unittest

level_path = "level_test.txt" # Import d'un niveau


class Icone:
    def __init__(self, x, y, id, is_solid, is_gravity_affected, is_pushable):
        self.x = x
        self.y = y
        self.id = id
        self.is_solid = is_solid # Détermine si l'icône peut être traversée (booléen)
        self.is_gravity_affected = is_gravity_affected # Détermine si l'icône est affectée par la gravité (booléen)
        self.is_pushable = is_pushable # Détermine si l'icône peut être poussée (booléen)


class Wall(Icone):
    def __init__(self, x, y):
        super().__init__(x, y, 'w', True, False, False)


class Trap(Icone):
    def __init__(self, x, y):
        super().__init__(x, y, 't', False, False, False)


class Coin(Icone):
    def __init__(self, x, y):
        super().__init__(x, y, 'c', False, True, True)


class Brick(Icone):
    def __init__(self, x, y):
        super().__init__(x, y, 'b', False, False, False)


class Stone(Icone):
    def __init__(self, x, y):
        super().__init__(x, y, 's', True, True, True)



class Empty(Icone):
    def __init__(self, x, y):
        super().__init__(x, y, ' ', False, False, False)


class Player(Icone):
    def __init__(self, x, y):
        super().__init__(x, y, '@', True, False, False)
        self.coins = 0 # le joueur commence avec 0 diamants

    def update_position(self, new_x, new_y):
        """
        Permet de déplacer le joueur
        """
        self.x = new_x
        self.y = new_y

    def get_coin(self):
        """
        Permet d'augmenter le score de 1 lorsqu'une pièce est ramassée
        """
        self.coins += 1


class Board:
    def __init__(self, width, height, level_path):
        self.width = width
        self.height = height
        self.level_path = level_path # Charge le niveau courant
        self.class_correspondings = { # Associe à chaque symbole sa classe correspondante
            '@': Player,
            'b': Brick,
            'w': Wall,
            's': Stone,
            'c': Coin,
            't': Trap,
            ' ': Empty
        }
        self.grid = self.create_grid() # Génère la grille
        self.player = Player(self.get_icone_coord('@')[0], self.get_icone_coord('@')[1]) # Crée le joueur

    def apply_gravity(self, grid):
        """
        Applique la gravité à la grille. La fonction est récursive pour savoir si une icône déjà tombée pourra retomber ou non
        """
        new_grid = [row[:] for row in grid]  # Crée une copie de la grille originale

        def apply_gravity_recursive(y, x):
            if new_grid[y][x].is_gravity_affected:
                if y + 1 < len(new_grid) and new_grid[y + 1][x].id == " ":
                    icone = new_grid[y][x].id
                    class_corres = self.class_correspondings[icone]
                    new_grid[y + 1][x] = class_corres(x, y + 1)
                    new_grid[y][x] = Empty(x, y)
                    apply_gravity_recursive(y + 1, x)  # Appel récursif avec la nouvelle position de la pierre

        for y in range(len(new_grid) - 1, -1, -1):
            for x in range(len(new_grid[0])):
                apply_gravity_recursive(y, x)

        return new_grid

    def moved_icone(self, old_grid, grid):
        """
        Renvoie une liste des icônes à supprimer, qui se trouvaient dans l'ancienne grille mais ne le sont plus dans la nouvelle
        """
        to_erase = []
        for y in range(len(old_grid)):
            for x in range(len(old_grid[0])):
                if old_grid[y][x].id != grid[y][x].id:
                    to_erase.append([x, y])  # Ajouter les coordonnées de l'icône à supprimer
        return to_erase

    def create_grid(self):
        """
        Charge un niveau et le stocke dans une grille (liste de listes)
        """
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
        """
        Permet l'affichage de la grille avec les icônes à la place des objets (améliore la lisibilité). Utile seulement pour le développement
        """
        nb_lignes = len(grid)
        nb_colonnes = len(grid[0])
        new_grid = np.empty((nb_lignes, nb_colonnes), dtype=object)

        for y in range(nb_lignes):
            for x in range(nb_colonnes):
                new_grid[y][x] = grid[y][x].id
        return new_grid.tolist()

    def get_icone_coord(self, icone_symb):
        """
        Permet d'accéder aux coordonnées du joueur
        """
        for y, row in enumerate(self.grid):
            for x, icone in enumerate(row):
                if icone.id == icone_symb:
                    return icone.x, icone.y
        return 0, 0

    def is_valid_position(self, x, y):
        """
        Vérifiz la conformité des coordonnées
        """
        if x < 0 or x >= len(self.grid[0]) or y < 0 or y >= len(self.grid): # Vérifier si les coordonnées sont dans les limites du plateau
            return False

        if isinstance(self.grid[y][x], Wall): # Vérifier si la case est un mur
            return False

        return True

    def push_stone(self, dx, dy):
        """
        Permet au joueur de pousser une pierre
        """
        new_x, new_y = self.player.x + dx, self.player.y + dy
        if not self.is_valid_position(new_x, new_y):
            return False  # Le mouvement n'est pas valide, retourner False

        if not isinstance(self.grid[new_y][new_x], Stone) or not self.grid[new_y][new_x].is_pushable: # Vérifier si la case suivante contient une pierre poussable
            return False  # La case suivante ne contient pas de pierre poussable, retourner False

        if dy < 0: # Vérifier la direction du mouvement
            return False  # Le mouvement vers le haut n'est pas autorisé

        new_stone_x = new_x + dx
        new_stone_y = new_y + dy
        if not self.is_valid_position(new_stone_x, new_stone_y) or isinstance(self.grid[new_stone_y][new_stone_x], Stone): # Vérifier si la case suivante après la pierre est valide
            return False  # La case suivante après la pierre n'est pas valide, retourner False

        self.grid[new_stone_y][new_stone_x] = Stone(new_stone_x, new_stone_y) # Pousser la pierre
        self.grid[new_y][new_x] = Empty(new_x, new_y)

        return True  # Le mouvement est valide, retourner True


    def center_view(self, view_width, view_height):
        """
        Calculer les coordonnées pour centrer la vue sur le joueur
        """
        pass


class BoardTests(unittest.TestCase):
    def setUp(self):
        self.board_1 = Board(5, 4, "level_test_unitaire1.txt")
        self.board_2 = Board(3, 3, "level_test_unitaire2.txt")

    def test_create_grid(self):
        expected_grid = [
            [Wall(0, 0), Wall(1, 0), Wall(2, 0), Wall(3, 0), Wall(4, 0)],
            [Wall(0, 1), Player(1, 1), Stone(2, 1), Brick(3, 1), Wall(4, 1)],
            [Wall(0, 2), Coin(1, 2), Empty(2, 2), Wall(3, 2), Wall(4, 2)],
            [Wall(0, 3), Wall(1, 3), Wall(2, 3), Wall(3, 3), Wall(4, 3)]
        ]
        actual_grid = self.board_1.grid # Premier cas testé

        for y in range(len(actual_grid)):
            for x in range(len(actual_grid[y])):
                self.assertEqual(actual_grid[y][x].id, expected_grid[y][x].id)

        expected_grid = [
            [Wall(0, 0), Wall(1, 0), Wall(2, 0)],
            [Wall(0, 1), Player(1, 1), Wall(2, 1)],
            [Wall(0, 2), Wall(1, 2), Wall(2, 3)]
        ]
        actual_grid = self.board_2.grid # Deuxième cas testé

        for y in range(len(actual_grid)):
            for x in range(len(actual_grid[y])):
                self.assertEqual(actual_grid[y][x].id, expected_grid[y][x].id)

    def test_apply_gravity(self):
        grid = [
            [Wall(0, 0), Wall(1, 0), Wall(2, 0), Wall(3, 0), Wall(4, 0)],
            [Wall(0, 1), Player(1, 1), Stone(2, 1), Brick(3, 1), Wall(4, 1)],
            [Wall(0, 2), Coin(1, 2), Empty(2, 2), Wall(3, 2), Wall(4, 2)],
            [Wall(0, 3), Wall(1, 3), Wall(2, 3), Wall(3, 3), Wall(4, 3)]
        ]
        expected_grid = [
            [Wall(0, 0), Wall(1, 0), Wall(2, 0), Wall(3, 0), Wall(4, 0)],
            [Wall(0, 1), Player(1, 1), Empty(2, 1), Brick(3, 1), Wall(4, 1)],
            [Wall(0, 2), Coin(1, 2), Stone(2, 2), Wall(3, 2), Wall(4, 2)],
            [Wall(0, 3), Wall(1, 3), Wall(2, 3), Wall(3, 3), Wall(4, 3)]
        ]
        result = self.board_1.apply_gravity(grid) # Premier cas testé

        for y in range(len(result)):
            for x in range(len(result[y])):
                self.assertEqual(result[y][x].id, expected_grid[y][x].id)

        grid = [
            [Wall(0, 0), Wall(1, 0), Wall(2, 0)],
            [Wall(0, 1), Player(1, 1), Wall(2, 1)],
            [Wall(0, 2), Wall(1, 2), Wall(2, 3)]
        ]

        expected_grid = [
            [Wall(0, 0), Wall(1, 0), Wall(2, 0)],
            [Wall(0, 1), Player(1, 1), Wall(2, 1)],
            [Wall(0, 2), Wall(1, 2), Wall(2, 3)]
        ]

        result = self.board_2.apply_gravity(grid) # Deuxième cas testé

        for y in range(len(result)):
            for x in range(len(result[y])):
                self.assertEqual(result[y][x].id, expected_grid[y][x].id)

    def test_moved_icone(self):
        old_grid = [
            [Wall(0, 0), Wall(1, 0), Wall(2, 0), Wall(3, 0), Wall(4, 0)],
            [Wall(0, 1), Player(1, 1), Stone(2, 1), Brick(3, 1), Wall(4, 1)],
            [Wall(0, 2), Coin(1, 2), Empty(2, 2), Wall(3, 2), Wall(4, 2)],
            [Wall(0, 3), Wall(1, 3), Wall(2, 3), Wall(3, 3), Wall(4, 3)]
        ]
        new_grid = [
            [Wall(0, 0), Wall(1, 0), Wall(2, 0), Wall(3, 0), Wall(4, 0)],
            [Wall(0, 1), Player(1, 1), Empty(2, 1), Brick(3, 1), Wall(4, 1)],
            [Wall(0, 2), Coin(1, 2), Stone(2, 2), Wall(3, 2), Wall(4, 2)],
            [Wall(0, 3), Wall(1, 3), Wall(2, 3), Wall(3, 3), Wall(4, 3)]
        ]
        expected_result = [[2, 1], [2, 2]]
        result = self.board_1.moved_icone(old_grid, new_grid)
        self.assertEqual(result, expected_result)

    def test_get_icone_coord(self):
        x, y = self.board_1.get_icone_coord('@')
        self.assertEqual(x, 1)
        self.assertEqual(y, 1)

    def test_is_valid_position(self):
        # Vérifier des positions valides
        self.assertTrue(self.board_1.is_valid_position(2, 1))  # Position vide
        self.assertTrue(self.board_1.is_valid_position(1, 2))  # Pièce

        # Vérifier des positions invalides
        self.assertFalse(self.board_1.is_valid_position(-1, 2))  # Position en dehors du plateau (gauche)
        self.assertFalse(self.board_1.is_valid_position(5, 2))  # Position en dehors du plateau (droite)
        self.assertFalse(self.board_1.is_valid_position(2, -1))  # Position en dehors du plateau (haut)
        self.assertFalse(self.board_1.is_valid_position(2, 4))  # Position en dehors du plateau (bas)
        self.assertFalse(self.board_1.is_valid_position(0, 2))  # Position contenant un mur (non valide)

    def test_push_stone(self):
        # Vérifier un mouvement de pierre valide vers le bas
        self.assertTrue(self.board_1.push_stone(1, 0))  # Pousser la pierre vers la droite

        expected_grid = [
            [Wall(0, 0), Wall(1, 0), Wall(2, 0), Wall(3, 0), Wall(4, 0)],
            [Wall(0, 1), Player(1, 1), Empty(2, 1), Stone(3, 1), Wall(4, 1)],
            [Wall(0, 2), Coin(1, 2), Empty(2, 2), Wall(3, 2), Wall(4, 2)],
            [Wall(0, 3), Wall(1, 3), Wall(2, 3), Wall(3, 3), Wall(4, 3)]
        ]

        for y in range(len(expected_grid)):
            for x in range(len(expected_grid[y])):
                self.assertEqual(self.board_1.grid[y][x].id, expected_grid[y][x].id)

        # Vérifier un mouvement de pierre non valide (vers le haut)
        self.assertFalse(self.board_1.push_stone(0, -1))  # Tentative de pousser la pierre vers le haut
        for y in range(len(expected_grid)): # La grille ne doit pas avoir changé
            for x in range(len(expected_grid[y])):
                self.assertEqual(self.board_1.grid[y][x].id, expected_grid[y][x].id)

        # Vérifier un mouvement de pierre non valide (vers la droite)
        self.assertFalse(self.board_1.push_stone(1, 0))  # Tentative de pousser la pierre vers la droite
        for y in range(len(expected_grid)):  # La grille ne doit pas avoir changé
            for x in range(len(expected_grid[y])):
                self.assertEqual(self.board_1.grid[y][x].id, expected_grid[y][x].id)

        # Vérifier un mouvement de pierre non valide (vers le bas, obstruction)
        self.assertFalse(self.board_1.push_stone(0, 1))  # Tentative de pousser la pierre vers le bas (obstruction)
        for y in range(len(expected_grid)):  # La grille ne doit pas avoir changé
            for x in range(len(expected_grid[y])):
                self.assertEqual(self.board_1.grid[y][x].id, expected_grid[y][x].id)

        # Vérifier un mouvement de pierre non valide (vers le bas, hors limites)
        self.assertFalse(self.board_1.push_stone(0, 2))  # Tentative de pousser la pierre vers le bas (hors limites)
        for y in range(len(expected_grid)):  # La grille ne doit pas avoir changé
            for x in range(len(expected_grid[y])):
                self.assertEqual(self.board_1.grid[y][x].id, expected_grid[y][x].id)


if __name__ == "__main__":
    unittest.main()