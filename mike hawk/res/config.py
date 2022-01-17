#CONSTANTS

GRAVITY = 9.82
BASE_FRICTION = 0.31
PLAYER_SPEED = 10
TERMINAL_VELOCITY = 100
MAX_Y = 256

import ctypes, pygame, os
SCREENSIZE = ctypes.windll.user32.GetSystemMetrics(0), ctypes.windll.user32.GetSystemMetrics(1)
SCREEN_WIDTH, SCREEN_HEIGHT = SCREENSIZE
#SCREENSIZE = 400, 200
print(SCREENSIZE)
fps = 60
debug = True
_screen_offset = SCREEN_WIDTH / 1280


colors = {
    "white": (255, 255, 255),
    "black": (0, 0, 0),
    "red": (255, 0, 0),
    "blue": (0, 0, 255),
    "green": (0, 255, 0),
    "black magic": (20, 20, 20),
    "white knight": (200, 200, 200),
    "cool blue": (40, 128, 235)
}

game_vars = {
    "gravity": 0.5*_screen_offset,
    "jump strength": 8*_screen_offset,
    "speed": 5*_screen_offset,
    "ground_friction": -0.2,
    "air_resistance": -0.075,
    "max_vel": 3*_screen_offset,
    "tile_size": int(40*_screen_offset),
    "sprint_multiplier": 1.5,
    "jump_amplifier": 1.5,
    "crouch_slowdown": 0.5,
    "player_height": 2,
    "fall_ranges":[4,10,20], # dy<4:nothing, 4<dy<10:rolling, 10<dy<20:unconscious, dy>20:dead
    "player_fire_angle":40 # Degrees
}   

bounding_boxes = {
    "player": {
        "hitbox":pygame.math.Vector2(18,22),
        "drawbox":pygame.math.Vector2(64,32)
    }

}

# LOAD RESOURCES

SCREEN_RECT = pygame.Rect((0, 0), SCREENSIZE)
PYGAME_CAPS_KEYS = {
    "space": pygame.K_SPACE,
    "escape": pygame.K_ESCAPE,
    "left shift": pygame.K_LSHIFT,
    "left control": pygame.K_LCTRL,
    "left alt": pygame.K_LALT
}

_base_dir = os.path.abspath(os.path.dirname(__file__))
spritesheet_dir = os.path.join(_base_dir, "assets", "spritesheets")
_menu_dir = os.path.join(_base_dir, "assets", "menu", "MenuButton.png")
menubutton = pygame.image.load(_menu_dir)

# Loading sprites
from .spritesheet import Spritesheet

def load_frames(filename, tag=None):
    if tag == None:
        tag = filename
    spritesheet = Spritesheet(filename)
    return spritesheet.get_frames(tag)

dynamite_frames = load_frames("dynamite")
paralax_layers = load_frames("desertdemo")
player_animations = load_frames("demo_hawk", "walking")
editor_buttons = load_frames("editor_buttons")
spawn_image = pygame.image.load(
        os.path.join(_base_dir, "assets", "editor", "spawn_point.png")
)
