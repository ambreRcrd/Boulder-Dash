import unittest

# Importation d'un niveau
level_path = "/Users/ambrericouard/Desktop/boulder_dash/level_test.txt"

class Piece:
    def __init__(self, x, y, id):
        self.x = x
        self.y = y
        self.is_solid = False # la piece n'est pas solide et peut etre traversee
        self.id = id

class Brick:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.is_solid = True  # la brique est solide et ne peut pas être traversée
        self.is_gravity_affected = False  # la brique n'est pas affectée par la gravité

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.is_solid = True  # le joueur est solide et ne peut pas être traversé
        self.is_gravity_affected = True  # le joueur est affecté par la gravité
        self.has_diamonds = 0  # le joueur commence avec 0 diamants

class Diamond:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.is_solid = False  # le diamant n'est pas solide et peut être traversé
        self.is_gravity_affected = True  # le diamant est affecté par la gravité

class Stone:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.is_solid = True  # la pierre est solide et ne peut pas être traversée
        self.is_gravity_affected = True  # la pierre est affectée par la gravité
        self.is_pushable = True  # la pierre peut être poussée par le joueur ou d'autres objets

class Empty:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.is_solid = False  # l'espace vide n'est pas solide et peut être traversé
        self.is_gravity_affected = False  # l'espace vide n'est pas affecté par la gravité


class Board:
    def __init__(self, width, height, level_path):
        self.width = width
        self.height = height
        self.grid = self.create_grid(level_path)
        self.player = Player(self.get_player_coord()[0], self.get_player_coord()[1])  # initialiser le joueur en haut à gauche

    def update(self):
        # Mettre à jour la position des pièces soumises à la gravité
        for y in range(self.height - 1, -1, -1):  # parcourir les colonnes de bas en haut
            for x in range(self.width):
                if isinstance(self.grid[x][y], Falling):
                    self.move_falling_piece(x, y)

    def create_grid(self, level_path):
        with open(level_path, "r") as f:
            return [list(line.strip()) for line in f.readlines()]

    def get_player_coord(self):
        x_coord, y_coord = 0, 0
        nb_lignes, nb_colonnes = len(self.grid), len(self.grid[0])
        size_x, size_y = self.width / nb_colonnes, self.height / nb_lignes
        for y in range(nb_colonnes):
            for x in range(nb_lignes):
                if self.grid[x][y] == '@':
                    return x_coord, y_coord  # position initiale du joueur
                y_coord += size_y
            x_coord += size_x
            y_coord = 0
        return 0, 0

    def move_falling_piece(self, x, y):
        # Vérifier si la pièce peut tomber d'un cran
        if not self.is_valid_position(x, y + 1):
            return  # la pièce ne peut pas tomber, ne rien faire

        # Faire tomber la pièce d'un cran
        self.grid[x][y + 1] = self.grid[x][y]
        self.grid[x][y] = Empty(x, y)

        # Si la pièce est une pierre et qu'elle est tombée sur un diamant, le collecter
        if isinstance(self.grid[x][y + 1], Diamond):
            self.player.has_diamonds += 1
            self.grid[x][y + 1] = Empty(x, y + 1)

        # Si la pièce est une pierre et qu'elle est tombée sur le joueur, le tuer
        if isinstance(self.grid[x][y + 1], Player):
            self.player.is_alive = False

    def is_valid_position(self, x, y):
        # Vérifier si la position est à l'intérieur du plateau
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return False

        # Vérifier si la case est traversable
        return not self.grid[x][y].is_solid

    def move_player(self, dx, dy):
        # Vérifier si le mouvement est valide
        new_x = self.player.x + dx
        new_y = self.player.y + dy
        if not self.is_valid_position(new_x, new_y):
            return False  # le mouvement n'est pas valide, retourner False

        # Déplacer le joueur
        self.grid[self.player.x][self.player.y] = Empty(self.player.x, self.player.y)  # effacer la case précédente du joueur
        self.player.x = new_x
        self.player.y = new_y
        self.grid[self.player.x][self.player.y] = self.player  # placer le joueur sur la nouvelle case

        # Si le joueur a collecté un diamant, l'ajouter à son inventaire
        if isinstance(self.grid[self.player.x][self.player.y], Diamond):
            self.player.has_diamonds += 1
            self.grid[self.player.x][self.player.y] = Empty(self.player.x, self.player.y)  # effacer le diamant de la case

        return True  # le mouvement est valide, retourner True

    def push_stone(self, dx, dy):
        # Vérifier si le mouvement est valide
        new_x = self.player.x + dx
        new_y = self.player.y + dy
        if not self.is_valid_position(new_x, new_y):
            return False  # le mouvement n'est pas valide, retourner False

        # Vérifier si la case suivante contient une pierre poussable
        if not isinstance(self.grid[new_x][new_y], Stone) or not self.grid[new_x][new_y].is_pushable:
            return False  # la case suivante ne contient pas de pierre poussable, retourner False

        # Vérifier si la case suivante après la pierre est valide
        new_stone_x = new_x + dx
        new_stone_y = new_y + dy
        if not self.is_valid_position(new_stone_x, new_stone_y):
            return False  # la case suivante après la pierre n'est pas valide, retourner False

        # Pousser la pierre
        self.grid[new_stone_x][new_stone_y] = self.grid[new_x][new_y]
        self.grid[new_x][new_y] = Empty(new_x, new_y)

        # Déplacer le joueur
        self.grid[self.player.x][self.player.y] = Empty(self.player.x, self.player.y)  # effacer la case précédente du joueur
        self.player.x = new_x
        self.player.y = new_y
        self.grid[self.player.x][self.player.y] = self.player  # placer le joueur sur la nouvelle case

        # Si le joueur a collecté un diamant, l'ajouter à son inventaire
        if isinstance(self.grid[self.player.x][self.player.y], Diamond):
            self.player.has_diamonds += 1
            self.grid[self.player.x][self.player.y] = Empty(self.player.x, self.player.y)  # effacer le diamant de la case

        return True  # le mouvement est valide, retourner True

    def center_view(self, view_width, view_height):
        # Calculer les coordonnées pour centrer la vue sur le joueur
        pass

class TestBoard(unittest.TestCase):
    def setUp(self):
        self.board = Board(5, 5, level_path)
        self.board.grid[1][1] = Piece(1, 1, 1)
        self.board.grid[3][3] = Piece(3, 3, 2)

    def test_piece_positions(self):
        self.assertEqual(self.board.grid[1][1].x, 1)
        self.assertEqual(self.board.grid[1][1].y, 1)
        self.assertEqual(self.board.grid[3][3].x, 3)
        self.assertEqual(self.board.grid[3][3].y, 3)

    def test_piece_ids(self):
        self.assertEqual(self.board.grid[1][1].id, 1)
        self.assertEqual(self.board.grid[3][3].id, 2)
