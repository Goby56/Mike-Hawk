#CONSTANTS

GRAVITY = 9.82
BASE_FRICTION = 0.31
PLAYER_SPEED = 10
TERMINAL_VELOCITY = 100

import pygame, os
res_dir = os.path.join("res")

spritesheet = pygame.image.load(os.path.join(res_dir, "spritesheet.png"))
