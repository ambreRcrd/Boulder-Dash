from button import Button
import copy
import numpy as np
import pygame
import pygame_textinput
import sqlite3
from game import *


'''Initialiser Pygame'''
pygame.init()
conn = sqlite3.connect('scores.accdb')

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
text_input = pygame_textinput.TextInputManager


'''Icônes de la grille'''
icon_paths = {
    '@': 'bonhomme.png',
    'b': 'brick.png',
    'w': 'wall.png',
    's': 'stone.png',
    'c': 'coin.png',
    't': 'trap.png',
}

nb_lignes, nb_colonnes = len(grid), len(grid[0])
size_x, size_y = screen_width / nb_colonnes, screen_height / nb_lignes # Taille des cases de la grille et des icônes

icons = {k: pygame.transform.scale(pygame.image.load(v), (size_x, size_y))
         for k, v in icon_paths.items()}

player_x, player_y = bonhomme.x * size_x, bonhomme.y * size_y # Coordonnées réelles du joueur
old_player_x, old_player_y = player_x, player_y
i_old_player_x, i_old_player_y = bonhomme.x, bonhomme.y # Coordonnées indicielles du joueur


'''Icônes du menu de pause'''
titlescr = pygame.image.load("titlescreen.png")
defeat_image = pygame.image.load("defeat.png")
victory_image = pygame.image.load("victory.png")
play_img = pygame.image.load("play_bouton.png").convert_alpha() #Chargement des images bouton
replay_img = pygame.image.load("replay_bouton.png").convert_alpha()
exit_img = pygame.image.load("exit_bouton.png").convert_alpha()

play_button = Button(300, 125, play_img, 1) #Création boutons du menu pause
replay_button = Button(300, 250, replay_img, 1)
exit_button = Button(300, 375, exit_img, 1)
defeat_button = Button(346, 460, exit_img, 1)

#Init stockage scores
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS scores
                  (id INTEGER PRIMARY KEY AUTOINCREMENT,
                   name TEXT,
                   time INTEGER)''')


def print_grid(grid):
    '''Affichage de la grille'''
    for y, row in enumerate(grid):
        for x, icone in enumerate(row):
            if icone.id != ' ':
                image = icons[icone.id]
                x_coord, y_coord = x * size_x, y * size_y
                screen.blit(image, (x_coord, y_coord))

print_grid(grid)


def try_gravity(old_grid, grid):
    '''Mise à jour de l'affichage si la gravité modifie la grille'''
    if old_grid != grid:
        to_erase = board.moved_icone(old_grid, grid)
        for coord in to_erase:
            erase_rect = pygame.Rect(coord[0] * size_x, coord[1] * size_y, size_x, size_y)
            screen.fill(background_color, erase_rect)


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
        KEY_LEFT: lambda x, y: (x - 1, y),
        KEY_RIGHT: lambda x, y: (x + 1, y),
        KEY_UP: lambda x, y: (x, y - 1),
        KEY_DOWN: lambda x, y: (x, y + 1),
    }

movement_variables()

def move():
    '''Déplace le joueur'''
    moved = False
    for key, coords in moving_coord.items():
        if event.key == key:
            new_x, new_y = coords(bonhomme.x, bonhomme.y)
            icone = grid[new_y][new_x]

            if isinstance(icone, Stone):
                # Tentative de pousser une pierre
                dx, dy = new_x - bonhomme.x, new_y - bonhomme.y
                pushed = board.push_stone(dx, dy)
                if pushed:
                    bonhomme.update_position(new_x, new_y)
                    moved = True
                break

            elif not icone.is_solid:
                bonhomme.update_position(new_x, new_y)
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

def level_up(levelnumber,levelpath2,levelpath3):
    if levelnumber == 1:
        return import_level(levelpath2)
    if levelnumber == 2:
         return import_level(levelpath3)


'''Initialisations'''
running = True # Le jeu tourne
game_pause = False # Le jeu n'est pas mis en pause
game_defeat = False
starter = False

