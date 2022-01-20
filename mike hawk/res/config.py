#CONSTANTS

GRAVITY = 9.82
BASE_FRICTION = 0.31
PLAYER_SPEED = 10
TERMINAL_VELOCITY = 100
MAX_Y = 256

import ctypes, pygame, os
SCREENSIZE = ctypes.windll.user32.GetSystemMetrics(0), ctypes.windll.user32.GetSystemMetrics(1)
SCREENSIZE = (1280, 720) #Test school laptop screensize
SCREEN_WIDTH, SCREEN_HEIGHT = SCREENSIZE
NOMINAL_WIDTH, NOMINAL_HEIGHT = [1920, 1080]
screen_scale_x = SCREEN_WIDTH / NOMINAL_WIDTH
screen_scale_y = SCREEN_HEIGHT / NOMINAL_HEIGHT

print(SCREENSIZE)
fps = 60
debug = True

colors = {
    "white": (255, 255, 255),
    "black": (0, 0, 0),
    "red": (255, 0, 0),
    "blue": (0, 0, 255),
    "green": (0, 255, 0),
    "black magic": (20, 20, 20),
    "white knight": (200, 200, 200),
    "cool blue": (40, 128, 235),
    "hot pink": (255,105,180)
}

game_vars = {
    "gravity": 2/3*screen_scale_x,
    "player_jump_strength": 32/3*screen_scale_x,
    "gorilla_jump_strength": 64/3*screen_scale_x,
    "speed": 20/3*screen_scale_x,
    "ground_friction": -0.2*screen_scale_x,
    "air_resistance": -0.075*screen_scale_x,
    "max_vel": 3*screen_scale_x,
    "tile_size": int(54*screen_scale_x),
    "fall_ranges":[4,10,20], # dy<4:nothing, 4<dy<10:rolling, 10<dy<20:unconscious, dy>20:dead
    "player_fire_angle":40 # Degrees
}   

bounding_boxes = {
    "player": {
        "hitbox":pygame.math.Vector2(18,22),
        "drawbox":pygame.math.Vector2(64,32),
        "height":2
    },
    "gorilla": {
        "hitbox":pygame.math.Vector2(36,44),
        "drawbox":pygame.math.Vector2(64,64),
        "height":3,
        "aggrobox":pygame.math.Vector2(24,5) # Tiles
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
paralax_layers = load_frames("moody_jungle")
player_animations = load_frames("demo_hawk", "walking")
editor_buttons = load_frames("editor_buttons")
spawn_image = pygame.image.load(
        os.path.join(_base_dir, "assets", "editor", "spawn_point.png")
)

gui = pygame.Surface((200, 600)) # temp make image
gui.fill(colors["black magic"])
gui_selection = pygame.Surface((200, 200))
gui_selection.fill(colors["white knight"])


