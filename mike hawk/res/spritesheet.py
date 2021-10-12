import pygame, os, json
from config import sprite_dir

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