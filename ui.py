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
print(np.array(grid))

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

# Dictionnaire de correspondance des symboles des icônes avec leur icône
symbol_correspondings = {
    '@': player,
    'b': brick,
    'w': wall,
    's': stone,
    'c': coin
}

# Affichage des icônes
x_coord, y_coord = 0, 0
for y in range(nb_colonnes):
    for x in range(nb_lignes):
        icone = grid[x][y]
        if icone != ' ':
            screen.blit(symbol_correspondings[icone], (x_coord,y_coord))
        if icone == '@':
            player_x, player_y = x_coord, y_coord # position initiale du joueur
            i_player_x, i_player_y = y, x
        y_coord += size_y
    x_coord += size_x
    y_coord = 0

# Mettez à jour l'affichage pour afficher l'image
pygame.display.update()

# Vitesse de déplacement du personnage
old_player_x, old_player_y = player_x, player_y
i_old_player_x, i_old_player_y = i_player_x, i_player_y

# Boucle principale du jeu
running = True
while running:
    Board(screen_width, screen_height, level_path)
    # Gestion des événements
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            # Détection des touches enfoncées
            if event.key == pygame.K_LEFT:
                if grid[i_player_y][i_player_x-1] != 'w':
                    player_x = old_player_x - size_x
                    i_player_x = i_old_player_x - 1
            elif event.key == pygame.K_RIGHT:
                if grid[i_player_y][i_player_x + 1] != 'w':
                    player_x = old_player_x + size_x
                    i_player_x = i_old_player_x + 1
            elif event.key == pygame.K_UP:
                if grid[i_player_y - 1][i_player_x] != 'w':
                    player_y = old_player_y - size_y
                    i_player_y = i_old_player_y - 1
            elif event.key == pygame.K_DOWN:
                if grid[i_player_y + 1][i_player_x] != 'w':
                    player_y = old_player_y + size_y
                    i_player_y = i_old_player_y + 1

            grid[i_old_player_y][i_old_player_x] = ' '
            grid[i_player_y][i_player_x] = '@'
            print(np.array(grid))

        screen.fill(background_color, (old_player_x, old_player_y, player.get_width(), player.get_height())) # Supprime le joueur de son ancienne position
        screen.fill(background_color, (player_x, player_y, player.get_width(), player.get_height())) # Supprimer les icônes situées à la nouvelle position du joueur

        # Afficher l'image du personnage à sa nouvelle position
        screen.blit(player, (player_x, player_y))

        old_player_x, old_player_y = player_x, player_y
        i_old_player_x, i_old_player_y = i_player_x, i_player_y

        # Rafraîchir l'écran
        pygame.display.flip()



# Quitter Pygame
pygame.quit()