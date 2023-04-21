import pygame
from game import *

# Initialiser Pygame
pygame.init()

# Définir la taille de la fenêtre
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))

# Définir le titre de la fenêtre
pygame.display.set_caption("BOULDER DASH")

# Chargement de l'image du personnage
character_image = pygame.image.load('/Users/ambrericouard/Desktop/boulder_dash/bonhomme.png')

# Redimensionner l'image
width = 100  # largeur souhaitée
height = 100  # hauteur souhaitée
character_image = pygame.transform.scale(character_image, (width, height))

# Position initiale du personnage
character_x = 50
character_y = 50

# Affichez un fond d'écran blanc
screen.fill((255, 255, 255))

# Mettez à jour l'affichage pour afficher l'image
pygame.display.update()

# Vitesse de déplacement du personnage
character_speed = 5
speed_factor = 3

# Boucle principale du jeu
running = True
while running:
    # Gestion des événements
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    Board(screen_width,screen_height)

    # Détection des touches enfoncées
    keys = pygame.key.get_pressed()

    old_character_x, old_character_y = character_x, character_y

    # Modification des variables de position du personnage en fonction des touches enfoncées
    if keys[pygame.K_LEFT]:
        character_x = old_character_x - character_speed * speed_factor
    if keys[pygame.K_RIGHT]:
        character_x = old_character_x + character_speed * speed_factor
    if keys[pygame.K_UP]:
        character_y = old_character_y - character_speed * speed_factor
    if keys[pygame.K_DOWN]:
        character_y = old_character_y + character_speed * speed_factor

    # Effacer l'emplacement précédent de l'image
    screen.fill((255, 255, 255),
                (old_character_x, old_character_y, character_image.get_width(), character_image.get_height()))

    # Afficher l'image du personnage à sa nouvelle position
    screen.blit(character_image, (character_x, character_y))

    # Rafraîchir l'écran
    pygame.display.flip()

# Quitter Pygame
pygame.quit()