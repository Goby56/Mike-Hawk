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
_sprite_dir = os.path.join(_base_dir, "assets", "spritesheets")
_menu_dir = os.path.join(_base_dir, "assets", "Menu", "MenuButton.png")
menubutton = pygame.image.load(_menu_dir)

# Initialit
import json

class Spritesheet:
    def __init__(self, filename):
        """Do not include {.PNG} or {.JSON}, just filename"""
        self.filename = filename
        self.file_path = os.path.join(_sprite_dir, filename)
        self.sprite_sheet = pygame.image.load(self.file_path + ".png")#.convert()
        self.meta_data = os.path.join(_sprite_dir, self.filename + ".json")
        with open(self.meta_data) as f:
            self.data = json.load(f)

    def parse_sprite(self):
        sprite_data = dict()
        for name in self.data["frames"].keys():
            sd = self.data["frames"][name]["frame"] # Sprite data
            x, y, w, h = sd["x"], sd["y"], sd["w"], sd["h"]
            sprite_data[name] = (x,y,w,h)
        return sprite_data

    def get_sprite(self, data, color_key = (0,0,0)):
        x,y,w,h = data
        sprite = pygame.Surface((w,h))
        sprite.set_colorkey(color_key)
        sprite.blit(self.sprite_sheet, (0,0), (data))
        return sprite

    def get_frames(self, data_list, color_key = (0,0,0)):
        if type(data_list) == dict:
            data_list = data_list.values() 
        frame_list = []
        for data in data_list:
            sprite = self.get_sprite(data, color_key)
            frame_list.append(sprite)
        return frame_list

spritesheet = Spritesheet("8x8")
data = spritesheet.parse_sprite()
frames = spritesheet.get_frames(data)
print(frames)


print(data)


assets_dir = os.path.join("assets")

#spritesheet = pygame.image.load(os.path.join(assets_dir, "spritesheet.png"))
