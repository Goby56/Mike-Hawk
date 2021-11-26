from typing import List
import pygame, json, ctypes, os

import tkinter as tk
from tkinter import filedialog as fd

from res.tileset import load_set
from res.widgets import MenuButtonPanel
from phases.phase import Phase
from res.config import colors, _base_dir
from listener import Listener


SCREENSIZE = [ctypes.windll.user32.GetSystemMetrics(0), ctypes.windll.user32.GetSystemMetrics(1)]
SCREENSIZE[0] //= 2
SCREENSIZE[1] //= 2

MAX_X, MAX_Y = 1024, 256 # flytta till config
SETDIR = os.path.join(_base_dir, "assets", "tilesets")
pygame.font.init()

def load_level(path):
    with open(path, "r") as file:
        json_dict = json.load(file)
    return json_dict

class Menu(Phase):
    def __init__(self, canvas, listener):
        self.canvas = canvas
        self.listener = listener
        self.btn_panel = MenuButtonPanel(
            self.canvas, listener, (10, 10), 3, 10, 
            ["New Map", "Load Map", "Quit"], 
            [self.new_map, self.load_map, quit]
        )
        tk.Tk().withdraw()

    def update(self):
        self.canvas.fill(colors["white knight"])
        self.btn_panel.update()

    def create_file(self, path, tileset):
        with open(path, "w") as file:
            level = {}
            level["tileset"] = tileset.split(".")[0]
            level["spawn"] = (0, MAX_Y)
            level["map"] = [[(0, 0) for _ in range(MAX_X)] for _ in range(MAX_Y)]
            json.dump(level, file)

    def new_map(self):
        tilepath = fd.askopenfilename(
            initialdir=os.path.join(_base_dir, "assets", "tilesets"),
            defaultextension='.json', 
            filetypes=[("tilesets,", '*.png')]
        )
        if not tilepath: quit()
        tileset = os.path.split(tilepath)[1]
        level = fd.asksaveasfilename(defaultextension='.json', 
            filetypes=[("level files, ", '*.json')], 
            initialdir=os.path.join(_base_dir, "levels"))
        if not level: quit()
        self.create_file(level, tileset)
        Phase.enter_phase(Editor(self.canvas, 
            self.listener, level))

    def load_map(self):
        level = fd.askopenfilename(defaultextension='.json', 
            filetypes=[("level files, ", '*.json')], 
            initialdir=os.path.join(_base_dir, "levels"))
        Phase.enter_phase(Editor(self.canvas, 
            self.listener, level))

class Editor(Phase):
    def __init__(self, canvas, listener, path):
        self.canvas = canvas
        self.listener = listener
        self.path = path
        with open(self.path, "r") as file:
            self.level = json.load(file)
        
        # tile things
        tileset = load_set(SETDIR, self.level["tileset"])
        self.tileset = [list(tileset["fg"]), list(tileset["bg"])]

        self.tile = 50
        self.tiles = []

        self.load_data()
        self.new_tile(1, 255, 0, 0)
        self.new_tile(1, 254, 1, 0)
        self.new_tile(2, 253, 1, 0)

        #movement
        self.x_offset = 0
        self.y_offset = 0

        # inputs
        self.func_keys = {"space": False}

    def update(self):
        self.canvas.fill(colors["white knight"])
        for key in self.func_keys.keys():
            self.func_keys[key] = self.listener.key_pressed(key, hold=True)
        self.draw_lines()
        self.get_movement()
        self.get_mouse()
        for tile in self.tiles:
            tile.update(self.tile, self.x_offset, self.y_offset)

        pygame.mouse.get_rel()

    def load_data(self):
        for y, row in enumerate(self.level["map"]):
            for x, node in enumerate(row):
                if node[0]: self.new_tile(x, y, node[0]-1, node[1])

    def new_tile(self, x, y, index, layer):
        image = self.tileset[layer][index]
        self.tiles.append(Tile(self.canvas, (x, y), image))
        self.level["map"][y][x] = [index, layer]

    def get_movement(self):
        if self.listener.mouse_clicked(4): self.tile -= 1
        if self.listener.mouse_clicked(5): self.tile += 1

        if self.func_keys["space"] and self.listener.mouse_clicked(1, hold=True):
            rel = pygame.mouse.get_rel()
            self.x_offset += rel[0] if self.x_offset + rel[0] < 0 else 0
            self.y_offset += rel[1] if self.y_offset + rel[1] > 0 else 0

    def get_mouse(self):
        mouse = pygame.mouse.get_pos()
        if self.listener.mouse_clicked(1) and not any(self.func_keys.values()):
            x_pos, y_pos = mouse[0]-self.x_offset, SCREENSIZE[1] - mouse[1]+self.y_offset
            x, y = x_pos//self.tile, MAX_Y - y_pos//self.tile - 1
            print(x, y_pos//self.tile, y)
            self.new_tile(x, y, 1, 1)

    def draw_lines(self):
        for x in range(int(SCREENSIZE[0]//self.tile) + 1):
            pygame.draw.line(self.canvas, colors["black magic"], 
                (x*self.tile + self.x_offset % self.tile, 0), 
                (x*self.tile + self.x_offset % self.tile, SCREENSIZE[1]))
        for y in range(int(SCREENSIZE[1]//self.tile) + 1):
            pygame.draw.line(self.canvas, colors["black magic"], 
                (0, SCREENSIZE[1] - y*self.tile + self.y_offset % self.tile), (SCREENSIZE[0], 
                SCREENSIZE[1] - y*self.tile + self.y_offset % self.tile))

        # + movement % self.tile

    # add toolbar and tile selector

class App:
    def __init__(self):
        self._display = pygame.display.set_mode(SCREENSIZE)
        self._clock = pygame.time.Clock()

        self.canvas = pygame.Surface(SCREENSIZE)
        self.listerner = Listener()
        Phase.enter_phase(Menu(self.canvas, self.listerner))

    def main(self):
        self.canvas.fill(colors["white knight"])
        self.listerner.listen()

        self.listerner.on_event("quit", quit)

        phase = Phase.get_current()
        phase.update()
        phase.render()

        self._display.blit(self.canvas, (0, 0))
        pygame.display.update()
        self._clock.tick(60)


class Tile:
    def __init__(self, canvas, pos, image):
        self.canvas = canvas
        self.x, self.y = pos
        self.image = image

    def update(self, dim, x_offset, y_offset):
        dim = int(dim)
        surf = pygame.transform.scale(self.image, (dim,dim))
        self.canvas.blit(surf, (self.x*dim+x_offset, SCREENSIZE[1]-(MAX_Y-self.y)*dim+y_offset))


if __name__ == "__main__":
    app = App()
    while True:
        app.main()
