import button
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

def import_niveau(level_path):
    '''Importation d'un niveau'''
    global board, grid, bonhomme
    board = Board(screen_width, screen_height, level_path)
    grid, bonhomme = board.grid, board.player
    board.apply_gravity(board.grid) # On applique la gravité au niveau avant même que le jeu commence
    board.to_list_grid(grid) # Affichage python de la grille
import_niveau("level_test.txt")

# Chargement des images
player = pygame.image.load('bonhomme.png') # Joueur
brick = pygame.image.load('brick.png') # Brique
wall = pygame.image.load('wall.png') # Mur
stone = pygame.image.load('stone.png') # Pierre
coin = pygame.image.load('coin.png') # Piece

# Tailles des icônes
nb_lignes, nb_colonnes = len(grid), len(grid[0])
size_x, size_y = screen_width/nb_colonnes, screen_height/nb_lignes

# Redimensionner les images
player = pygame.transform.scale(player, (size_x, size_y))
brick = pygame.transform.scale(brick, (size_x, size_y))
wall = pygame.transform.scale(wall, (size_x, size_y))
stone = pygame.transform.scale(stone, (size_x, size_y))
coin = pygame.transform.scale(coin, (size_x, size_y))

# Coordonnées réelles du joueur
player_x, player_y = bonhomme.x * size_x, bonhomme.y * size_y
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
    '''Affichage de la grille'''
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
    '''Mise à jour de l'affichage si la gravité modifie la grille'''
    if old_grid != grid:
        to_erase = board.moved_icone(old_grid, grid)
        for coord in to_erase:
            x_coord, y_coord = coord[0] * size_x, coord[1] * size_y
            screen.fill(background_color, (x_coord, y_coord, size_x, size_y))

# Chargement de la police
font = pygame.font.Font(None, 36)

# Temps de jeu
start_time = pygame.time.get_ticks()
game_time = 0
game_time_limit = 110

#Chargement image bouton
play_img = pygame.image.load("play_bouton.png").convert_alpha()
replay_img = pygame.image.load("replay_bouton.png").convert_alpha()
exit_img = pygame.image.load("exit_bouton.png").convert_alpha()

#Création boutons du menu pause
play_button = button.Button(300, 125, play_img, 1)
replay_button = button.Button(300, 250, replay_img, 1)
exit_button = button.Button(300, 375, exit_img, 1)

#Check jeu en pause
game_pause = False

# Boucle principale du jeu
running = True
while running:
    if game_pause:
        # Boucle de pause
        pause_running = True
        while pause_running:
            if play_button.draw(screen):
                pause_running = False
                game_pause = False
                screen.fill(background_color)

            elif exit_button.draw(screen):
                pause_running = False
                running = False

            elif replay_button.draw(screen):
                del grid
                del bonhomme
                del board
                import_niveau("level_test.txt") # On regénère le plateau de jeu
                player_x, player_y = bonhomme.x * size_x, bonhomme.y * size_y
                old_player_x, old_player_y = player_x, player_y
                i_old_player_x, i_old_player_y = bonhomme.x, bonhomme.y
                print_grid(grid)
                start_time = pygame.time.get_ticks()
                pause_running = False
                game_pause = False
                screen.fill(background_color)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pause_running = False
                    running = False

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        pause_running = False
            pygame.display.update()
    else:
        # Calcul du temps écoulé depuis le début du jeu et vérification si le temps imparti est écoulé
        game_time = (pygame.time.get_ticks() - start_time) // 1000  # en secondes
        if game_time >= game_time_limit:
            running = False

        # Apply gravity
        old_grid = copy.deepcopy(grid)
        grid = board.apply_gravity(old_grid)
        try_gravity(old_grid, grid)
        print_grid(grid)

        # Gestion des événements
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                # Détection des touches enfoncées
                if event.key == pygame.K_SPACE:
                    game_pause = True

                elif event.key == pygame.K_LEFT:
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
                old_grid = copy.deepcopy(grid)
                grid = board.apply_gravity(old_grid)
                try_gravity(old_grid, grid)
                print_grid(grid)
                pygame.display.update()

                board.to_list_grid(grid)

                old_player_x, old_player_y = player_x, player_y
                i_old_player_x, i_old_player_y = bonhomme.x, bonhomme.y

    # Affichage du score sur l'écran
    score_text = font.render("Score: {}".format(bonhomme.coins), True, (255, 255, 255))
    screen.fill(background_color, (10, 10, score_text.get_width(), score_text.get_height()))
    screen.blit(score_text, (10, 10))

    # Affichage du temps restant
    time_text = font.render("Time: {:02d}".format(game_time_limit - game_time), True, (255, 255, 255))
    try:
        time_text_w, time_text_h = old_text_size[0], old_text_size[1]
    except NameError:
        time_text_w, time_text_h = time_text.get_width(), time_text.get_height()

    screen.fill(background_color, (150, 10, time_text_w, time_text_h))
    screen.blit(time_text, (150, 10))
    old_text_size = time_text.get_width(), time_text.get_height()

    # Rafraîchir l'écran
    pygame.display.flip()

# Quitter Pygame
pygame.quit()