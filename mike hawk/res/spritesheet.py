from types import new_class
import pygame, os, json
from .config import sprite_dir

class Spritesheet:
    """
    Do not include {.PNG} or {.JSON}, just filename

    Example:\n
    spritesheet = Spritesheet("8x8") # Create object of file path\n
    data = spritesheet.parse_sprite() # Get meta data from sheet\n 
    frames = spritesheet.get_frames(data) # Get sequence of frames\n 
    """
    def __init__(self, filename):
        self.filename = filename
        self.file_path = os.path.join(sprite_dir, filename)
        self.sprite_sheet = pygame.image.load(self.file_path + ".png")#.convert()
        self.meta_data = os.path.join(sprite_dir, self.filename + ".json")
        with open(self.meta_data) as f:
            self.data = json.load(f)
        self.reorder_frames()

    def reorder_frames(self):
        new_sheet = dict()
        for name in self.data["frames"].keys():
            tag = str()
            frame = int()

            #tag = name.replaceAll("[0-9]","")
            for char in name:
                if char.isalpha():
                    tag = tag + char
                elif char.isdigit():
                    frame = frame + int(char)

            new_sheet[tag][frame] = self.data["frames"][name]

        self.data = new_sheet

    def parse_sprite(self):
        sprite_data = dict()
        for tag in self.data.keys():
            for i in range(len(self.data[tag])):
                sd = self.data[tag][i]["frame"] # Sprite data
                x, y, w, h = sd["x"], sd["y"], sd["w"], sd["h"]
                sprite_data[tag][i] = (x,y,w,h)
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
