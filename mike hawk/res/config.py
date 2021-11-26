#CONSTANTS

GRAVITY = 9.82
BASE_FRICTION = 0.31
PLAYER_SPEED = 10
TERMINAL_VELOCITY = 100

import ctypes
SCREENSIZE = ctypes.windll.user32.GetSystemMetrics(0), ctypes.windll.user32.GetSystemMetrics(1)
SCREEN_WIDTH, SCREEN_HEIGHT = SCREENSIZE
print(SCREENSIZE)
_screen_offset = SCREEN_WIDTH / 1280


colors = {
    "white": (255, 255, 255),
    "black": (0, 0, 0),
    "red": (255, 0, 0),
    "blue": (0, 255, 0),
    "green": (0, 0, 255),
    "black magic": (20, 20, 20),
    "white knight": (200, 200, 200)
}

game_vars = {
    "gravity": 0.5*_screen_offset,
    "jump strength": 13*_screen_offset,
    "speed": 1.5*_screen_offset,
    "friction": -0.2,
    "max_vel": 6*_screen_offset,
    "tile_size": int(40*_screen_offset)
}



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

def load_frames(filename):
    spritesheet = Spritesheet(filename) # Create object of file path
    data = spritesheet.parse_sprite() # Get meta data from sheet
    frames = spritesheet.get_frames(data) # Get sequence of frames
    return frames

dynamite_frames = load_frames("dynamite")
tile_frames = load_frames("dev_tiles")
tile_frames_bg = load_frames("dev_tiles_bg")
paralax_layers = load_frames("desertdemo")
player_animations = load_frames("player_walk")
