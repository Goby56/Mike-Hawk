import pygame, json, ctypes, os

import tkinter as tk
from tkinter import filedialog as fd
from tkinter import messagebox as mb

from res.tileset import load_set
from res.widgets import MenuButtonPanel, Toolbar
from phases.phase import Phase
from res.config import colors, _base_dir, paralax_layers
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
            level["details"] = []
            level["entities"] = []
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

        self.layer = 0

        #movement
        self.x_offset = 0
        self.y_offset = 0

        # inputs
        self.modes = ["place", "delete", "select", "entity", "spawn"]
        self.mode = "place"

        tmp = pygame.Surface((20, 20))
        tmp.fill(colors["red"])
        self.toolbar = Toolbar(self.canvas, self.listener, (70, 0), 
            [tmp, tmp, tmp, tmp, tmp], 5)
        self.toolbar.bind(("b", 0), ("e", 1), ("m", 2))
        
        self.layer_panel = Toolbar(self.canvas, self.listener, (self.toolbar.pos[0] + self.toolbar.dim[0] + 10, 0), 
            [tmp, tmp], 5)
        self.layer_panel.bind(("1", 0), ("2", 1))

        self.func_keys = {"space": False, "left control": False}
        
        #backgtound
        self.paralax_layers = [pygame.transform.scale(layer, SCREENSIZE) for layer in paralax_layers]

    @property
    def mouse(self):
        mouse = pygame.mouse.get_pos()
        x_pos, y_pos = mouse[0]-self.x_offset, SCREENSIZE[1] - mouse[1]+self.y_offset
        return x_pos//self.tile, MAX_Y - y_pos//self.tile - 1

    def update(self):
        for layer in self.paralax_layers:
            self.canvas.blit(layer, (0, 0))
        self.mode = self.modes[self.toolbar.get_selected()]
        self.layer = self.layer_panel.get_selected()

        if any(self.func_keys.values()) or self.toolbar.hover() or self.layer_panel.hover(): 
            self.mode = "other"

        for key in self.func_keys.keys():
            self.func_keys[key] = self.listener.key_pressed(key, hold=True)
        self.listener.on_key("escape", self.exit)
        self.listener.on_event("quit", self.exit)
        
        self.get_movement()
        
        if self.listener.mouse_clicked(1, hold=True) and self.mode in self.modes:
                exec("self.{}()".format(self.mode))

        for tile in self.tiles:
            tile.update(self.tile, self.x_offset, self.y_offset)
        if self.func_keys["left control"] and self.listener.key_pressed("s"):
            self.save()

        self.draw_lines()
        self.toolbar.update()
        self.layer_panel.update()
        pygame.mouse.get_rel()

    def load_data(self):
        for y, row in enumerate(self.level["map"]):
            for x, node in enumerate(row):
                if node[0]: self.new_tile(x, y, node[0]-1, node[1])

    def new_tile(self, x, y, index, layer):
        image = self.tileset[layer][index]
        self.tiles.append(Tile(self.canvas, (x, y), layer, image))
        self.level["map"][y][x] = [index+1, layer]

    def get_movement(self):
        if self.listener.mouse_clicked(4): self.tile -= 1
        if self.listener.mouse_clicked(5): self.tile += 1

        if self.func_keys["space"] and self.listener.mouse_clicked(1, hold=True):
            rel = pygame.mouse.get_rel()
            self.x_offset += rel[0] if self.x_offset + rel[0] < 0 else 0
            self.y_offset += rel[1] if self.y_offset + rel[1] > 0 else 0

    def place(self):
        x, y = self.mouse
        tile = self.get_tile(x, y)
        if tile and tile.layer != self.layer:
            return
        self.new_tile(x, y, 0, self.layer)

    def delete(self):
        tile = self.get_tile(*self.mouse)
        if tile and tile.layer == self.layer:
            self.tiles.remove(tile)
            self.level["map"][tile.y][tile.x] = [0, 0]

    def spawn(self):
        x, y = self.mouse
        print("spawn set at:", x, y)
        self.level["spawn"] = [x, y]

    def get_tile(self, x, y):
        for tile in self.tiles:
            if (tile.x, tile.y) == (x, y):
                return tile
        return False

    def draw_lines(self):
        for x in range(int(SCREENSIZE[0]//self.tile) + 1):
            pygame.draw.line(self.canvas, colors["black magic"], 
                (x*self.tile + self.x_offset % self.tile, 0), 
                (x*self.tile + self.x_offset % self.tile, SCREENSIZE[1]))
        for y in range(int(SCREENSIZE[1]//self.tile) + 1):
            pygame.draw.line(self.canvas, colors["black magic"], 
                (0, SCREENSIZE[1] - y*self.tile + self.y_offset % self.tile), (SCREENSIZE[0], 
                SCREENSIZE[1] - y*self.tile + self.y_offset % self.tile))

    def save(self):
        print("Saving...")
        with open(self.path, "w") as file:
            json.dump(self.level, file)

    def exit(self):
        if mb.askyesno("Save?", "Do you want to save?"):
            self.save()
        quit()

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

        phase = Phase.get_current()
        phase.update()
        phase.render()

        self.listerner.on_event("quit", quit)

        self._display.blit(self.canvas, (0, 0))
        pygame.display.update()
        self._clock.tick(60)


class Tile:
    def __init__(self, canvas, pos, layer, image):
        self.canvas = canvas
        self.x, self.y = pos
        self.image = image
        self.layer = layer

    def update(self, dim, x_offset, y_offset):
        dim = int(dim)
        surf = pygame.transform.scale(self.image, (dim,dim))
        self.canvas.blit(surf, (self.x*dim+x_offset, SCREENSIZE[1]-(MAX_Y-self.y)*dim+y_offset))


if __name__ == "__main__":
    app = App()
    while True:
        app.main()
