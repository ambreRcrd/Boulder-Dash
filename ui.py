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
screen.fill((150, 150, 150))

# Importation d'un niveau
level_path = "/Users/ambrericouard/Desktop/boulder_dash/level_test.txt"

with open(level_path, "r") as f:
    grid = np.array([list(line.strip()) for line in f.readlines()])
print(grid)

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
        y_coord += size_y
    x_coord += size_x
    y_coord = 0

# Mettez à jour l'affichage pour afficher l'image
pygame.display.update()

# Vitesse de déplacement du personnage
player_speed = 1

# Boucle principale du jeu
running = True
while running:
    # Gestion des événements
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    Board(screen_width, screen_height, level_path)

    # Détection des touches enfoncées
    keys = pygame.key.get_pressed()

    old_player_x, old_player_y = player_x, player_y

    # Modification des variables de position du personnage en fonction des touches enfoncées
    if keys[pygame.K_LEFT]:
        player_x = old_player_x - player_speed
    if keys[pygame.K_RIGHT]:
        player_x = old_player_x + player_speed
    if keys[pygame.K_UP]:
        player_y = old_player_y - player_speed
    if keys[pygame.K_DOWN]:
        player_y = old_player_y + player_speed

    # Effacer l'emplacement précédent de l'image
    screen.fill((255, 255, 255),
                (old_player_x, old_player_y, player.get_width(), player.get_height()))

    # Afficher l'image du personnage à sa nouvelle position
    screen.blit(player, (player_x, player_y))

    # Rafraîchir l'écran
    pygame.display.flip()

# Quitter Pygame
pygame.quit()