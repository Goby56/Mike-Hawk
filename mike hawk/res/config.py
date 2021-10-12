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
    "black magic": (20, 20, 20),
    "white knight": (200, 200, 200)
}

import ctypes
SCREENSIZE = ctypes.windll.user32.GetSystemMetrics(0), ctypes.windll.user32.GetSystemMetrics(1)
SCREENSIZE = (800, 700)

SCREEN_WIDTH, SCREEN_HEIGHT = SCREENSIZE

# LOAD RESOURCES
import pygame, os

SCREEN_RECT = pygame.Rect((0, 0), SCREENSIZE)
PYGAME_CAPS_KEYS = {
    "space": pygame.K_SPACE
}

assets_dir = os.path.join("assets")

#spritesheet = pygame.image.load(os.path.join(assets_dir, "spritesheet.png"))