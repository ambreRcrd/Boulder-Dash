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
grid = board.create_grid()

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

# Dictionnaire de correspondance des symboles des icônes avec leur image d'icône
icone_correspondings = {
    '@': player,
    'b': brick,
    'w': wall,
    's': stone,
    'c': coin,
}

# Affichage des icônes
x_coord, y_coord = 0, 0
for y in range(nb_colonnes):
    for x in range(nb_lignes):
        icone = grid[x][y]
        if icone.id != ' ':
            image = icone_correspondings[icone.id]
            x_coord, y_coord = icone.y* size_x, icone.x * size_y
            screen.blit(image, (x_coord, y_coord))

bonhomme = board.player

# Coordonnées du joueur
player_x, player_y = bonhomme.y * size_x, bonhomme.x * size_y
old_player_x, old_player_y = player_x, player_y
i_old_player_x, i_old_player_y = bonhomme.x, bonhomme.y

# Mettez à jour l'affichage pour afficher l'image
pygame.display.update()

# chargement de la police
font = pygame.font.Font(None, 36)

# Temps de jeu
start_time = pygame.time.get_ticks()
game_time = 0
game_time_limit = 150

def to_list_grid(grid): # fonction de test
    new_grid = [[0 for y in range(nb_colonnes)] for x in range(nb_lignes)]
    for y in range(nb_colonnes):
        for x in range(nb_lignes):
            new_grid[x][y] = grid[x][y].id
    print(np.array(new_grid))
    return

to_list_grid(grid)

# Boucle principale du jeu
running = True
while running:
    game_time = (pygame.time.get_ticks() - start_time) // 1000  # en secondes
    # Vérification si le temps imparti est écoulé
    if game_time >= game_time_limit:
        # Fin du jeu ou autre traitement
        running = False
    Board(screen_width, screen_height, level_path)
    # Gestion des événements
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            # Détection des touches enfoncées
            if event.key == pygame.K_LEFT:
                if not grid[bonhomme.x][bonhomme.y-1].is_solid:
                    bonhomme.go_left()
            elif event.key == pygame.K_RIGHT:
                if not grid[bonhomme.x][bonhomme.y+1].is_solid:
                    bonhomme.go_right()
            elif event.key == pygame.K_UP:
                if not grid[bonhomme.x-1][bonhomme.y].is_solid:
                    bonhomme.go_up()
            elif event.key == pygame.K_DOWN:
                if not grid[bonhomme.x+1][bonhomme.y].is_solid:
                    bonhomme.go_down()

            if grid[bonhomme.x][bonhomme.y].id == 'c':
                bonhomme.coins += 1

            grid[i_old_player_x][i_old_player_y] = Empty(i_old_player_x, i_old_player_y)
            grid[bonhomme.x][bonhomme.y] = Player(bonhomme.x, bonhomme.y)
            to_list_grid(grid)

    player_x, player_y = bonhomme.y * size_x, bonhomme.x * size_y
    screen.fill(background_color, (old_player_x, old_player_y, player.get_width(), player.get_height())) # Supprime le joueur de son ancienne position
    screen.fill(background_color, (player_x, player_y, player.get_width(), player.get_height())) # Supprime les icônes situées à la nouvelle position du joueur

    # Afficher l'image du personnage à sa nouvelle position
    screen.blit(player, (player_x, player_y))

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