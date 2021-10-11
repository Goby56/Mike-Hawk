#CONSTANTS

GRAVITY = 9.82
BASE_FRICTION = 0.31
PLAYER_SPEED = 10
TERMINAL_VELOCITY = 100

colors = {
    "white": (255, 255, 255),
    "black": (0, 0, 0),
    "red": (255, 0, 0),
    "blue": (0, 255, 0),
    "green": (0, 0, 255),
    "blackmagic": (20, 20, 20),
    "whiteknight": (200, 200, 200)
}

import pygame, os, ctypes
SCREENSIZE = ctypes.windll.user32.GetSystemMetrics(0), ctypes.windll.user32.GetSystemMetrics(1)
SCREEN_WIDTH, SCREEN_HEIGHT = SCREENSIZE
print(SCREENSIZE)
res_dir = os.path.join("res")

spritesheet = pygame.image.load(os.path.join(res_dir, "spritesheet.png"))
