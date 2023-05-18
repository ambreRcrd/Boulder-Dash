from button import Button
import copy
import numpy as np
import pygame

from game import *


'''Initialiser Pygame'''
pygame.init()


'''Crée la fenêtre graphique'''
screen_width, screen_height = 1000, 600 # Définir la taille de la fenêtre
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("BOULDER DASH") # Définir le titre de la fenêtre
background_color = (150, 150, 150)
screen.fill(background_color) # Affichez un fond d'écran gris
font = pygame.font.Font(None, 36) # Chargement de la police


def import_level(level_path):
    '''Importation d'un niveau'''
    board = Board(screen_width, screen_height, level_path)
    grid = board.grid
    board.apply_gravity(grid)  # On applique la gravité au niveau avant même que le jeu commence
    board.to_list_grid(grid)  # Affichage python de la grille
    return board, grid, board.player

board, grid, bonhomme = import_level("level_test.txt")


'''Icônes de la grille'''
icon_paths = {
    '@': 'bonhomme.png',
    'b': 'brick.png',
    'w': 'wall.png',
    's': 'stone.png',
    'c': 'coin.png',
}

nb_lignes, nb_colonnes = len(grid), len(grid[0])
size_x, size_y = screen_width / nb_colonnes, screen_height / nb_lignes # Taille des cases de la grille et des icônes

icons = {k: pygame.transform.scale(pygame.image.load(v), (size_x, size_y))
         for k, v in icon_paths.items()}

player_x, player_y = bonhomme.x * size_x, bonhomme.y * size_y # Coordonnées réelles du joueur
old_player_x, old_player_y = player_x, player_y
i_old_player_x, i_old_player_y = bonhomme.x, bonhomme.y # Coordonnées indicielles du joueur


'''Icônes du menu de pause'''
play_img = pygame.image.load("play_bouton.png").convert_alpha() #Chargement des images bouton
replay_img = pygame.image.load("replay_bouton.png").convert_alpha()
exit_img = pygame.image.load("exit_bouton.png").convert_alpha()

play_button = Button(300, 125, play_img, 1) #Création boutons du menu pause
replay_button = Button(300, 250, replay_img, 1)
exit_button = Button(300, 375, exit_img, 1)


def print_grid(grid):
    '''Affichage de la grille'''
    for y, row in enumerate(grid):
        for x, icone in enumerate(row):
            if icone.id != ' ':
                image = icons[icone.id]
                x_coord, y_coord = x * size_x, y * size_y
                screen.blit(image, (x_coord, y_coord))
    pygame.display.update()

print_grid(grid)


def try_gravity(old_grid, grid):
    '''Mise à jour de l'affichage si la gravité modifie la grille'''
    if old_grid != grid:
        to_erase = board.moved_icone(old_grid, grid)
        erase_rects = [pygame.Rect(coord[0] * size_x, coord[1] * size_y, size_x, size_y) for coord in to_erase]
        for rect in erase_rects:
            screen.fill(background_color, rect)


'''Constantes de la boucle principale du jeu'''
KEY_SPACE = pygame.K_SPACE
KEY_LEFT = pygame.K_LEFT
KEY_RIGHT = pygame.K_RIGHT
KEY_UP = pygame.K_UP
KEY_DOWN = pygame.K_DOWN
KEYDOWN = pygame.KEYDOWN
QUIT = pygame.QUIT


'''Gestion des dépalcements du joueur'''
def movement_variables():
    global moving_coord
    moving_coord = {
        KEY_LEFT: (lambda y, x: (y, x - 1), bonhomme.go_left),
        KEY_RIGHT: (lambda y, x: (y, x + 1), bonhomme.go_right),
        KEY_UP: (lambda y, x: (y - 1, x), bonhomme.go_up),
        KEY_DOWN: (lambda y, x: (y + 1, x), bonhomme.go_down)
    }

movement_variables()

def move():
    '''Déplace le joueur'''
    moved = False
    for key, (get_coords, movement) in moving_coord.items():
        if event.key == key:
            y, x = get_coords(bonhomme.y, bonhomme.x)
            icone = grid[y][x]
            if not icone.is_solid:
                movement()
                if icone.id == 'c':
                    bonhomme.get_coin()  # Le nombre de pièces ramassées est comptabilisé
                moved = True
                break
    return moved


def update_score():
    '''Met à jour le score du joueur'''
    score_text = font.render("Score: {}".format(bonhomme.coins), True, (255, 255, 255))
    screen.fill(background_color, (10, 10, score_text.get_width(), score_text.get_height()))
    screen.blit(score_text, (10, 10))


def update_time():
    '''Met à jour le temps restant'''
    game_time = (pygame.time.get_ticks() - start_time) // 1000
    time_remaining = game_time_limit - game_time
    time_text = font.render("Time: {:02d}".format(time_remaining), True, (255, 255, 255))
    time_text_rect = time_text.get_rect(topleft=(150, 10))

    screen.fill(background_color, time_text_rect)
    screen.blit(time_text, time_text_rect)


'''Initialisations'''
running = True # Le jeu tourne
game_pause = False # Le jeu n'est pas mis en pause

game_time = 0 # Initialisation du temps
game_time_limit = 110 # Temps de jeu
start_time = pygame.time.get_ticks() # Temps courant


'''Boucle principale du jeu'''
while running:
    if game_pause:
        # Boucle de pause
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
                break
            elif event.type == KEYDOWN:
                if event.key == KEY_SPACE:
                    game_pause = False
                    break

        if not game_pause:
            screen.fill(background_color)
            continue

        if play_button.draw(screen):
            game_pause = False
            screen.fill(background_color)
            continue

        if exit_button.draw(screen):
            running = False
            continue

        if replay_button.draw(screen):
            # Réinitialisation du jeu
            board, grid, bonhomme = import_level("level_test.txt")
            player_x, player_y = bonhomme.x * size_x, bonhomme.y * size_y
            old_player_x, old_player_y = player_x, player_y
            i_old_player_x, i_old_player_y = bonhomme.x, bonhomme.y
            print_grid(grid)
            start_time = pygame.time.get_ticks()
            game_pause = False
            screen.fill(background_color)

            movement_variables()  # Réinitialisation des variables de mouvement

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

        for event in pygame.event.get():
            if event.type == QUIT:
                running = False

            elif event.type == KEYDOWN:
                if event.key == KEY_SPACE:
                    game_pause = True
                elif event.key in moving_coord.keys():
                    move()

        # Mettre à jour la grille
        grid[i_old_player_y][i_old_player_x] = Empty(i_old_player_x, i_old_player_y)
        grid[bonhomme.y][bonhomme.x] = Player(bonhomme.x, bonhomme.y)

        # Supprime le joueur de son ancienne position
        player_x, player_y = bonhomme.x * size_x, bonhomme.y * size_y
        erase_rect = pygame.Rect(old_player_x, old_player_y, size_x, size_y)
        screen.fill(background_color, erase_rect)

        # Afficher l'image du personnage à sa nouvelle position
        player_rect = pygame.Rect(player_x, player_y, size_x, size_y)
        screen.fill(background_color, player_rect)
        player = icons.get('@')
        screen.blit(player, player_rect)

        # Apply gravity
        old_grid = copy.deepcopy(grid)
        board.apply_gravity(grid)
        try_gravity(old_grid, grid)

        old_player_x, old_player_y = player_x, player_y
        i_old_player_x, i_old_player_y = bonhomme.x, bonhomme.y

        update_score()  # Affichage du score sur l'écran
        update_time()  # Affichage du temps restant

        pygame.display.flip()  # Rafraîchir l'écran

pygame.quit()  # Quitter Pygame
