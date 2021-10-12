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

_base_dir = os.path.abspath(os.path.dirname(__file__))
_menu_dir = os.path.join(_base_dir, "assets", "Menu", "MenuButton.png")
menubutton = pygame.image.load(_menu_dir)


class Spritesheet:
    def __init__(self, filename):
        self.filename = filename
        self.sheet = pygame.image.load(filename).convert()

    def get_sprite():
        pass

assets_dir = os.path.join("assets")

#spritesheet = pygame.image.load(os.path.join(assets_dir, "spritesheet.png"))
