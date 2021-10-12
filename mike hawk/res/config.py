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
    "space": pygame.K_SPACE,
    "escape": pygame.K_ESCAPE
}

_base_dir = os.path.abspath(os.path.dirname(__file__))
sprite_dir = os.path.join(_base_dir, "assets", "spritesheets")
_menu_dir = os.path.join(_base_dir, "assets", "menu", "MenuButton.png")
menubutton = pygame.image.load(_menu_dir)

# Loading sprites
from .spritesheet import Spritesheet
spritesheet = Spritesheet("8x8") # Create object of file path
data = spritesheet.parse_sprite() # Get meta data from sheet
frames = spritesheet.get_frames(data) # Get sequence of frames