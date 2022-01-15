import pygame, os, sys, json, glob, pprint
sys.path.append("..")
from pathlib import Path
from .config import spritesheet_dir, _base_dir


class Spritesheet:
    """
    USE:
    Import spritesheet in aseprite, select grid dimensions and add tags to sequences of frames.
    If the sheet has less than two tags or rows set the tag to filename.
    While exporting include "Split Tags" and have the png and json file have the same name.
    For the "Item Filename" the expected key format is:{tag} {frame}

    While loading a spritesheet do not include {.PNG} or {.JSON}, just filename.

    Example:\n
    spritesheet = Spritesheet("dynamite") Creates an object from the file path\n
    data = spritesheet.parse_sprite() Gets the meta data from the sheet (Coordinates and dimension)\n
    frames = spritesheet.get_frames(data) Gets the sequence of frames\n 
    """

    instances = {}

    def get_instance(self, filename):
        return self.instances[filename]

    def __init__(self, filename):
        self.filename = filename
        self.file_path = self.find_file(self.filename)
        self.sprite_sheet = pygame.image.load(self.file_path + ".png")#.convert()
        self.meta_data = os.path.join(self.file_path + ".json")
        with open(self.meta_data) as f:
            self.data = json.load(f)
        self.refactor_dictionary()
        self.parse_dimensions()
        self.create_frames_dictionary()
        with open(os.path.join(_base_dir, "animation_delays.json"), "r") as f:
            data = json.load(f)
            if self.filename not in data.keys():
                self.add_animation_information()
        self.instances[self.filename] = self


    def find_file(self, filename):
        """
        Recursively searches for the given {filename} in the sprite sheet directory and returns the path
        """
        for path in Path(spritesheet_dir).rglob("**/*"):
            if path.is_file():
                if filename == path.name.split(".")[0]:
                    return str(path.absolute()).split(".")[0]

    def refactor_dictionary(self):
        """
        Refactors the basic asperite json file to a more readable configuration
        """
        new_sheet = dict()
        for item in self.data["frames"].keys():
            tag = str()
            frame = str()

            tag, frame = item.split(" ")[0], item.split(" ")[1]

            if tag not in new_sheet.keys():
                new_sheet[tag] = dict()

            new_sheet[tag][frame] = self.data["frames"][item]["frame"]

        self.data = new_sheet

    def parse_dimensions(self):
        """
        Extracts the useful bits about the sprite sheet. (i.e the position and size of each sprite) 
        """
        for tag in self.data.keys():
            for frame in range(len(self.data[tag].keys())):
                dim = self.data[tag][str(frame)]
                x, y, w, h = dim["x"], dim["y"], dim["w"], dim["h"]
                self.data[tag][str(frame)] = (int(x),int(y),int(w),int(h))
            
    def create_frames_dictionary(self):
        """
        Creates the dictionary for holding each frame categorized by the tag of the frame
        """
        self.frames = dict()
        for tag in self.data.keys():
            for frame in range(len(self.data[tag])):
                if tag not in self.frames.keys():
                    self.frames[tag] = list()
                data = self.data[tag][str(frame)]
                self.frames[tag].append(self.get_sprite(data))

    def add_animation_information(self):
        tags = self.data.keys()
        new_data = {tag: [1 for x in range(len(self.data[tag]))] for tag in tags}
        pprint.pprint(new_data)

        with open(os.path.join(_base_dir, "animation_delays.json"), "r+") as f:
            data = json.load(f)
            data[self.filename] = new_data
            f.seek(0)
            json.dump(data, f, indent=4)
            #f.truncate()

    def get_sprite(self, data, color_key = (0,0,0)):
        """
        Grabs the sprite located at {data} in this sprite sheet
        """
        x,y,w,h = data
        sprite = pygame.Surface((w,h))
        sprite.set_colorkey(color_key)
        sprite.blit(self.sprite_sheet, (0,0), (data))
        return sprite

    def get_frames(self, tag):
        """
        Get the sequence of frames categorized by {tag}
        """
        return self.frames[tag]
