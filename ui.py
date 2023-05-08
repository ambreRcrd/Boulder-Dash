import copy
import numpy as np
import pygame

from game import *

# Initialiser Pygame
pygame.init()

# Définir la taille de la fenêtre
screen_width, screen_height = 1000, 600
screen = pygame.display.set_mode((screen_width, screen_height))

# Définir le titre de la fenêtre
pygame.display.set_caption("BOULDER DASH")

# Affichez un fond d'écran blanc
background_color = (150, 150, 150)
screen.fill(background_color)

# Importation d'un niveau
level_path = "/Users/ambrericouard/Desktop/boulder_dash/level_test.txt"
board = Board(screen_width, screen_height, level_path)
grid = board.grid
board.apply_gravity(board.grid) # On applique la gravité au niveau avant même que le jeu commence
board.to_list_grid(grid) # Affichage python

# Chargement des images
player = pygame.image.load('/Users/ambrericouard/Desktop/boulder_dash/bonhomme.png') # joueur
brick = pygame.image.load('/Users/ambrericouard/Desktop/boulder_dash/brick.png') # brique
wall = pygame.image.load('/Users/ambrericouard/Desktop/boulder_dash/wall.png') # mur
stone = pygame.image.load('/Users/ambrericouard/Desktop/boulder_dash/stone.png') # pierre
coin = pygame.image.load('/Users/ambrericouard/Desktop/boulder_dash/coin.png') # piece

# Tailles des icônes
nb_lignes, nb_colonnes = len(grid), len(grid[0])
size_x, size_y = screen_width/nb_colonnes, screen_height/nb_lignes

# Redimensionner les images
player = pygame.transform.scale(player, (size_x, size_y))
brick = pygame.transform.scale(brick, (size_x, size_y))
wall = pygame.transform.scale(wall, (size_x, size_y))
stone = pygame.transform.scale(stone, (size_x, size_y))
coin = pygame.transform.scale(coin, (size_x, size_y))

# Création du joueur
bonhomme = board.player

# Coordonnées réelles du joueur
player_x, player_y = bonhomme.y * size_x, bonhomme.x * size_y
old_player_x, old_player_y = player_x, player_y
i_old_player_x, i_old_player_y = bonhomme.x, bonhomme.y

# Dictionnaire de correspondance des symboles des icônes avec leur image d'icône
icone_correspondings = {
    '@': player,
    'b': brick,
    'w': wall,
    's': stone,
    'c': coin,
}

# Affichage des icônes
def print_grid(grid):
    for y in range(nb_lignes):
        for x in range(nb_colonnes):
            icone = grid[y][x]
            if icone.id != ' ':
                image = icone_correspondings[icone.id]
                x_coord, y_coord = x * size_x, y * size_y
                screen.blit(image, (x_coord, y_coord))
                pygame.display.update()
print_grid(grid)

def try_gravity(old_grid,grid):
    if old_grid != grid:
        to_erase = board.moved_icone(old_grid, grid)
        for coord in to_erase:
            x_coord, y_coord = coord[0] * size_x, coord[1] * size_y
            screen.fill(background_color, (x_coord, y_coord, size_x, size_y))
    pygame.display.update()

def print_gravity(grid):
    old_grid = copy.deepcopy(grid)
    grid = board.apply_gravity(old_grid)
    print_grid(grid)
    try_gravity(old_grid, grid)

# Chargement de la police
font = pygame.font.Font(None, 36)

# Temps de jeu
start_time = pygame.time.get_ticks()
game_time = 0
game_time_limit = 150



# Boucle principale du jeu
running = True
while running:
    # Calcul du temps écoulé depuis le début du jeu et vérification si le temps imparti est écoulé
    game_time = (pygame.time.get_ticks() - start_time) // 1000  # en secondes
    if game_time >= game_time_limit:
        running = False

    # Apply gravity
    print_gravity(grid)

    board.to_list_grid(grid)

    # Gestion des événements
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            # Détection des touches enfoncées
            if event.key == pygame.K_LEFT:
                if not grid[bonhomme.y][bonhomme.x-1].is_solid:
                    bonhomme.go_left()
            elif event.key == pygame.K_RIGHT:
                if not grid[bonhomme.y][bonhomme.x+1].is_solid:
                    bonhomme.go_right()
            elif event.key == pygame.K_UP:
                if not grid[bonhomme.y-1][bonhomme.x].is_solid:
                    bonhomme.go_up()
            elif event.key == pygame.K_DOWN:
                if not grid[bonhomme.y+1][bonhomme.x].is_solid:
                    bonhomme.go_down()

            # Le nombre de pièces ramassées est comptabilisé
            if grid[bonhomme.y][bonhomme.x].id == 'c':
                bonhomme.coins += 1

            # Mettre à jour la grille
            grid[i_old_player_y][i_old_player_x] = Empty(i_old_player_x, i_old_player_y)
            grid[bonhomme.y][bonhomme.x] = Player(bonhomme.x, bonhomme.y)

            # Supprime le joueur de son ancienne position
            player_x, player_y = bonhomme.x * size_x, bonhomme.y * size_y
            screen.fill(background_color, (old_player_x, old_player_y, player.get_width(), player.get_height()))

            # Afficher l'image du personnage à sa nouvelle position
            screen.fill(background_color, (player_x, player_y, player.get_width(), player.get_height()))  # Supprime les icônes situées à la nouvelle position du joueur
            screen.blit(player, (player_x, player_y))

            # Apply gravity
            print_gravity(grid)

            board.to_list_grid(grid)

            # Affichage du score sur l'écran
            score_text = font.render("Score: {}".format(bonhomme.coins), True, (255, 255, 255))
            screen.fill(background_color, (10, 10, score_text.get_width(), score_text.get_height()))
            screen.blit(score_text, (10, 10))

            # Affichage du temps restant
            time_text = font.render("Time: {:02d}".format(game_time_limit - game_time), True, (255, 255, 255))
            screen.fill(background_color, (150, 10, time_text.get_width(), time_text.get_height()))
            screen.blit(time_text, (150, 10))

            old_player_x, old_player_y = player_x, player_y
            i_old_player_x, i_old_player_y = bonhomme.x, bonhomme.y

            # Rafraîchir l'écran
            pygame.display.flip()


# Quitter Pygame
pygame.quit()