levelnumber = 1
game_time = 0 # Initialisation du temps
game_time_limit = 150 # Temps de jeu
start_time = pygame.time.get_ticks() # Temps courant
pygame.mixer.music.load("boulder_sound.mp3")    # Charger la musique
coin_sound = pygame.mixer.Sound("coin.wav")
brick_sound = pygame.mixer.Sound("brick.wav")
victory_sound = pygame.mixer.Sound("victory.wav")
trap_sound = pygame.mixer.Sound("trap.wav")
death_sound = pygame.mixer.Sound("death.wav")
pygame.mixer.music.play(-1)     # Jouer la musique en boucle


'''Boucle principale du jeu'''
while running:
    if not starter:
        paused_time = 0
        pause_start = pygame.time.get_ticks()
        base_font = pygame.font.Font(None, 32)
        user_text = ''
        input_rect = pygame.Rect(430, 500, 300, 30)
        color_passive = pygame.Color((50, 50, 50))
        color = color_passive
        while not starter:
            for event in pygame.event.get():

                # if user types QUIT then the screen will close
                if event.type == pygame.QUIT:
                    pygame.quit()
                if event.type == pygame.KEYDOWN:

                    # Check for backspace
                    if event.key == pygame.K_BACKSPACE:

                        # get text input from 0 to -1 i.e. end.
                        user_text = user_text[:-1]

                    # Unicode standard is used for string
                    # formation
                    else:
                        user_text += event.unicode
                    if event.key == pygame.K_RETURN:
                        starter = True

                    # it will set background color of screen
                screen.blit(titlescr, (0, 0))
                # draw rectangle and argument passed which should
                # be on screen
                pygame.draw.rect(screen, color, input_rect)

                text_surface = base_font.render(user_text, True, (255, 255, 255))

                # render at position stated in arguments
                screen.blit(text_surface, (input_rect.x + 5, input_rect.y + 5))

                # set width of textfield so that text cannot get
                # outside of user's text input
                input_rect.w = max(100, text_surface.get_width() + 10)

                # display.flip() will update only a portion of the
                # screen to updated, not full area
                pygame.display.flip()
        screen.fill(background_color)
        pause_end = pygame.time.get_ticks()
        paused_time += pause_end - pause_start
        start_time += paused_time
    if game_pause:
        # Boucle de pause
        pygame.mixer.music.pause()
        pause_start = pygame.time.get_ticks()
        paused_time = 0
        while game_pause:
            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False
                    game_pause = False
                    break
                elif event.type == KEYDOWN:
                    if event.key == KEY_SPACE:
                        game_pause = False
                        pause_end = pygame.time.get_ticks()
                        paused_time += pause_end - pause_start
                        break
            start_time += paused_time # Mettre à jour le temps de départ après la pause

            if not game_pause:
                screen.fill(background_color)
                continue

            if play_button.draw(screen):
                pygame.mixer.music.unpause()
                game_pause = False
                screen.fill(background_color)
                pause_end = pygame.time.get_ticks()
                paused_time += pause_end - pause_start
                start_time += paused_time  # Mettre à jour le temps de départ après la pause
                break

            if exit_button.draw(screen):
                running = False
                game_pause = False
                continue

            if replay_button.draw(screen): # Réinitialisation du jeu
                board, grid, bonhomme = import_level("level_test.txt")
                player_x, player_y = bonhomme.x * size_x, bonhomme.y * size_y
                old_player_x, old_player_y = player_x, player_y
                i_old_player_x, i_old_player_y = bonhomme.x, bonhomme.y
                print_grid(grid)
                start_time = pygame.time.get_ticks()
                pygame.mixer.music.rewind()
                pygame.mixer.music.play(-1)
                game_pause = False
                levelnumber = 1
                screen.fill(background_color)
                movement_variables()  # Réinitialisation des variables de mouvement

            pygame.display.update()
    else:
        game_time = (pygame.time.get_ticks() - start_time) // 1000  # Calcul du temps en secondes écoulé depuis le début du jeu
        if game_time >= game_time_limit: # Vérification si le temps imparti est écoulé
            game_defeat=True

        # Apply gravity
        old_grid = copy.deepcopy(grid)
        grid = board.apply_gravity(old_grid)
        try_gravity(old_grid, grid)

        for event in pygame.event.get():
            if event.type == QUIT:
                running = False

            elif event.type == KEYDOWN:
                if event.key == KEY_SPACE:
                    game_pause = True
                elif event.key in moving_coord.keys():
                    move()
                    grid = board.grid

        if game_defeat:  # si le joueur perd
            pygame.mixer.music.pause()
            death_sound.play()
            while running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False  # Quitter la boucle si l'utilisateur ferme la fenêtre
                screen.fill((0, 0, 0))
                screen.blit(defeat_image, (0, 0))
                if defeat_button.draw(screen):
                    running = False
                    game_pause = False
                    continue
                pygame.display.update()
                pygame.display.flip()

        # Mettre à jour la grille
        grid[i_old_player_y][i_old_player_x] = Empty(i_old_player_x, i_old_player_y)
        if grid[bonhomme.y][bonhomme.x].id == 'c':
            coin_sound.play()
        elif grid[bonhomme.y][bonhomme.x].id == 'b':
            brick_sound.play()
        elif grid[bonhomme.y][bonhomme.x].id == 't':
            if levelnumber == 3:
                pygame.mixer.music.pause()
                if bonhomme.coins == 19:
                    victory_sound.play()
                else:
                    death_sound.play()
                while running:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            running = False  # Quitter la boucle si l'utilisateur ferme la fenêtre
                    screen.fill((0, 0, 0))
                    if bonhomme.coins == 19:
                        pseudo = user_text
                        temps = game_time  # Récupérez le temps du joueur depuis votre code existant
                        cursor.execute('INSERT INTO scores (name, time) VALUES (?, ?)', (pseudo, temps))
                        conn.commit()
                        screen.blit(victory_image, (0, 0))
                    else:
                        screen.blit(defeat_image, (0, 0))
                    if defeat_button.draw(screen):
                        running = False
                        game_pause = False
                        continue
                    pygame.display.update()
                    pygame.display.flip()
            goldcoins = bonhomme.coins
            timebtrap = game_time
            trap_sound.play()
            board, grid, bonhomme = level_up(levelnumber,"level_test2.txt","level_test3.txt")
            levelnumber += 1
            player_x, player_y = bonhomme.x * size_x, bonhomme.y * size_y
            old_player_x, old_player_y = player_x, player_y
            i_old_player_x, i_old_player_y = bonhomme.x, bonhomme.y
            print_grid(grid)
            start_time = timebtrap
            bonhomme.coins = goldcoins
            game_pause = False
            screen.fill(background_color)
            movement_variables()  # Réinitialisation des variables de mouvement



        grid[bonhomme.y][bonhomme.x] = Player(bonhomme.x, bonhomme.y)
        board.grid = grid

        # Supprime le joueur de son ancienne position
        player_x, player_y = bonhomme.x * size_x, bonhomme.y * size_y
        erase_rect = pygame.Rect(old_player_x, old_player_y, size_x, size_y)
        screen.fill(background_color, erase_rect)

        # Apply gravity
        old_grid = copy.deepcopy(grid)
        grid = board.apply_gravity(old_grid)
        try_gravity(old_grid, grid)

        print_grid(grid)
        update_score()  # Affichage du score sur l'écran
        update_time()  # Affichage du temps restant
        pygame.display.update()

        old_player_x, old_player_y = player_x, player_y
        i_old_player_x, i_old_player_y = bonhomme.x, bonhomme.y

        pygame.display.flip()  # Rafraîchir l'écran

pygame.quit()  # Quitter Pygame
conn.close()
